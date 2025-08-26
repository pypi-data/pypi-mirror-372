import importlib.metadata
import logging
import os
import pathlib
import shutil
import subprocess

import charm_refresh_build_version
import requests
import rich
import rich.text
import tomli
import typer
import typing_extensions

app = typer.Typer(help="Pack charms with local Python package dependencies")
Verbose = typing_extensions.Annotated[bool, typer.Option("--verbose", "-v")]
running_in_ci = os.environ.get("CI") == "true"
if running_in_ci:
    # Show colors in CI (https://rich.readthedocs.io/en/stable/console.html#terminal-detection)
    console = rich.console.Console(highlight=False, color_system="truecolor")
else:
    console = rich.console.Console(highlight=False)
logger = logging.getLogger(__name__)


class RichHandler(logging.Handler):
    """Use rich to print logs"""

    def emit(self, record):
        try:
            message = self.format(record)
            if getattr(record, "disable_wrap", False):
                console.print(message, overflow="ignore", crop=False)
            else:
                console.print(message)
        except Exception:
            self.handleError(record)


handler = RichHandler()


class WarningFormatter(logging.Formatter):
    """Only show log level if level >= logging.WARNING or verbose enabled"""

    def format(self, record):
        if record.levelno >= logging.WARNING or state.verbose:
            level = rich.text.Text(record.levelname, f"logging.level.{record.levelname.lower()}")
            replacement = f"{level.markup} "
        else:
            replacement = ""
        old_format = self._style._fmt
        self._style._fmt = old_format.replace("{levelname} ", replacement)
        result = super().format(record)
        self._style._fmt = old_format
        return result


