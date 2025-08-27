<a id="mypy-boto3-greengrass"></a>

# mypy-boto3-greengrass

[![PyPI - mypy-boto3-greengrass](https://img.shields.io/pypi/v/mypy-boto3-greengrass.svg?color=blue)](https://pypi.org/project/mypy-boto3-greengrass/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mypy-boto3-greengrass.svg?color=blue)](https://pypi.org/project/mypy-boto3-greengrass/)
[![Docs](https://img.shields.io/readthedocs/boto3-stubs.svg?color=blue)](https://youtype.github.io/boto3_stubs_docs/)
[![PyPI - Downloads](https://static.pepy.tech/badge/mypy-boto3-greengrass)](https://pypistats.org/packages/mypy-boto3-greengrass)

![boto3.typed](https://github.com/youtype/mypy_boto3_builder/raw/main/logo.png)

Type annotations for
[boto3 Greengrass 1.40.18](https://pypi.org/project/boto3/) compatible with
[VSCode](https://code.visualstudio.com/),
[PyCharm](https://www.jetbrains.com/pycharm/),
[Emacs](https://www.gnu.org/software/emacs/),
[Sublime Text](https://www.sublimetext.com/),
[mypy](https://github.com/python/mypy),
[pyright](https://github.com/microsoft/pyright) and other tools.

Generated with
[mypy-boto3-builder 8.11.0](https://github.com/youtype/mypy_boto3_builder).

More information can be found on
[boto3-stubs](https://pypi.org/project/boto3-stubs/) page and in
[mypy-boto3-greengrass docs](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_greengrass/).

See how it helps you find and fix potential bugs:

![types-boto3 demo](https://github.com/youtype/mypy_boto3_builder/raw/main/demo.gif)

- [mypy-boto3-greengrass](#mypy-boto3-greengrass)
  - [How to install](#how-to-install)
    - [Generate locally (recommended)](<#generate-locally-(recommended)>)
    - [VSCode extension](#vscode-extension)
    - [From PyPI with pip](#from-pypi-with-pip)
  - [How to uninstall](#how-to-uninstall)
  - [Usage](#usage)
    - [VSCode](#vscode)
    - [PyCharm](#pycharm)
    - [Emacs](#emacs)
    - [Sublime Text](#sublime-text)
    - [Other IDEs](#other-ides)
    - [mypy](#mypy)
    - [pyright](#pyright)
    - [Pylint compatibility](#pylint-compatibility)
  - [Explicit type annotations](#explicit-type-annotations)
    - [Client annotations](#client-annotations)
    - [Paginators annotations](#paginators-annotations)
    - [Literals](#literals)
    - [Type definitions](#type-definitions)
  - [How it works](#how-it-works)
  - [What's new](#what's-new)
    - [Implemented features](#implemented-features)
    - [Latest changes](#latest-changes)
  - [Versioning](#versioning)
  - [Thank you](#thank-you)
  - [Documentation](#documentation)
  - [Support and contributing](#support-and-contributing)

<a id="how-to-install"></a>

## How to install

<a id="generate-locally-(recommended)"></a>

### Generate locally (recommended)

You can generate type annotations for `boto3` package locally with
`mypy-boto3-builder`. Use
[uv](https://docs.astral.sh/uv/getting-started/installation/) for build
isolation.

1. Run mypy-boto3-builder in your package root directory:
   `uvx --with 'boto3==1.40.18' mypy-boto3-builder`
2. Select `boto3-stubs` AWS SDK.
3. Add `Greengrass` service.
4. Use provided commands to install generated packages.

<a id="vscode-extension"></a>

### VSCode extension

Add
[AWS Boto3](https://marketplace.visualstudio.com/items?itemName=Boto3typed.boto3-ide)
extension to your VSCode and run `AWS boto3: Quick Start` command.

Click `Modify` and select `boto3 common` and `Greengrass`.

<a id="from-pypi-with-pip"></a>

### From PyPI with pip

Install `boto3-stubs` for `Greengrass` service.

```bash
# install with boto3 type annotations
python -m pip install 'boto3-stubs[greengrass]'

# Lite version does not provide session.client/resource overloads
# it is more RAM-friendly, but requires explicit type annotations
python -m pip install 'boto3-stubs-lite[greengrass]'

# standalone installation
python -m pip install mypy-boto3-greengrass
```

<a id="how-to-uninstall"></a>

## How to uninstall

```bash
python -m pip uninstall -y mypy-boto3-greengrass
```

<a id="usage"></a>

## Usage

<a id="vscode"></a>

### VSCode

- Install
  [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- Install
  [Pylance extension](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- Set `Pylance` as your Python Language Server
- Install `boto3-stubs[greengrass]` in your environment:

```bash
python -m pip install 'boto3-stubs[greengrass]'
```

Both type checking and code completion should now work. No explicit type
annotations required, write your `boto3` code as usual.

<a id="pycharm"></a>

### PyCharm

> ⚠️ Due to slow PyCharm performance on `Literal` overloads (issue
> [PY-40997](https://youtrack.jetbrains.com/issue/PY-40997)), it is recommended
> to use [boto3-stubs-lite](https://pypi.org/project/boto3-stubs-lite/) until
> the issue is resolved.

> ⚠️ If you experience slow performance and high CPU usage, try to disable
> `PyCharm` type checker and use [mypy](https://github.com/python/mypy) or
> [pyright](https://github.com/microsoft/pyright) instead.

> ⚠️ To continue using `PyCharm` type checker, you can try to replace
> `boto3-stubs` with
> [boto3-stubs-lite](https://pypi.org/project/boto3-stubs-lite/):

```bash
pip uninstall boto3-stubs
pip install boto3-stubs-lite
```

Install `boto3-stubs[greengrass]` in your environment:

```bash
python -m pip install 'boto3-stubs[greengrass]'
```

Both type checking and code completion should now work.

<a id="emacs"></a>

### Emacs

- Install `boto3-stubs` with services you use in your environment:

```bash
python -m pip install 'boto3-stubs[greengrass]'
```

- Install [use-package](https://github.com/jwiegley/use-package),
  [lsp](https://github.com/emacs-lsp/lsp-mode/),
  [company](https://github.com/company-mode/company-mode) and
  [flycheck](https://github.com/flycheck/flycheck) packages
- Install [lsp-pyright](https://github.com/emacs-lsp/lsp-pyright) package

```elisp
(use-package lsp-pyright
  :ensure t
  :hook (python-mode . (lambda ()
                          (require 'lsp-pyright)
                          (lsp)))  ; or lsp-deferred
  :init (when (executable-find "python3")
          (setq lsp-pyright-python-executable-cmd "python3"))
  )
```

- Make sure emacs uses the environment where you have installed `boto3-stubs`

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="sublime-text"></a>

### Sublime Text

- Install `boto3-stubs[greengrass]` with services you use in your environment:

```bash
python -m pip install 'boto3-stubs[greengrass]'
```

- Install [LSP-pyright](https://github.com/sublimelsp/LSP-pyright) package

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="other-ides"></a>

### Other IDEs

Not tested, but as long as your IDE supports `mypy` or `pyright`, everything
should work.

<a id="mypy"></a>

### mypy

- Install `mypy`: `python -m pip install mypy`
- Install `boto3-stubs[greengrass]` in your environment:

```bash
python -m pip install 'boto3-stubs[greengrass]'
```

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="pyright"></a>

### pyright

- Install `pyright`: `npm i -g pyright`
- Install `boto3-stubs[greengrass]` in your environment:

```bash
python -m pip install 'boto3-stubs[greengrass]'
```

Optionally, you can install `boto3-stubs` to `typings` directory.

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="pylint-compatibility"></a>

### Pylint compatibility

It is totally safe to use `TYPE_CHECKING` flag in order to avoid
`mypy-boto3-greengrass` dependency in production. However, there is an issue in
`pylint` that it complains about undefined variables. To fix it, set all types
to `object` in non-`TYPE_CHECKING` mode.

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_ec2 import EC2Client, EC2ServiceResource
    from mypy_boto3_ec2.waiters import BundleTaskCompleteWaiter
    from mypy_boto3_ec2.paginators import DescribeVolumesPaginator
else:
    EC2Client = object
    EC2ServiceResource = object
    BundleTaskCompleteWaiter = object
    DescribeVolumesPaginator = object

...
```

<a id="explicit-type-annotations"></a>

## Explicit type annotations

<a id="client-annotations"></a>

### Client annotations

`GreengrassClient` provides annotations for `boto3.client("greengrass")`.

```python
from boto3.session import Session

from mypy_boto3_greengrass import GreengrassClient

client: GreengrassClient = Session().client("greengrass")

# now client usage is checked by mypy and IDE should provide code completion
```

<a id="paginators-annotations"></a>

### Paginators annotations

`mypy_boto3_greengrass.paginator` module contains type annotations for all
paginators.

```python
from boto3.session import Session

from mypy_boto3_greengrass import GreengrassClient
from mypy_boto3_greengrass.paginator import (
    ListBulkDeploymentDetailedReportsPaginator,
    ListBulkDeploymentsPaginator,
    ListConnectorDefinitionVersionsPaginator,
    ListConnectorDefinitionsPaginator,
    ListCoreDefinitionVersionsPaginator,
    ListCoreDefinitionsPaginator,
    ListDeploymentsPaginator,
    ListDeviceDefinitionVersionsPaginator,
    ListDeviceDefinitionsPaginator,
    ListFunctionDefinitionVersionsPaginator,
    ListFunctionDefinitionsPaginator,
    ListGroupVersionsPaginator,
    ListGroupsPaginator,
    ListLoggerDefinitionVersionsPaginator,
    ListLoggerDefinitionsPaginator,
    ListResourceDefinitionVersionsPaginator,
    ListResourceDefinitionsPaginator,
    ListSubscriptionDefinitionVersionsPaginator,
    ListSubscriptionDefinitionsPaginator,
)

client: GreengrassClient = Session().client("greengrass")

# Explicit type annotations are optional here
# Types should be correctly discovered by mypy and IDEs
list_bulk_deployment_detailed_reports_paginator: ListBulkDeploymentDetailedReportsPaginator = (
    client.get_paginator("list_bulk_deployment_detailed_reports")
)
list_bulk_deployments_paginator: ListBulkDeploymentsPaginator = client.get_paginator(
    "list_bulk_deployments"
)
list_connector_definition_versions_paginator: ListConnectorDefinitionVersionsPaginator = (
    client.get_paginator("list_connector_definition_versions")
)
list_connector_definitions_paginator: ListConnectorDefinitionsPaginator = client.get_paginator(
    "list_connector_definitions"
)
list_core_definition_versions_paginator: ListCoreDefinitionVersionsPaginator = client.get_paginator(
    "list_core_definition_versions"
)
list_core_definitions_paginator: ListCoreDefinitionsPaginator = client.get_paginator(
    "list_core_definitions"
)
list_deployments_paginator: ListDeploymentsPaginator = client.get_paginator("list_deployments")
list_device_definition_versions_paginator: ListDeviceDefinitionVersionsPaginator = (
    client.get_paginator("list_device_definition_versions")
)
list_device_definitions_paginator: ListDeviceDefinitionsPaginator = client.get_paginator(
    "list_device_definitions"
)
list_function_definition_versions_paginator: ListFunctionDefinitionVersionsPaginator = (
    client.get_paginator("list_function_definition_versions")
)
list_function_definitions_paginator: ListFunctionDefinitionsPaginator = client.get_paginator(
    "list_function_definitions"
)
list_group_versions_paginator: ListGroupVersionsPaginator = client.get_paginator(
    "list_group_versions"
)
list_groups_paginator: ListGroupsPaginator = client.get_paginator("list_groups")
list_logger_definition_versions_paginator: ListLoggerDefinitionVersionsPaginator = (
    client.get_paginator("list_logger_definition_versions")
)
list_logger_definitions_paginator: ListLoggerDefinitionsPaginator = client.get_paginator(
    "list_logger_definitions"
)
list_resource_definition_versions_paginator: ListResourceDefinitionVersionsPaginator = (
    client.get_paginator("list_resource_definition_versions")
)
list_resource_definitions_paginator: ListResourceDefinitionsPaginator = client.get_paginator(
    "list_resource_definitions"
)
list_subscription_definition_versions_paginator: ListSubscriptionDefinitionVersionsPaginator = (
    client.get_paginator("list_subscription_definition_versions")
)
list_subscription_definitions_paginator: ListSubscriptionDefinitionsPaginator = (
    client.get_paginator("list_subscription_definitions")
)
```

<a id="literals"></a>

### Literals

`mypy_boto3_greengrass.literals` module contains literals extracted from shapes
that can be used in user code for type checking.

Full list of `Greengrass` Literals can be found in
[docs](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_greengrass/literals/).

```python
from mypy_boto3_greengrass.literals import BulkDeploymentStatusType


def check_value(value: BulkDeploymentStatusType) -> bool: ...
```

<a id="type-definitions"></a>

### Type definitions

`mypy_boto3_greengrass.type_defs` module contains structures and shapes
assembled to typed dictionaries and unions for additional type checking.

Full list of `Greengrass` TypeDefs can be found in
[docs](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_greengrass/type_defs/).

```python
# TypedDict usage example
from mypy_boto3_greengrass.type_defs import AssociateRoleToGroupRequestTypeDef


def get_value() -> AssociateRoleToGroupRequestTypeDef:
    return {
        "GroupId": ...,
    }
```

<a id="how-it-works"></a>

## How it works

Fully automated
[mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder) carefully
generates type annotations for each service, patiently waiting for `boto3`
updates. It delivers drop-in type annotations for you and makes sure that:

- All available `boto3` services are covered.
- Each public class and method of every `boto3` service gets valid type
  annotations extracted from `botocore` schemas.
- Type annotations include up-to-date documentation.
- Link to documentation is provided for every method.
- Code is processed by [ruff](https://docs.astral.sh/ruff/) for readability.

<a id="what's-new"></a>

## What's new

<a id="implemented-features"></a>

### Implemented features

- Fully type annotated `boto3`, `botocore`, `aiobotocore` and `aioboto3`
  libraries
- `mypy`, `pyright`, `VSCode`, `PyCharm`, `Sublime Text` and `Emacs`
  compatibility
- `Client`, `ServiceResource`, `Resource`, `Waiter` `Paginator` type
  annotations for each service
- Generated `TypeDefs` for each service
- Generated `Literals` for each service
- Auto discovery of types for `boto3.client` and `boto3.resource` calls
- Auto discovery of types for `session.client` and `session.resource` calls
- Auto discovery of types for `client.get_waiter` and `client.get_paginator`
  calls
- Auto discovery of types for `ServiceResource` and `Resource` collections
- Auto discovery of types for `aiobotocore.Session.create_client` calls

<a id="latest-changes"></a>

### Latest changes

Builder changelog can be found in
[Releases](https://github.com/youtype/mypy_boto3_builder/releases).

<a id="versioning"></a>

## Versioning

`mypy-boto3-greengrass` version is the same as related `boto3` version and
follows
[Python Packaging version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/).

<a id="thank-you"></a>

## Thank you

- [Allie Fitter](https://github.com/alliefitter) for
  [boto3-type-annotations](https://pypi.org/project/boto3-type-annotations/),
  this package is based on top of his work
- [black](https://github.com/psf/black) developers for an awesome formatting
  tool
- [Timothy Edmund Crosley](https://github.com/timothycrosley) for
  [isort](https://github.com/PyCQA/isort) and how flexible it is
- [mypy](https://github.com/python/mypy) developers for doing all dirty work
  for us
- [pyright](https://github.com/microsoft/pyright) team for the new era of typed
  Python

<a id="documentation"></a>

## Documentation

All services type annotations can be found in
[boto3 docs](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_greengrass/)

<a id="support-and-contributing"></a>

## Support and contributing

This package is auto-generated. Please reports any bugs or request new features
in [mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder/issues/)
repository.
