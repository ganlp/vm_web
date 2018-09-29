#!/bin/sh
python3 /data/vm_web/manage.py runserver --noreload 0.0.0.0:789 >>/opt/djangorun.log 2>&1 &
