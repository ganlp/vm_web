from django.core.management.base import BaseCommand
from apps.vm.models import VmHardware
from apps.vm.fun.sshconn import SSH
from vm_web.settings import HOST
import re
import time


class Command(BaseCommand):
    help = '功能：根据远程的xml文件最后修改时间更新VmHardware数据'


    def get_xmldata(self,name, host):
        # 获取服务器上单个xml文件并解析

        import xml.etree.ElementTree as ET
        cmd = 'if [ -f /etc/libvirt/qemu/%s ];then cat /etc/libvirt/qemu/%s; fi' % (name, name)
        ret = SSH.conn1(cmd, host, timeout=10)
        if ret:
            root = ET.fromstring(ret)
            domain = root.find('name').text  # 虚拟机名称
            uuid = root.find('uuid').text  # uuid
            description = root.find('description').text if 'description' in ret else ''  # 描述
            memory = root.find('memory').text  # 内存
            vcpu = root.find('vcpu').text  # vcpu
            storage = []  # 存储设备
            disk = root.find('devices').findall('disk')
            for i in disk:
                storage.append({'device': i.get('device'),
                                'storage_format': i.find('driver').get('type'),
                                'source_path': (
                                    i.find('source').get('file', default=i.find('source').get('dev')) if i.find(
                                        'source') is not None else '-'),
                                'dev': i.find('target').get('dev'),
                                'disk_bus': i.find('target').get('bus'),
                                'storage_size': '-',
                                'readonly': ('yes' if i.find('readonly') is not None else 'no'),
                                'shareable': ('yes' if i.find('shareable') is not None else 'no')})
            for i in storage:
                if i['device'] == 'disk' and i['source_path'] != '-':
                    cmd = 'stat -c %%s %s' % i['source_path']
                    size = SSH.conn1(cmd, host, timeout=10)
                    if size.isdigit():
                        i['storage_size'] = size
                    else:
                        i['storage_size'] = 'Unknown'  # 可能磁盘文件被删了
            network = []  # 网络设备
            interface = root.find('devices').findall('interface')
            for i in interface:
                network.append({'mac': i.find('mac').get('address'),
                                'source_device': i.find('source').attrib,
                                'device_model': (
                                    i.find('model').get('type') if i.find(
                                        'model') is not None else 'Hypervisor default')})
            data = {"domain": domain,
                    "uuid": uuid,
                    "description": description,
                    "memory": memory,
                    "vcpu": vcpu,
                    "storage": storage,
                    "network": network}
            return data
        else:
            raise Exception('没找到xml文件')

    def handle(self, *args, **options):
        then = time.time()
        host = HOST
        for kvm in host.keys():
            cmd = 'stat -c %n---%Y /etc/libvirt/qemu/*.xml'
            files = SSH.conn1(cmd, host[kvm])
            names = re.findall(r'(?<=/etc/libvirt/qemu/).+(?=---)', files)
            modify = re.findall(r'(?<=\.xml---)\d+', files)
            if len(names) != len(modify):
                self.stdout.write(self.style.ERROR('xml_update ERROR:%s的xml文件名和最后修改时间没有一一对应' % kvm))
                continue
            if len(names) == 0:
                self.stdout.write(self.style.ERROR('xml_update ERROR:%s查询数据异常' % kvm))
                continue
            modify = map(int,modify)
            i = 0
            for name,mtime in zip(names,modify):
                obj = VmHardware.objects.filter(xml=name, host=kvm)
                if obj:
                    if obj.first().modified_time != mtime:
                        data = self.get_xmldata(name,host[kvm])
                        obj.update(domain=data['domain'], uuid=data['uuid'], description=data['description'],
                                   memory=data['memory'], vcpu=data['vcpu'], storage=data['storage'],
                                   network=data['network'], modified_time=mtime)
                        #print('%s的%s被更新。' % (kvm, name))
                        i += 1

            if i > 0:
                self.stdout.write(self.style.SUCCESS('从%s更新了%s条数据！' % (kvm, i)))
                from apps.vm.models import VmLog
                msg = 'VmHardware: 从%s更新了%s条数据！' % (kvm,i)
                VmLog.objects.create(type='Check', content=msg, created_by='System', ip='127.0.0.1')
        interval = time.time() - then
        msg = '耗时 %.3f秒!' % interval if interval < 180 else '耗时 %d分%d秒!' % (
            int(interval / 60), int(interval % 60))
        #self.stdout.write(self.style.SUCCESS(msg))










