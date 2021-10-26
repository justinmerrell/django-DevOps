''' Deploys configuration and services for the application '''

import os

from django.core.management.base import BaseCommand

from django.conf import settings

class Command(BaseCommand):
    '''Checks that configuration and service files exsist and have not beeen deployed before deploying.'''

    help = 'Deploys configuration and services for the application'

    def handle(self, *args, **options):
        '''
        Deploys configuration and services for the application
        '''

        # Check if /etc/conf.d/ directory exists
        if not os.path.exists('/etc/conf.d'):
            os.makedirs('/etc/conf.d')

        # Update config files
        try:
            project_name = os.path.basename(os.path.normpath(settings.BASE_DIR))

            for filename in os.listdir(f'{settings.BASE_DIR}/{project_name}/config_files'):
                with open(os.path.join(f'{settings.BASE_DIR}/{project_name}/config_files', filename), 'r') as file:
                    file_content = file.read()
                    file.close()

                # Update config file to match
                with open(f'/etc/conf.d/{filename}') as file:
                    file_content_old = file.read()
                    file.close()

                if file_content != file_content_old:
                    with(open(f'/etc/conf.d/{filename}.old', 'w')) as file:
                        file.write(file_content_old)
                        file.close()

                    with open(f'/etc/conf.d/{filename}', 'w') as file:
                        file.write(file_content)
                        file.close()

                print(f'Updated {filename}')

        except Exception as err:
            print(err)


        # Update service files
        services = []

        try:
            for filename in os.listdir(f'{settings.BASE_DIR}/{project_name}/service_files'):
                with open(os.path.join(f'{settings.BASE_DIR}/{project_name}/service_files', filename), 'r') as file:
                    file_content = file.read()
                    file.close()

                # Update service file to match
                with open(f'/etc/systemd/system/{filename}') as file:
                    file_content_old = file.read()
                    file.close()

                if file_content != file_content_old:
                    with(open(f'/etc/systemd/system/{filename}.old', 'w')) as file:
                        file.write(file_content_old)
                        file.close()

                    with open(f'/etc/systemd/system/{filename}', 'w') as file:
                        file.write(file_content)
                        file.close()

                services.append(filename)
                print(f'Updated {filename}')

        except Exception as err:
            print(err)


        # Reload daemon and start services
        try:
            for service in services:
                os.system('systemctl daemon-reload')
                os.system(f'systemctl start {service}')
                os.system(f'systemctl enable {service}')
                os.system(f'systemctl restart {service}')
                # os.system('systemctl status *')

        except Exception as err:
            print(err)
