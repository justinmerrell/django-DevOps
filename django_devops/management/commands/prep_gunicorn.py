'''
A programatic way to prepare a gunicorn config file.
'''

import os
from textwrap import dedent
from os.path import exists

from django.core.management.base import BaseCommand, CommandError

from django.conf import settings

from django_devops.utils.user_input import query_yes_no

PROJECT_NAME = os.path.basename(os.path.normpath(settings.BASE_DIR))


class Command(BaseCommand):
    '''
    Programaticly generates a gunicorn config file.
    '''

    help = 'Prepare a gunicorn config file.'

    def handle(self, *args, **options):
        '''
        Verifies that the service folder exsists for use with django_devops
        '''
        if not exists(f'{settings.BASE_DIR}/{PROJECT_NAME}/service_files'):
            raise CommandError(f'''
                        {settings.BASE_DIR}/{PROJECT_NAME}/service_files does not exist.
                        First run "python manage.py devops" to configure django_devops.
                    ''')

        # Check if the file exsists and confirm overwrite.
        if exists(f'{settings.BASE_DIR}/{PROJECT_NAME}/service_files/gunicorn.service'):
            if query_yes_no(f'{PROJECT_NAME}/service_files/gunicorn.service exists. Overwrite?'):
                pass
            else:
                raise CommandError(f'''
                            {PROJECT_NAME}/service_files/gunicorn.service will not be overwritten.
                        ''')

        # Generate gunicorn.service file.
        file_template = f'''
                            [Unit]
                            Description=gunicorn daemon for {PROJECT_NAME}
                            After=network.target

                            [Service]
                            User=root
                            Group=www-data
                            WorkingDirectory=/opt/{PROJECT_NAME}/
                            ExecStart=/opt/{PROJECT_NAME}/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/opt/{PROJECT_NAME}/{PROJECT_NAME}.sock {PROJECT_NAME}.wsgi:application

                            [Install]
                            WantedBy=multi-user.target
                        '''

        file_path = f'{settings.BASE_DIR}/{PROJECT_NAME}/service_files'
        with open(f'{file_path}/gunicorn.service', 'w+', encoding='UTF-8') as file:
            file.seek(0)
            file.write(dedent(file_template))
            file.truncate()
