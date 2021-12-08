''' Deploys configuration and services for the application '''

import os
import subprocess

from django.core.management.base import BaseCommand

from django.conf import settings

class Command(BaseCommand):
    '''
    Checks that configuration and service files exsist and have not beeen deployed before deploying
    '''

    help = 'Deploys configuration and services for the application'

    def handle(self, *args, **options):
        '''
        Deploys configuration and services for the application
        '''
        # Check if /etc/conf.d/ directory exists
        if not os.path.exists('/etc/conf.d'):
            os.makedirs('/etc/conf.d')

        project_name = os.path.basename(os.path.normpath(settings.BASE_DIR))

        # ---------------------------- Update Config Files --------------------------- #
        nginx = False # Flag to check if an Nginx config file is present.

        try:
            file_path = f'{settings.BASE_DIR}/{project_name}/config_files'

            for filename in os.listdir(file_path):
                with open(os.path.join(file_path, filename), 'r', encoding='UTF-8') as file:
                    file_content = file.read()
                    file.close()

                # Handle configfile with same name as project as web service config file.
                if filename == project_name:
                    nginx = True
                    deploy_path = '/etc/nginx/sites-available/'
                else:
                    deploy_path = '/etc/conf.d/'


                # Create config file if it does not exist
                with subprocess.Popen(['touch', f'{deploy_path}{filename}']) as script:
                    print(script)

                # Update config file to match
                with open(f'{deploy_path}{filename}', encoding='UTF-8') as file:
                    file_content_old = file.read()
                    file.close()

                if file_content != file_content_old:
                    with(open(f'{deploy_path}{filename}.old', 'w', encoding='UTF-8')) as file:
                        file.write(file_content_old)
                        file.close()

                    with open(f'{deploy_path}{filename}', 'w', encoding='UTF-8') as file:
                        file.write(file_content)
                        file.close()

                print(f'Updated {filename}')

        except FileNotFoundError:
            print('No config_files files found')


        # --------------------------- Update Service Files --------------------------- #
        services = []

        try:
            file_path = f'{settings.BASE_DIR}/{project_name}/service_files'

            for filename in os.listdir(file_path):
                with open(os.path.join(file_path, filename), 'r', encoding='UTF-8') as file:
                    file_content = file.read()
                    file.close()

                deploy_path = '/etc/systemd/system/'

                # Create service file if it does not exist
                with subprocess.Popen(['touch', f'{deploy_path}{filename}']) as script:
                    print(script)

                # Update service file to match
                with open(f'{deploy_path}{filename}', encoding='UTF-8') as file:
                    file_content_old = file.read()
                    file.close()

                if file_content != file_content_old:
                    with(open(f'{deploy_path}{filename}.old', 'w', encoding='UTF-8')) as file:
                        file.write(file_content_old)
                        file.close()

                    with open(f'{deploy_path}{filename}', 'w', encoding='UTF-8') as file:
                        file.write(file_content)
                        file.close()

                services.append(filename)
                print(f'Updated {filename}')

        except FileNotFoundError:
            print('No service_files files found')


        # Reload daemon and start services
        try:
            for service in services:
                os.system('systemctl daemon-reload')
                os.system(f'systemctl start {service}')
                os.system(f'systemctl enable {service}')
                os.system(f'systemctl restart {service}')
                # os.system('systemctl status *')

            if nginx:
                ngx = '/etc/nginx/sites-'
                if not os.path.exists(f'{ngx}enabled/{project_name}'):
                    os.system(f'ln -s {ngx}available/{project_name} {ngx}enabled/{project_name}')
                os.system('systemctl restart nginx')

        except SystemError:
            print('No services found')
