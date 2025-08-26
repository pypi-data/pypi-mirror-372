# charmcraftlocal
Pack charms with local Python package dependencies

## Installation
Install `pipx`: https://pipx.pypa.io/stable/installation/
```
pipx install charmcraftlocal
```

## Usage
At the moment, only charms that manage Python dependencies with Poetry are supported.

### Example directory layout
```
common/
    # Local Python package with shared code
    pyproject.toml
    common/
        __init__.py
kubernetes/
    charmcraft.yaml
    pyproject.toml
    poetry.lock
    # [...]
machines/
    charmcraft.yaml
    pyproject.toml
    poetry.lock
    # [...]
```

<details>
<summary>Example common/pyproject.toml</summary>

```toml
[project]
name = "common"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```
</details>


### Step 1: Add local package to charm dependencies

Repeat this step for each charm that depends on the local package.

```
poetry add ../common --editable
```

Example pyproject.toml
```toml
[tool.poetry.dependencies]
common = {path = "../common", develop = true}
```

### Step 2: Pack charm
```
ccl pack
```

## How it works
Currently, during `charmcraft pack`, charmcraft can only access files in the directory that contains charmcraft.yaml.

charmcraftlocal
- searches (the charm's) pyproject.toml for local Python dependencies,
- copies them to the charm directory,
- and calls Poetry to update pyproject.toml and poetry.lock to reference the copied package(s)

