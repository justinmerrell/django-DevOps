'''
"devops" is a manage.py callable command that is called to run through project recommendations
'''

import os
import sys
import pwd

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from django_devops.utils.user_input import query_yes_no

PROJECT_NAME = os.path.basename(os.path.normpath(settings.BASE_DIR))
PROJECT_DIR = f'/opt/{PROJECT_NAME}'
ENV_FILE = f'{settings.BASE_DIR}/.env'
REQUIREMENTS_FILE = f'{PROJECT_DIR}/requirements.txt'

def get_base_prefix_compat():
    '''
    Get base/real prefix, or sys.prefix if there is none.
    '''
    return getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix


def in_virtualenv():
    '''
    Returns True if the code is running inside a virtualenv, False otherwise.
    '''
    return get_base_prefix_compat() != sys.prefix


class Command(BaseCommand):
    '''
    Steps through a user guided review to do the following:
    1) Create file locations used by django_devops
    2) Check for the presence of a virtual environment
    3) Make recommendations for GitHub Actions
    '''

    help = 'Runs through a user guided DevOps review and makes recommendations as needed.'

    def handle(self, *args, **options):
        '''
        1) Confirms project compliance with django_devops
        2) Make recommendations for django-devops
        '''
        # ----------------------------- Verify Compliance ---------------------------- #
        if not os.path.exists(PROJECT_DIR):
            raise CommandError(f'{PROJECT_NAME} is not installed in /opt/')
        print(f'✓ - {PROJECT_NAME} is installed in /opt/')

        # ----------------------- Check For Virtual Environment ---------------------- #
        if not in_virtualenv():
            raise CommandError(f'{PROJECT_NAME} is not running in a virtual environment')
        print(f'✓ - {PROJECT_NAME} is running in a virtual environment')

        # ---------------------------- Check For .env File --------------------------- #
        if not os.path.exists(ENV_FILE):
            raise CommandError(f'{PROJECT_NAME} is missing a .env file')
        print(f'✓ - {PROJECT_NAME} has a .env file')

        # ------------------------------ Recommendations ----------------------------- #
        folders = [
            ('config_files', f'{settings.BASE_DIR}/{PROJECT_NAME}/config_files'),
            ('service_files', f'{settings.BASE_DIR}/{PROJECT_NAME}/service_files')
        ]

        for folder_name, folder_path in folders:
            if not os.path.exists(folder_path):
                if query_yes_no(f'{PROJECT_NAME}/{folder_name} does not exist. Create it?'):
                    os.makedirs(folder_path)
                else:
                    raise CommandError(f'Please create the folder {folder_name}.')
            else:
                print(f'✓ - /{PROJECT_NAME}/{folder_name} exists.')

        # ----------------------------- Check System User ---------------------------- #
        try:
            pwd.getpwnam(f'{PROJECT_NAME}')
            print(f'✓ - System user "{PROJECT_NAME}" exists.')
        except KeyError:
            if query_yes_no(f'System user "{PROJECT_NAME}" does not exist. Create it?'):
                os.system(f'''
                          adduser --system --no-create-home
                          --disabled-password --ingroup=www-data
                          --shell=/bin/bash --add_extra_groups {PROJECT_NAME}
                          ''')

                os.system(f"addgroup --system {PROJECT_NAME}")

                os.system(f"usermod -a -G {PROJECT_NAME} {PROJECT_NAME}")

                os.system(f"chgrp -R {PROJECT_NAME} /opt/{PROJECT_NAME}")

                os.system(f"chmod -R 775 /opt/{PROJECT_NAME}")

        # -------------------------- Static File Permissions ------------------------- #
        # chmod o+r - R

        # -------------------------- Python Package Versions ------------------------- #
        if not os.path.exists(REQUIREMENTS_FILE):
            if query_yes_no(f'{REQUIREMENTS_FILE} does not exist. Create it?'):
                os.system(f'pip freeze > /opt/{PROJECT_NAME}/requirements.txt')
            else:
                raise CommandError('Please create the file requirements.txt.')
        else:
            print(f'✓ - /opt/{PROJECT_NAME}/requirements.txt exists.')

        # Ensures that packages have a fixed version number.
        with open(f'/opt/{PROJECT_NAME}/requirements.txt', 'r', encoding="UTF-8") as file:
            requirements = file.readlines()

        packages = []
        for requirement in requirements:
            if not '==' in requirement:
                package_name = requirement.split('> | < | =')[0]
                packages.append(package_name)

        if packages:
            if query_yes_no(f'These packages are missing fixed versions: {packages}. Fix them?'):
                os.system(f'pip freeze > {REQUIREMENTS_FILE}')
            else:
                raise CommandError('Please fix the version numbers of the packages.')
        else:
            print('✓ - All packages have a fixed version number.')

        # -------------------------- Verifies GitHub Actions ------------------------- #
        github_workflow_dir = f'{settings.BASE_DIR}/.github/workflows'
        pylint_workflow_file = f'{github_workflow_dir}/pylint.yml'

        if not os.path.exists(github_workflow_dir):
            if query_yes_no('GitHub workflows directory is missing. Create it?'):
                os.makedirs(github_workflow_dir)
            else:
                raise CommandError('Please create the .github/workflows directory.')

        if not os.path.exists(pylint_workflow_file):
            if query_yes_no('Pylint GitHub Action is missing. Create it?'):
                pylint_workflow_content = '''
                name: Pylint

                on:
                push:
                    branches:
                    - main
                pull_request:
                    branches:
                    - main

                jobs:
                pylint:
                    runs-on: ubuntu-latest
                    steps:
                    - name: Check out repository
                        uses: actions/checkout@v2

                    - name: Set up Python
                        uses: actions/setup-python@v2
                        with:
                        python-version: 3.x

                    - name: Install dependencies
                        run: |
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt

                    - name: Run Pylint
                        run: pylint --fail-under=9 --output-format=colorized --reports=no **/*.py
                    '''

                with open(pylint_workflow_file, 'w', encoding="UTF-8") as file:
                    file.write(pylint_workflow_content)
                    print('✓ - Pylint GitHub Action created.')
            else:
                raise CommandError('Please create the Pylint GitHub Action.')
        else:
            print(f'✓ - Pylint GitHub Action exists at {pylint_workflow_file}.')
