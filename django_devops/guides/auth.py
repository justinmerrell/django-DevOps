'''
auth.py is callable with manage.py using the command "do_guide_auth"
'''

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


PROJECT_NAME = os.path.basename(os.path.normpath(settings.BASE_DIR))


def confirm_file(name, path=None):
    '''
    Finds a file by name.
    If path is set, it will confirm file is in that path.
    Returns True if file is found, False otherwise.
    '''
    for root, _, files in os.walk(os.path.join('opt', PROJECT_NAME)):
        if name in files:
            if path:
                if path in root:
                    return True

    return False


class Command(BaseCommand):
    '''
    Steps through the guide and makes recommendations related to the Django authentication system.
    '''

    help = 'Runs through a user guided DevOps review and makes recommendations as needed.'

    def handle(self, *args, **options):
        '''
        Steps through a best practice guide checking the following:
        1) `LOGIN_URL` is set in settings.py
        2) `LOGIN_REDIRECT_URL` is set in settings.py
        3) `LOGOUT_REDIRECT_URL` is set in settings.py
        '''

        errors_found = False

        # ----------------------------- Verify Templates ----------------------------- #
        # login.html
        if confirm_file('login.html', 'templates/registration'):
            print('✓ - login.html found in templates/registration/')
        else:
            print('✗ - login.html not found in templates/registration/')
            errors_found = True

        # register.html
        if confirm_file('register.html', 'templates/registration'):
            print('✓ - register.html found in templates/registration/')
        else:
            print('✗ - register.html not found in templates/registration/')
            errors_found = True

        # ----------------------------- Verify LOGIN_URL ----------------------------- #
        if not hasattr(settings, 'LOGIN_URL'):
            errors_found = True
            print('✗ | LOGIN_URL is not set in settings.py')
        else:
            print(f'✓ | LOGIN_URL is set in settings.py to {settings.LOGIN_URL}')

        # -------------------------- Verify LOGIN_REDIRECT_URL ----------------------- #
        if not hasattr(settings, 'LOGIN_REDIRECT_URL'):
            errors_found = True
            print('✗ | LOGIN_REDIRECT_URL is not set in settings.py')
        else:
            print(f'✓ | LOGIN_REDIRECT_URL is set in settings.py to {settings.LOGIN_REDIRECT_URL}')

        # -------------------------- Verify LOGOUT_REDIRECT_URL ----------------------- #
        if not hasattr(settings, 'LOGOUT_REDIRECT_URL'):
            errors_found = True
            print('✗ | LOGOUT_REDIRECT_URL is not set in settings.py')
        else:
            print(f'✓ | LOGOUT_REDIRECT_URL set in settings.py to {settings.LOGOUT_REDIRECT_URL}')

        # ------------------------------- Report Errors ------------------------------ #
        if errors_found:
            raise CommandError('One or more errors were found in the guide.')
