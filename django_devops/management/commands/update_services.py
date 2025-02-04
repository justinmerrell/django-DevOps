''' Deploys configuration and services for the application '''

import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand

from django_devops.utils.logger import log


CONFIG_DIR = '/etc/conf.d'
NGINX_SITES_AVAILABLE = '/etc/nginx/sites-available'
NGINX_SITES_ENABLED = '/etc/nginx/sites-enabled'
SYSTEMD_DIR = '/etc/systemd/system'

def ensure_directory_exists(dir_path: str) -> None:
    """
    Ensure a directory exists, creating it if needed.
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        log(f"Created directory: {dir_path}", "INFO")

def deploy_file(src_path: str, dst_path: str) -> bool:
    """
    Deploys a single file from src_path to dst_path.
    Backs up the old version to dst_path + '.old' if content differs.
    Returns True if the file was updated, False otherwise.
    """
    # Read new content
    try:
        with open(src_path, 'r', encoding='UTF-8') as src_file:
            new_content = src_file.read()
    except FileNotFoundError:
        log(f"Source file not found: {src_path}", "WARNING")
        return False

    # Read existing content (if any)
    try:
        with open(dst_path, 'r', encoding='UTF-8') as dst_file:
            old_content = dst_file.read()
    except FileNotFoundError:
        old_content = ""

    # Compare and update if different
    if new_content != old_content:
        # Make a backup
        if old_content:
            backup_path = dst_path + '.old'
            with open(backup_path, 'w', encoding='UTF-8') as backup_file:
                backup_file.write(old_content)
            log(f"Backed up old file to {backup_path}", "INFO")

        # Ensure the file exists (like touch) and write new content
        with open(dst_path, 'w', encoding='UTF-8') as dst_file:
            dst_file.write(new_content)
        log(f"Updated file: {dst_path}", "INFO")
        return True

    # If no change, do nothing
    log(f"No changes for {dst_path}", "INFO")
    return False

def manage_systemd_services(services: list) -> None:
    """
    Reloads systemd daemons and restarts/enables each service in the given list.
    Raises subprocess.CalledProcessError if systemctl commands fail.
    """
    if not services:
        log("No services to manage.", "INFO")
        return

    # Reload once for all changes
    subprocess.run(['systemctl', 'daemon-reload'], check=True)

    for service in services:
        subprocess.run(['systemctl', 'enable', service], check=True)
        subprocess.run(['systemctl', 'restart', service], check=True)
        log(f"Enabled and restarted {service}", "INFO")

class Command(BaseCommand):
    '''
    Checks that configuration and service files exist and have not been deployed before deploying
    '''

    help = 'Deploys configuration and services for the application'

    def handle(self, *args, **options):
        '''
        Deploys configuration and services for the application
        '''
        project_name = os.path.basename(os.path.normpath(settings.BASE_DIR))
        config_files_path = os.path.join(settings.BASE_DIR, project_name, 'config_files')
        service_files_path = os.path.join(settings.BASE_DIR, project_name, 'service_files')

        # Ensure config directory exists
        ensure_directory_exists(CONFIG_DIR)

        # Flag to know if we found a project-specific (Nginx) config
        nginx_project_config_deployed = False

       # ---------------------------- Update Config Files --------------------------- #
        if os.path.isdir(config_files_path):
            for filename in os.listdir(config_files_path):
                src_file = os.path.join(config_files_path, filename)

                # If the filename matches the project, treat it as Nginx config
                if filename == project_name:
                    nginx_project_config_deployed = True
                    dst_path = os.path.join(NGINX_SITES_AVAILABLE, filename)
                else:
                    dst_path = os.path.join(CONFIG_DIR, filename)

                # "Touch" the file by simply opening in append mode if it doesn't exist
                if not os.path.exists(dst_path):
                    with open(dst_path, 'a', encoding='UTF-8'):
                        pass

                deploy_file(src_file, dst_path)
        else:
            self.stdout.write(self.style.WARNING("No config_files directory found."))

        # --------------------------- Update Service Files --------------------------- #
        services = []
        if os.path.isdir(service_files_path):
            for filename in os.listdir(service_files_path):
                src_file = os.path.join(service_files_path, filename)
                dst_file = os.path.join(SYSTEMD_DIR, filename)

                if not os.path.exists(dst_file):
                    with open(dst_file, 'a', encoding='UTF-8'):
                        pass

                deploy_file(src_file, dst_file)
                services.append(filename)
        else:
            self.stdout.write(self.style.WARNING("No service_files directory found."))

        # --------------------------- Reload and Start Services --------------------------- #
        if services:
            try:
                manage_systemd_services(services)
                self.stdout.write(self.style.SUCCESS("-- Services Updated and Restarted --"))
            except subprocess.CalledProcessError as err:
                self.stderr.write(self.style.ERROR(f"Error managing systemd services: {err}"))
        else:
            self.stdout.write("No services to reload or restart.")

        # --------------------------- Handle Nginx --------------------------- #
        if nginx_project_config_deployed:
            # Link site if not already enabled
            available_path = os.path.join(NGINX_SITES_AVAILABLE, project_name)
            enabled_path = os.path.join(NGINX_SITES_ENABLED, project_name)

            if not os.path.exists(enabled_path) and os.path.exists(available_path):
                try:
                    subprocess.run(['ln', '-s', available_path, enabled_path], check=True)
                    log(f"Linked {available_path} to {enabled_path}", "INFO")
                except subprocess.CalledProcessError as err:
                    self.stderr.write(self.style.ERROR(f"Error linking Nginx config: {err}"))

                # Restart Nginx to load the new site
                try:
                    subprocess.run(['systemctl', 'restart', 'nginx'], check=True)
                    log("Nginx restarted", "INFO")
                except subprocess.CalledProcessError as err:
                    self.stderr.write(self.style.ERROR(f"Error restarting Nginx: {err}"))
            else:
                log(f"Enabled Nginx site: {project_name}", "INFO")
        else:
            log("No project-specific Nginx config file found.", "INFO")
