#!/bin/bash

dir_path=$1

# ---------------------------------------------------------------------------- #
#                            System Update/Updgrade                            #
# ---------------------------------------------------------------------------- #

sudo apt-get update -y && sudo apt-get upgrade -y &

# ---------------------------------------------------------------------------- #
#                                Update Packages                               #
# ---------------------------------------------------------------------------- #

# PIP
python3 -m pip install --upgrade pip

# Django
python3 -m pip install -U Django

# Install or Update Required Packages
pip3 install --force-reinstall --upgrade -r requirements.txt

# Pulls the latest code from GitHub, performs the required steps then deploys.

git pull --no-edit
python3 "$dir_path"/manage.py collectstatic --noinput --clear
python3 "$dir_path"/manage.py migrate


# ---------------------------------------------------------------------------- #
#                                Update Services                               #
# ---------------------------------------------------------------------------- #

python3 "$dir_path"/manage.py update_services

# ---------------------------------------------------------------------------- #
#                               Restart Services                               #
# ---------------------------------------------------------------------------- #
systemctl restart gunicorn
