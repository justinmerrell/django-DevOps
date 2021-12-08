'''
"devops" is a manage.py callable command that is called to run through project reccomendations
'''

import os
import sys

from django.core.management.base import BaseCommand, CommandError

from django.conf import settings

PROJECT_NAME = os.path.basename(os.path.normpath(settings.BASE_DIR))

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError(f"invalid default answer: {default}")

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]

        if choice in valid:
            return valid[choice]

        sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


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
        1) Make reccomendations for django-devops
        2)
        '''
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
