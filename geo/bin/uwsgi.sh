#! /usr/bin/env sh

uwsgi --http :5000 --wsgi-file /home/web/pygeo/geo/__init__.py --callable app --processes 2 --threads 4