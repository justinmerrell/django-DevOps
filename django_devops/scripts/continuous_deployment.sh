#!/bin/bash

dir_path=$1
log_file="update_log_$(date +%Y%m%d_%H%M%S).log"

exec 3>&1 1>>"$log_file" 2>&1

function log_error() {
    echo "Error on line $1" >&3
    exit 1
}

trap 'log_error $LINENO' ERR


# ---------------------------------------------------------------------------- #
#                                Update Packages                               #
# ---------------------------------------------------------------------------- #

# Git
echo "Updating from git repository..."
git pull --no-edit

# PIP
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install or Update Required Packages
echo "Installing and updating required packages..."
pip3 install --force-reinstall --upgrade --upgrade-strategy=only-if-needed -r requirements.txt

# Pulls the latest code from GitHub, performs the required steps then deploys.


echo "Collecting static files..."
python3 "$dir_path"/manage.py collectstatic --noinput

echo "Applying migrations..."
python3 "$dir_path"/manage.py migrate


# ---------------------------------------------------------------------------- #
#                                Update Services                               #
# ---------------------------------------------------------------------------- #


echo "Updating services..."
python3 "$dir_path"/manage.py update_services


# ---------------------------------------------------------------------------- #
#                               Restart Services                               #
# ---------------------------------------------------------------------------- #

echo "Restarting gunicorn..."
systemctl restart gunicorn

echo "Update completed successfully." >&3
