# hatch-project-name

| | |
| --- | --- |
| CI/CD | [![CI - Test](https://github.com/valentinoli/hatch-project-name/actions/workflows/test.yml/badge.svg)](https://github.com/valentinoli/hatch-project-name/actions/workflows/test.yml) [![CD - Build](https://github.com/valentinoli/hatch-project-name/actions/workflows/build.yml/badge.svg)](https://github.com/valentinoli/hatch-project-name/actions/workflows/build.yml) |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/hatch-project-name.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/hatch-project-name/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-project-name.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/hatch-project-name/) |
| Meta | [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://docs.astral.sh/uv/) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://mypy.readthedocs.io/en/stable/) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) |

-----

This provides a build hook plugin for [Hatch](https://github.com/pypa/hatch) that writes the project name defined in `pyproject.toml` to a file.

**Table of Contents**

- [Rationale](#rationale)
- [Configuration](#configuration)
  - [Build hook options](#build-hook-options)
  - [Editable installs](#editable-installs)
- [License](#license)

## Rationale

TODO

## Configuration

The [build hook plugin](https://hatch.pypa.io/latest/plugins/build-hook/reference/) name is `project-name`.

- ***pyproject.toml***

    ```toml
    [project]
    name = "my-package"

    [tool.hatch.build.hooks.project-name]
    dependencies = ["hatch-project-name"]
    name-file = "src/my_package/_name.py"
    ```

- ***hatch.toml***

    ```toml
    [project]
    name = "my-package"

    [build.hooks.project-name]
    dependencies = ["hatch-project-name"]
    name-file = "src/my_package/_name.py"
    ```

Building the project will generate the file

- ***_name.py***

    ```python
    project_name = __project_name__ = distribution_name = __distribution_name__ = "my-package"
    ```

### Build hook options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `name-file` | `str` | ***REQUIRED*** | The relative path to the file that gets updated with the project name. |

### Editable installs

The name file is only updated upon install or build. Thus the name in an [editable install](https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs) (Hatch's [dev mode](https://hatch.pypa.io/latest/config/build/#dev-mode)) will be incorrect if the name is changed in `pyproject.toml` and the project is not rebuilt.

## License

`hatch-project-name` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
