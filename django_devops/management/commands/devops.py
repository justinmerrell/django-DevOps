'''
"devops" is a manage.py callable command that is called to run through project recommendations
'''

import os
import sys
import pwd

from django.core.management.base import BaseCommand, CommandError

from django.conf import settings

from django_devops.utils.user_input import query_yes_no


PROJECT_NAME = os.path.basename(os.path.normpath(settings.BASE_DIR))


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
        if not os.path.exists(f'/opt/{PROJECT_NAME}'):
            raise CommandError(f'{PROJECT_NAME} is not installed in /opt/')
        print(f'✓ - {PROJECT_NAME} is installed in /opt/')

        # ----------------------- Check For Virtual Environment ---------------------- #
        if not in_virtualenv():
            raise CommandError(f'{PROJECT_NAME} is not running in a virtual environment')
        print(f'✓ - {PROJECT_NAME} is running in a virtual environment')

        # ---------------------------- Check For .env File --------------------------- #
        if not os.path.exists(f'{settings.BASE_DIR}/{PROJECT_NAME}/.env'):
            raise CommandError(f'{PROJECT_NAME} is missing a .env file')
        print(f'✓ - {PROJECT_NAME} has a .env file')

        # ------------------------------ Recommendations ----------------------------- #
        # Checks that the folder 'config_files' exists.
        if not os.path.exists(f'{settings.BASE_DIR}/{PROJECT_NAME}/config_files'):
            if query_yes_no(f'{PROJECT_NAME}/config_files does not exist. Create it?'):
                os.makedirs(f'{settings.BASE_DIR}/{PROJECT_NAME}/config_files')
            else:
                raise CommandError('Please create the folder config_files.')
        else:
            print(f'✓ - /{PROJECT_NAME}/config_files exists.')

        # Checks that the folder 'service_files' exists.
        if not os.path.exists(f'{settings.BASE_DIR}/{PROJECT_NAME}/service_files'):
            if query_yes_no(f'{PROJECT_NAME}/service_files does not exist. Create it?'):
                os.makedirs(f'{settings.BASE_DIR}/{PROJECT_NAME}/service_files')
            else:
                raise CommandError('Please create the folder service_files.')
        else:
            print(f'✓ - /{PROJECT_NAME}/service_files exists.')

        # Checks for system user.
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
        # Checks that requirements.txt exists, and if not, creates it.
        if not os.path.exists(f'/opt/{PROJECT_NAME}/requirements.txt'):
            if query_yes_no(f'/opt/{PROJECT_NAME}/requirements.txt does not exist. Create it?'):
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
                os.system(f'pip freeze > /opt/{PROJECT_NAME}/requirements.txt')
            else:
                raise CommandError('Please fix the version numbers of the packages.')
        else:
            print('✓ - All packages have a fixed version number.')

        # -------------------------- Verifies GitHub Actions ------------------------- #
