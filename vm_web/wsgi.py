"""
WSGI config for vm_web project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os
from multiprocessing import Process
from django.core.wsgi import get_wsgi_application
from . import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vm_web.settings')

application = get_wsgi_application()

# -----------------------------------------------------
def worker():
    '''
        Multi process service VNC start
    '''
    dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'apps', 'vnc')

    websockify_path = os.path.join(dir_path, 'websockify', 'websockify.py')
    web_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    target_path = os.path.join(dir_path, 'vm_token')

    cmd = 'python3 %s --web=%s --target-config=%s %s' %(websockify_path, web_path, target_path, settings.VNC_PROXY_PORT)
    print(cmd)
    os.system(cmd)

def start_websockify():
    '''
        Start the VNC agent service
        ./utils/websockify/websockify --web=. --target-config=vnc_tokens 6080
    '''

    print('start vnc proxy..')

    t = Process(target=worker, args=())
    t.start()

    print('vnc proxy started..')

start_websockify()
