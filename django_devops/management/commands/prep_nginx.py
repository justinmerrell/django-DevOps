'''
A programatic way to prepare the nginx config file.
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
    Programaticly create the sites-available file.
    '''

    help = 'Prepare the nginx config file.'

    def handle(self, *args, **options):
        '''
        Verifies that the service folder exsis for use with django_devops
        '''
        if not exists(f'{settings.BASE_DIR}/{PROJECT_NAME}/config_files'):
            raise CommandError(f'''
                        {settings.BASE_DIR}/{PROJECT_NAME}/config_files does not exist.
                        First run "python manage.py devops" to configure django_devops.
                    ''')

        # Check if the file exsists and confirm overwrite.
        if exists(f'{settings.BASE_DIR}/{PROJECT_NAME}/config_files/{PROJECT_NAME}'):
            if query_yes_no(f'{PROJECT_NAME}/config_files/{PROJECT_NAME} exists. Overwrite?'):
                pass
            else:
                raise CommandError(f'''
                            {PROJECT_NAME}/config_files/{PROJECT_NAME} will not be overwritten.
                        ''')

        # Generate nginx config file.
        file_template = f'''
                           server {{
                                server_name

                                location /static/ {{
                                    root /var/www/{PROJECT_NAME};
                                }}

                                location / {{
                                    include proxy_params;
                                    proxy_pass http://unix:/opt/{PROJECT_NAME}/run/{PROJECT_NAME}.sock;
                                }}
                           }}
                        '''

        file_path = f'{settings.BASE_DIR}/{PROJECT_NAME}/config_files'
        with open(f'{file_path}/{PROJECT_NAME}', 'r+', encoding='UTF-8') as file:
            file.seek(0)
            file.write(dedent(file_template))
            file.truncate()
