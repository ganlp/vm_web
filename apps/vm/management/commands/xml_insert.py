from django.core.management.base import BaseCommand
from apps.vm.models import VmHardware
from apps.vm.fun.sshconn import SSH
from vm_web.settings import HOST
import re
import xml.etree.ElementTree as ET
import time


class Command(BaseCommand):
    help = '功能：获取远程xml文件解析后写入db'

    def handle(self, *args, **options):
        then = time.time()
        host = HOST

        #VmHardware.objects.all().delete()  # 清空VmHardware，全部重新添加
        for kvm in host.keys():
            cmd = 'stat -c %n---%Y /etc/libvirt/qemu/*.xml'
            files = SSH.conn1(cmd,host[kvm])
            names = re.findall(r'(?<=/etc/libvirt/qemu/).+(?=---)',files)
            modify = re.findall(r'(?<=\.xml---)\d+',files)
            vm = []
            for i,j in zip(names,modify):
                data = {"host": kvm,
                        "name": "",
                        "uuid": "",
                        "description": "",
                        "memory": "",
                        "vcpu": "",
                        "storage": "",
                        "network": "",
                        "modified_time": j}
                vm.append({i: data})

            file_names = ''
            for i in names:
                file_names += './'+ i + ' '
            cmd = 'cd /etc/libvirt/qemu/; cat %s' % file_names
            xml_data = SSH.conn1(cmd,host[kvm])
            xml_list = re.findall(r'<domain.*?</domain>?',xml_data,re.S)
            if len(xml_list) != len(names):
                self.stdout.write(self.style.ERROR('xml_insert ERROR:%s中，xml文件数和xml数据不对应!' % kvm))
                continue
            if len(xml_list) == 0:
                self.stdout.write(self.style.ERROR('xml_insert ERROR:%s查询数据异常!' % kvm))
                continue

            for i,j,k in zip(xml_list,names,vm):
                root = ET.fromstring(i)
                name = root.find('name').text  # 虚拟机名称
                uuid = root.find('uuid').text  # uuid
                description = root.find('description').text if 'description' in i else ''  # 描述
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
                        size = SSH.conn1(cmd, host[kvm], timeout=10)
                        if size.isdigit():
                            i['storage_size'] = size
                        else:
                            i['storage_size'] = 'Unknown'  # 可能磁盘文件不存在了
                network = []  # 网络设备
                interface = root.find('devices').findall('interface')
                for i in interface:
                    network.append({'mac': i.find('mac').get('address'),
                                    'source_device': i.find('source').attrib,
                                    'device_model': (
                                        i.find('model').get('type') if i.find(
                                            'model') is not None else 'Hypervisor default')})
                data = {"name": name,
                        "uuid": uuid,
                        "description": description,
                        "memory": memory,
                        "vcpu": vcpu,
                        "storage": storage,
                        "network": network}

                k[j].update(data)

            insert_list = []
            i = 0
            for data in vm:
                xml_name = list(data.keys())[0]
                if not VmHardware.objects.filter(xml=xml_name,host=data[xml_name]['host']):
                    insert_list.append(VmHardware(host=data[xml_name]['host'],
                                                  xml=xml_name,
                                                  domain=data[xml_name]['name'],
                                                  uuid=data[xml_name]['uuid'],
                                                  description=data[xml_name]['description'],
                                                  memory=data[xml_name]['memory'],
                                                  vcpu=data[xml_name]['vcpu'],
                                                  storage=data[xml_name]['storage'],
                                                  network=data[xml_name]['network'],
                                                  modified_time=data[xml_name]['modified_time']))
                    i += 1
            VmHardware.objects.bulk_create(insert_list)
            if i >0:
                self.stdout.write(self.style.SUCCESS('从%s插入了%s条新数据！' % (kvm, i)))
                from apps.vm.models import VmLog
                msg = 'VmHardware: 从%s插入了%s条新数据！' % (kvm,i)
                VmLog.objects.create(type='Check', content=msg, created_by='System', ip='127.0.0.1')
        interval = time.time() - then
        msg = '耗时 %.3f秒!' % interval if interval < 180 else '耗时 %d分%d秒!' % (interval/60, interval%60)
        #self.stdout.write(self.style.SUCCESS(msg))














