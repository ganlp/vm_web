from apps.vm.fun.sshconn import SSH
from vm_web.settings import HOST
import re
from os import path


def vnc_display(kvm,name):
    cmd = 'virsh vncdisplay %s' % name
    host = HOST
    result = SSH.conn1(cmd,host[kvm],timeout=5)
    if 'error' in result or '错误' in result:
        return { "success": 0, "message": result, "data": {}}
    listen, port = re.split(r':', result)
    if not listen:
        listen = '0.0.0.0'
    port = int(port) + 5900
    return { "success": 1, "message": result, "data": {"listen":listen, "port":port}}

def write_tokenfile(token, kvm, port):
    ip = HOST[kvm][0]
    text = '%s: %s:%s' % (token, ip, port)
    tokenfile = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'vm_token', 'token.conf')
    with open(tokenfile, 'w') as f: # 临时写，不保存token
        f.write(text)
