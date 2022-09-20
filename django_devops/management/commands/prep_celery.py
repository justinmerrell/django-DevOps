'''
A programatic way to prepare and configure celery.
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
    Programmatically generates the service file for celery.
    '''

    help = 'PProgrammatically generates the service file for celery.'

    def handle(self, *args, **options):
        '''
        Verifies that the service folder exists for use with django_devops
        '''
        if not exists(f'{settings.BASE_DIR}/{PROJECT_NAME}/service_files'):
            raise CommandError(f'''
                        {settings.BASE_DIR}/{PROJECT_NAME}/service_files does not exist.
                        First run "python manage.py devops" to configure django_devops.
                    ''')

        # Check if the service file exists and confirm overwrite.
        if exists(f'{settings.BASE_DIR}/{PROJECT_NAME}/service_files/celery.service'):
            if query_yes_no(f'{PROJECT_NAME}/service_files/celery.service exists. Overwrite?'):
                pass
            else:
                raise CommandError(f'''
                            {PROJECT_NAME}/service_files/celery.service will not be overwritten.
                        ''')

        # Generate celery.service file.
        file_template = f'''[Unit]
                            Description = Celery Service
                            After = network.target

                            [Service]
                            Type = forking
                            User = {PROJECT_NAME}
                            Group = {PROJECT_NAME}

                            EnvironmentFile = /etc/conf.d/celery

                            WorkingDirectory = /opt/{PROJECT_NAME}

                            ExecStart   =   /bin/sh -c '/opt/{PROJECT_NAME}/env/bin/celery multi start ${{CELERYD_NODES}} \
                                            -A ${{CELERY_APP}} --pidfile=${{CELERYD_PID_FILE}} \
                                            --logfile=${{CELERYD_LOG_FILE}} --loglevel=${{CELERYD_LOG_LEVEL}} $CELERYD_OPTS'

                            ExecStop    =   /bin/sh -c '/opt/{PROJECT_NAME}/env/bin/celery ${{CELERY_BIN}} multi stopwait ${{CELERYD_NODES}} \
                                            --pidfile=$CELERYD_PID_FILE'

                            ExecReload  =   /bin/sh -c '/opt/{PROJECT_NAME}/env/bin/celery ${{CELERY_BIN}} multi restart ${{CELERYD_NODES}} \
                                            -A ${{CELERY_APP}} --pidfile=${{CELERYD_PID_FILE}} \
                                            --logfile=${{CELERYD_LOG_FILE}} --loglevel=${{CELERYD_LOG_LEVEL}} $CELERYD_OPTS'

                            Restart=always

                            [Install]
                            WantedBy = multi-user.target
                        '''

        file_path = f'{settings.BASE_DIR}/{PROJECT_NAME}/service_files'
        with open(f'{file_path}/celery.service', 'w+', encoding='UTF-8') as file:
            file.seek(0)
            file.write(dedent(file_template))
            file.truncate()

        # Check if the config file exists and confirm overwrite.
        if exists(f'{settings.BASE_DIR}/{PROJECT_NAME}/config_files/celery'):
            if query_yes_no(f'{PROJECT_NAME}/config_files/celery exists. Overwrite?'):
                pass
            else:
                raise CommandError(f'''
                            {PROJECT_NAME}/config_files/celery will not be overwritten.
                        ''')

        # Generate celery.service file.
        file_template = f'''# Name of nodes to start.
                            CELERYD_NODES="worker"

                            CELERY_BIN="/opt/{PROJECT_NAME}/env/bin/celery"

                            CELERY_APP="{PROJECT_NAME}"

                            CELERYD_CHDIR="/opt/{PROJECT_NAME}/"

                            CELERYD_OPTS="--time-limit=300 --concurrency=8"

                            CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
                            CELERYD_PID_FILE="/var/run/celery/%n.pid"

                            # Workers should run as an unprivileged user.
                            #   You need to create this user manually (or you can choose
                            #   a user/group combination that already exists (e.g., nobody).
                            CELERYD_USER="{PROJECT_NAME}"
                            CELERYD_GROUP="{PROJECT_NAME}"
                            CELERYD_LOG_LEVEL="INFO"

                            # If enabled PID and log directories will be created if missing,
                            # and owned by the userid/group configured.
                            CELERY_CREATE_DIRS=1


                            CELERYBEAT_PID_FILE="/var/run/celery/beat.pid"
                            CELERYBEAT_LOG_FILE="/var/log/celery/beat.log"
                        '''

        file_path = f'{settings.BASE_DIR}/{PROJECT_NAME}/config_files'
        with open(f'{file_path}/celery', 'w+', encoding='UTF-8') as file:
            file.seek(0)
            file.write(dedent(file_template))
            file.truncate()

        # Generate directories for celery.
        if not exists('/var/run/celery/'):
            os.makedirs('/var/run/celery/')
            os.system(f'chown -R {PROJECT_NAME}:{PROJECT_NAME} /var/run/celery/')

        if not exists('/var/log/celery/'):
            os.makedirs('/var/log/celery/')
            os.system('chown -R {PROJECT_NAME}:{PROJECT_NAME} /var/log/celery')
