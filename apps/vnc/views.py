from django.shortcuts import render, HttpResponse
from django.conf import settings
import uuid, re
from .fun import graphics,functions
from apps.vm.models import VmInfo

def run_vnc(request):

    if request.GET:
        vm_id = request.GET.get('id')
    else:
        return HttpResponse('错误，页面未找到。')

    host = settings.VNC_PROXY_SERVER_ADDRESS
    port = settings.VNC_PROXY_PORT
    obj = VmInfo.objects.get(id=vm_id)
    vm_ip = obj.ip if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',obj.ip) else 'unknown'

    getVNC = graphics.vnc_display(obj.host, obj.name)
    if getVNC['success']:
        if getVNC['data']['listen'] != '0.0.0.0':
            return HttpResponse(
                '目前服务器对该虚拟机的监听地址限制为%s！' % getVNC['data']['listen'])
        else:
            token = uuid.uuid3(uuid.uuid1(), obj.name)
            graphics.write_tokenfile(token, obj.host, getVNC['data']['port'])
            data = {'host': host,
                    'port': port,
                    'password': '',
                    'path': 'websockify/?token=%s' % token,
                    'ip': vm_ip,
                    'kvm': obj.host,
                    'vm_name': obj.name,
                    'etime': functions.get_etime(obj.host, obj.name)}
            return render(request, 'console.html', data)
    else:
        return HttpResponse(getVNC['message'])
