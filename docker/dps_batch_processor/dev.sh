#!/bin/sh

watchmedo auto-restart --patterns="*.py" --recursive -d /usr/src python -- docker.py

exec "$@"
