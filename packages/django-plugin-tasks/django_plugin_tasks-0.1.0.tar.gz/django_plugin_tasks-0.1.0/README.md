# django-plugin-tasks

[![PyPI](https://img.shields.io/pypi/v/django-plugin-tasks.svg)](https://pypi.org/project/django-plugin-tasks/)
[![Changelog](https://img.shields.io/github/v/release/Sleppy-Technologies/django-plugin-tasks?include_prereleases&label=changelog)](https://github.com/Sleppy-Technologies/django-plugin-tasks/releases)
[![Tests](https://github.com/Sleppy-Technologies/django-plugin-tasks/workflows/Test/badge.svg)](https://github.com/Sleppy-Technologies/django-plugin-tasks/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/Sleppy-Technologies/django-plugin-tasks/blob/main/LICENSE)

Django plugin wrapping django_tasks for background work

## Installation

First configure your Django project [to use DJP](https://djp.readthedocs.io/en/latest/installing_plugins.html).

Then install this plugin in the same environment as your Django application.

```bash
pip install django-plugin-tasks
```

## Usage

The plugin defaults to using the `DatabaseBackend`, which is a reasonable for production and local development. Override these settings as desired after the `djp.settings(globals())` call. For example, you may want to run the `DummyBackend` or `ImmediateBackend` while running tests.

No further configuration is needed, refer to [`django_tasks` documentation](https://github.com/RealOrangeOne/django-tasks) to learn about your new capabilities.

## Development

Install `uv` following [`uv`'s install documentation](https://docs.astral.sh/uv/getting-started/installation/). Install [`just`](https://just.systems/man/en/introduction.html) with `uv tool install rust-just`.

### Testing

`just test`

### Linting

`just lint`
