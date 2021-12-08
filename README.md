<div align="center">

<h1> django-DevOps </h1>

[![Code Quality](https://github.com/justinmerrell/django-DevOps/actions/workflows/pylint.yml/badge.svg)](https://github.com/justinmerrell/django-DevOps/actions/workflows/pylint.yml)
[![Script Check](https://github.com/justinmerrell/django-DevOps/actions/workflows/shellcheck.yml/badge.svg)](https://github.com/justinmerrell/django-DevOps/actions/workflows/shellcheck.yml) &nbsp;
[![CodeQL](https://github.com/justinmerrell/django-DevOps/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/justinmerrell/django-DevOps/actions/workflows/codeql-analysis.yml)

</div>

## Table of Contents

- [Table of Contents](#table-of-contents)
- [What is django-DevOps?](#what-is-django-devops)
- [Getting Started](#getting-Started)
- [Manage Commands](#manage-commands)
- [Directory Structure](#directory-structure)

## What is django-DevOps?

The goal of this repository is to provide a set of programatic tools to help you build and deploy your Django projects. This is done by defining best practices for the following:

- Service and Config file management
- Auto deploy from GIT

## Getting Started

To install the package, run the following command:

```bash
pip install django-DevOps
```

Then add `django_devoop` to your `INSTALLED_APPS` list in your `settings.py` file.

```pytohn
INSTALLED_APPS = [
    ...
    'django_devops',
    ...
]
```

For additional pip information visit: [https://pypi.org/project/django-DevOps/](https://pypi.org/project/django-DevOps/)

### Configuration Files

Under your project folder create a ```config_files``` and ```service_files``` folder to place files to be deployed.

## Manage Commands

| Command         | Description                                                                                            |
|-----------------|--------------------------------------------------------------------------------------------------------|
| devops          | Guided project review. (Reccomended)                                                                   |
| update_services | Similar to "collectstatic", this command will deploy config and service files from the project folder. |

## Directory Structure

```default
.
├── .github             # CI/CD using GitHub Actions and other functions.
└── django_devops       # Main package directory.
```
