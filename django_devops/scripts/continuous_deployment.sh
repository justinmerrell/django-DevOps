#!/bin/bash

dir_path=$1

# ---------------------------------------------------------------------------- #
#                                Update Packages                               #
# ---------------------------------------------------------------------------- #

git pull --no-edit

# PIP
python3 -m pip install --upgrade pip

# Install or Update Required Packages
pip3 install --force-reinstall --upgrade --upgrade-strategy=only-if-needed -r requirements.txt

# Pulls the latest code from GitHub, performs the required steps then deploys.


python3 "$dir_path"/manage.py collectstatic --noinput
python3 "$dir_path"/manage.py migrate


# ---------------------------------------------------------------------------- #
#                                Update Services                               #
# ---------------------------------------------------------------------------- #

python3 "$dir_path"/manage.py update_services

# ---------------------------------------------------------------------------- #
#                               Restart Services                               #
# ---------------------------------------------------------------------------- #
systemctl restart gunicorn
