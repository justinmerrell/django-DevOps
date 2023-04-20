'''
auth.py is callable with manage.py using the command "do_guide_auth"
'''

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


PROJECT_NAME = os.path.basename(os.path.normpath(settings.BASE_DIR))


def confirm_file(name, path=None):
    """
    Finds a file by name.
    If path is set, it will confirm file is in that path.
    Returns True if file is found, False otherwise.
    """
    for root, _, files in os.walk(os.path.join('opt', PROJECT_NAME)):
        if name in files and (not path or path in root):
            return True
    return False


class Command(BaseCommand):
    """
    Steps through the guide and makes recommendations related to the Django authentication system.
    """

    help = 'Runs through a user guided DevOps review and makes recommendations as needed.'

    def handle(self, *args, **options):
        """
        Steps through a best practice guide checking the following:
        1) `LOGIN_URL` is set in settings.py
        2) `LOGIN_REDIRECT_URL` is set in settings.py
        3) `LOGOUT_REDIRECT_URL` is set in settings.py
        """

        errors_found = False

        # ----------------------------- Verify Templates ----------------------------- #
        template_checklist = [
            ('login.html', 'templates/registration'),
            ('register.html', 'templates/registration')
        ]

        for file_name, expected_path in template_checklist:
            if confirm_file(file_name, expected_path):
                print(f'✓ - {file_name} found in {expected_path}/')
            else:
                print(f'✗ - {file_name} not found in {expected_path}/')
                errors_found = True

        # ----------------------------- Verify Settings ----------------------------- #
        settings_checklist = [
            ('LOGIN_URL', 'LOGIN_URL'),
            ('LOGIN_REDIRECT_URL', 'LOGIN_REDIRECT_URL'),
            ('LOGOUT_REDIRECT_URL', 'LOGOUT_REDIRECT_URL')
        ]

        for attr, display_name in settings_checklist:
            if not hasattr(settings, attr):
                errors_found = True
                print(f'✗ | {display_name} is not set in settings.py')
            else:
                print(f'✓ | {display_name} is set in settings.py to {getattr(settings, attr)}')

        # ------------------------------- Report Errors ------------------------------ #
        if errors_found:
            raise CommandError('One or more errors were found in the guide.')