class State:
    def __init__(self):
        self._verbose = None
        self.verbose = False

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value: bool):
        if value == self._verbose:
            return
        self._verbose = value
        log_format = "\[charmcraftlocal] {levelname} {message}"
        if value:
            log_format = "{asctime} " + log_format
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        logger.removeHandler(handler)
        handler.setFormatter(WarningFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S", style="{"))
        logger.addHandler(handler)
        logger.debug(f"Version: {installed_version}")


class InvalidLocalPackageDependency(Exception):
    """Dependency is not a local Python package specified by a relative path to a directory"""


class LocalPackageDependency:
    def __init__(self, *, key: str, value):
        if isinstance(value, list):
            logger.warning(
                f"Skipped dependency {repr(key)}. Multiple constraints dependencies (i.e. "
                "dependency values with type list) are not currently supported"
            )
        if not isinstance(value, dict):
            raise InvalidLocalPackageDependency
        try:
            path = value.pop("path")
        except KeyError:
            raise InvalidLocalPackageDependency
        path = pathlib.Path(path)
        if path.is_absolute():
            logger.debug(f"Skipped dependency {repr(key)}. Path is not relative: {repr(path)}")
            raise InvalidLocalPackageDependency
        if path.is_symlink():
            logger.debug(
                f"Skipped dependency {repr(key)}. Symlink paths are not supported: {repr(path)}"
            )
            raise InvalidLocalPackageDependency
        if not path.exists():
            logger.debug(f"Skipped dependency {repr(key)}. Path does not exist: {repr(path)}")
            raise InvalidLocalPackageDependency
        if not path.is_dir():
            logger.debug(f"Skipped dependency {repr(key)}. Path is not a directory: {repr(path)}")
            raise InvalidLocalPackageDependency
        try:
            git_repository_root = pathlib.Path(
                subprocess.run(
                    ["git", "rev-parse", "--show-toplevel"],
                    capture_output=True,
                    check=True,
                    text=True,
                ).stdout.strip()
            )
        except FileNotFoundError:
            raise FileNotFoundError("git not installed")
        assert git_repository_root.is_absolute()
        if not path.resolve(strict=True).is_relative_to(git_repository_root):
            logger.debug(
                f"Skipped dependency {repr(key)}. Path must be in the same git repository "
                f"({repr(git_repository_root)}) as the current working directory. Dependency "
                f"path: {repr(path)}"
            )
            raise InvalidLocalPackageDependency
        if path.resolve(strict=True).is_relative_to(pathlib.Path.cwd()):
            logger.debug(
                f"Skipped dependency {repr(key)}. Path is already in charm directory. Dependency "
                f"path: {repr(path)}"
            )
            raise InvalidLocalPackageDependency
        self.name = key
        self.original_path = path
        self.copy_for_packing_path = pathlib.Path() / path.name
        # Ignore "develop" (editable installs) since charmcraft + Juju relocates the virtual
        # environment to a different filesystem.
        # Editable installs in a virtual environment use absolute paths, so it is not possible to
        # relocate a virtual environment & the absolute location of the editable install source
        # while preserving an editable install—without editing the path in the .pth file for the
        # editable install dependency.
        # Details:
        # - https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
        # - https://setuptools.pypa.io/en/latest/userguide/development_mode.html
        # This limitation applies to both pip and uv virtual environments (including uv virtual
        # environments created with --relocatable) as of pip 25.2 and uv 0.8.11
        value.pop("develop", None)

        if value != {}:
            raise NotImplementedError(
                f"Dependency {repr(key)} has unrecognized dependency specification options: "
                f"{repr(value)}"
            )


def run_command(command: list[str]):
    logger.debug(f"Running {command}")
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError:
        command_name = command[0]
        message = f"{command_name} not installed"
        if command_name in ("poetry", "charmcraftcache"):
            message += f". Run `pipx install {command_name}`"
        raise FileNotFoundError(message)
    except subprocess.CalledProcessError as exception:
        # stderr will be shown in terminal, no need to raise exception—just log traceback.
        logger.exception(f"{command[0]} command failed:")
        exit(exception.returncode)


def validate_command_name(command_name: str):
    if command_name in ("charmcraftlocal", "ccl"):
        raise typer.BadParameter("charmcraftlocal cannot call itself")
    return command_name


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def pack(
    context: typer.Context,
    verbose: Verbose = False,
    command_name: typing_extensions.Annotated[
        str, typer.Option(callback=validate_command_name, help="Program to pack charm with")
    ] = "charmcraftcache",
):
    """Move local Python package dependencies to charm directory & `charmcraftcache pack`

    Unrecognized command arguments are passed to `charmcraftcache pack`
    """
    if verbose:
        # Verbose can be globally enabled from command level or app level
        # (Therefore, we should only enable verbose—not disable it)
        state.verbose = True
    if context.args:
        logger.info(
            f"Passing unrecognized arguments to `{command_name} pack`: {' '.join(context.args)}"
        )
    if not pathlib.Path("charmcraft.yaml").exists():
        raise FileNotFoundError(
            "charmcraft.yaml not found. `cd` into the directory with charmcraft.yaml"
        )
    pyproject_toml = pathlib.Path("pyproject.toml")
    pyproject_toml_backup = pathlib.Path("pyproject.toml.backup")
    poetry_lock = pathlib.Path("poetry.lock")
    poetry_lock_backup = pathlib.Path("poetry.lock.backup")
    refresh_versions_toml = pathlib.Path("refresh_versions.toml")
    refresh_versions_toml_backup = pathlib.Path("refresh_versions.toml.backup")
    try:
        with pyproject_toml.open("rb") as file:
            pyproject = tomli.load(file)
    except FileNotFoundError:
        logger.debug("pyproject.toml not found")
        pyproject = {}
    local_packages: list[LocalPackageDependency] = []
    # Relative paths are not supported in project.dependencies, so we only need to check
    # tool.poetry.dependencies
    for key, value in pyproject.get("tool", {}).get("poetry", {}).get("dependencies", {}).items():
        try:
            local_packages.append(LocalPackageDependency(key=key, value=value))
        except InvalidLocalPackageDependency:
            pass
    if not local_packages:
        # Info instead of warning since it's expected that charmcraftlocal will be used to pack
        # charms without any local Python package dependencies
        logger.info("No local Python package dependencies detected")
    if local_packages:
        assert pyproject_toml.exists()
        if not poetry_lock.exists():
            raise FileNotFoundError("poetry.lock not found")
    for package in local_packages:
        if package.copy_for_packing_path.exists():
            raise FileExistsError(
                f"Destination path in charm directory already exists. Delete path and retry: "
                f"{repr(package.copy_for_packing_path)}"
            )
    try:
        if local_packages:
            if refresh_versions_toml.exists():
                # .git directory not available during `charmcraft pack` because this charm is not
                # at the root of the git repository. Therefore, we need to set charm refresh
                # compatibility version (which inspects git tags & status) before `charmcraft pack`
                logger.debug("Writing charm refresh compatibility version to refresh_versions.toml")
                charm_version = charm_refresh_build_version.determine_charm_version_before_pack()
                shutil.copy2(refresh_versions_toml, refresh_versions_toml_backup)
                charm_refresh_build_version.write_charm_version_before_pack(charm_version)
                logger.debug("Wrote charm refresh compatibility version to refresh_versions.toml")
            shutil.copy2(pyproject_toml, pyproject_toml_backup)
            shutil.copy2(poetry_lock, poetry_lock_backup)
        for package in local_packages:
            shutil.copytree(package.original_path, package.copy_for_packing_path, symlinks=True)
            logger.info(
                f"Copied {repr(package.original_path)} to {repr(package.copy_for_packing_path)}"
            )
            run_command(["poetry", "remove", package.name, "--lock"])
            run_command(["poetry", "add", f"./{package.copy_for_packing_path}", "--lock"])
        command = [command_name, "pack", *context.args]
        if state.verbose:
            command.append("-v")
        run_command(command)
    finally:
        if local_packages:
            for backup, original in (
                (refresh_versions_toml_backup, refresh_versions_toml),
                (pyproject_toml_backup, pyproject_toml),
                (poetry_lock_backup, poetry_lock),
            ):
                try:
                    shutil.move(backup, original)
                except FileNotFoundError:
                    pass
        for package in local_packages:
            try:
                shutil.rmtree(package.copy_for_packing_path)
            except FileNotFoundError:
                pass


@app.callback()
def main(verbose: Verbose = False):
    if verbose:
        # Verbose can be globally enabled from app level or command level
        # (Therefore, we should only enable verbose—not disable it)
        state.verbose = True


installed_version = importlib.metadata.version("charmcraftlocal")
state = State()
response_ = requests.get("https://pypi.org/pypi/charmcraftlocal/json")
response_.raise_for_status()
latest_pypi_version = response_.json()["info"]["version"]
if installed_version != latest_pypi_version:
    logger.info(
        f"Update available. Run `pipx upgrade charmcraftlocal` ({installed_version} -> "
        f"{latest_pypi_version})"
    )
