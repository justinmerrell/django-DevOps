<div align="center">

<h1> django-DevOps </h1>

[![Code Quality](https://github.com/justinmerrell/django-DevOps/actions/workflows/pylint.yml/badge.svg)](https://github.com/justinmerrell/django-DevOps/actions/workflows/pylint.yml)
[![Script Check](https://github.com/justinmerrell/django-DevOps/actions/workflows/shellcheck.yml/badge.svg)](https://github.com/justinmerrell/django-DevOps/actions/workflows/shellcheck.yml) &nbsp;
[![CodeQL](https://github.com/justinmerrell/django-DevOps/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/justinmerrell/django-DevOps/actions/workflows/codeql-analysis.yml)

</div>

## Table of Contents

- [Table of Contents](#table-of-contents)
- [What is django-DevOps?](#what-is-django-devops)
- [Getting Started](#getting-started)
  - [Configuration Files](#configuration-files)
- [Manage Commands](#manage-commands)
- [Directory Structure](#directory-structure)
- [License](#license)

## What is django-DevOps?

The goal of this repository is to provide a set of programmatic tools to help you build and deploy your Django projects. This is done by defining best practices for the following:

- Service and Config file management
- Auto deploy from GIT
- Guided feature implementation

No more returning to the same Stackoverflow pages every time you start a new project just to remind yourself what directory config files should be placed in. All files can now be managed from a project level and quickly deployed/updated.

## Getting Started

To install the package, run the following command:

```bash
pip install django-DevOps
```

Then add `django_devoop` to your `INSTALLED_APPS` list in your `settings.py` file.

```python
INSTALLED_APPS = [
    ...
    'django_devops',
    ...
]
```

For additional pip information visit: [https://pypi.org/project/django-DevOps/](https://pypi.org/project/django-DevOps/)

### Configuration Files

Under your project folder create a ```config_files``` and ```service_files``` folder to place files to be deployed.

A config file with the same name as the project will be treated as the NGINX config file and copied to site-available.

## Manage Commands

| Command          | Description                                                                                            |
|------------------|--------------------------------------------------------------------------------------------------------|
| devops           | Guided project review. (Recommended)                                                                   |
| do_guide_account | Walks through the guide for user account management.                                                   |
| prep_gunicorn    | Prepares the gunicorn config file for use with gunicorn.                                               |
| prep_celery      | Prepares the celery config file for use with celery.                                                   |
| prep_nginx       | Prepares the nginx config file for use with nginx.                                                     |
| update_services  | Similar to "collectstatic", this command will deploy config and service files from the project folder. |

## Directory Structure

```default
.
├── .github             # CI/CD using GitHub Actions and other functions.
└── django_devops       # Main package directory.
```

## License

This project is licensed under the terms of the [MIT license](https://opensource.org/licenses/MIT).
