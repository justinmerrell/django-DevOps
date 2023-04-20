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


def generate_file(file_path, file_template):
    '''
    Generates a file from a template.
    '''
    if exists(file_path):
        if query_yes_no(f'{file_path} exists. Overwrite?'):
            pass
        else:
            raise CommandError(f'{file_path} will not be overwritten.')

    with open(file_path, 'w+', encoding='UTF-8') as file:
        file.seek(0)
        file.write(dedent(file_template))
        file.truncate()


def create_and_set_permissions(directory, owner, group):
    '''
    Creates a directory and sets the owner and group.
    '''
    if not exists(directory):
        os.makedirs(directory)
        os.system(f'chown -R {owner}:{group} {directory}')


class Command(BaseCommand):
    '''
    Programmatically generates the service file for celery.
    '''

    help = 'PProgrammatically generates the service file for celery.'

    def handle(self, *args, **options):
        '''
        Verifies that the service folder exists for use with django_devops
        '''
        service_files_path = f'{settings.BASE_DIR}/{PROJECT_NAME}/service_files'
        config_files_path = f'{settings.BASE_DIR}/{PROJECT_NAME}/config_files'

        if not exists(service_files_path):
            raise CommandError(f'''
                {service_files_path} does not exist.
                First run "python manage.py devops" to configure django_devops.
            ''')

        # Generate celery.service file.
        celery_service_template = f'''
            [Unit]
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
                            --pidfile=${{CELERYD_PID_FILE}}'

            ExecReload  =   /bin/sh -c '/opt/{PROJECT_NAME}/env/bin/celery ${{CELERY_BIN}} multi restart ${{CELERYD_NODES}} \
                            -A ${{CELERY_APP}} --pidfile=${{CELERYD_PID_FILE}} \
                            --logfile=${{CELERYD_LOG_FILE}} --loglevel=${{CELERYD_LOG_LEVEL}} $CELERYD_OPTS'

            Restart=always

            [Install]
            WantedBy = multi-user.target
        '''

        # Generate celery.service file.
        celery_config_template = f'''
            # Name of nodes to start.
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

        generate_file(f'{service_files_path}/celery.service', celery_service_template)
        generate_file(f'{config_files_path}/celery', celery_config_template)

        create_and_set_permissions('/var/run/celery/', PROJECT_NAME, PROJECT_NAME)
        create_and_set_permissions('/var/log/celery/', PROJECT_NAME, PROJECT_NAME)
