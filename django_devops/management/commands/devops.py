'''
"devops" is a manage.py callable command that is called to run through project reccomendations
'''

import os
import sys

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
    Stepts through a user guided review to do the following:
    1) Create file locations used by django_devops
    2) Check for the presence of a virtual environment
    3) Make recomendations for GitHub Actions
    '''

    help = 'Runs through a user guided DevOps review and makes reccomendations as needed.'

    def handle(self, *args, **options):
        '''
        1) Confirms project compliance with django_devops
        2) Make reccomendations for django-devops
        '''
        # ----------------------------- Verify Compliance ---------------------------- #
        if not os.path.exists(f'/opt/{PROJECT_NAME}'):
            raise CommandError(f'{PROJECT_NAME} is not installed in /opt/')
        print(f'✓ - {PROJECT_NAME} is installed in /opt/')


        # ----------------------- Check For Virtual Environment ---------------------- #
        if not in_virtualenv():
            raise CommandError(f'{PROJECT_NAME} is not running in a virtual environment')
        print(f'✓ - {PROJECT_NAME} is running in a virtual environment')




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

        # -------------------------- Verifies GitHub Actions ------------------------- #
