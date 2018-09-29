from django.core.management.base import BaseCommand, CommandError
from apps.vm.models import VmInfo,VmLog
from apps.vm.fun import comments
from vm_web.settings import HOST

class Command(BaseCommand):
    help = '功能：更新虚拟机运行状态'

    def check_error(self, content, kvm):
        if len(content) == 1:  # 当查询数据为1个时，验证返回的是否是报错信息
            if 'Authentication failed' in content[0]:
                self.stdout.write(self.style.ERROR('check_status ERROR:%s远程连接失败，用户验证不通过!' % kvm))
                return 1
            elif 'Unable to connect' in content[0]:
                self.stdout.write(self.style.ERROR('check_status ERROR:无法连接%s，端口错误或服务器未开启!' % kvm))
                return 1
            elif 'timed out' in content[0]:
                self.stdout.write(self.style.ERROR('check_status ERROR:%s远程连接超时!' % kvm))
                return 1
        if len(content) <= 3:  # 当查询数据过少时，验证是否至少有1个数据正常
            num = 0
            for name in content:
                rows = VmInfo.objects.filter(host=kvm, name=name)
                if rows:
                    num += 1
            if num == 0:
                self.stdout.write(self.style.ERROR('check_status ERROR:查询异常!'))
                return 1
        return 0

    def handle(self, *args, **options):
        host = HOST

        for kvm in host.keys():
            all_list = comments.search_vm(host[kvm])
            if self.check_error(all_list,kvm):
                continue
            on_list = comments.search_vm(host[kvm], 'on')
            off_list = comments.search_vm(host[kvm], 'off')
            vm = VmInfo.objects.filter(host=kvm)
            for obj in vm:
                if obj.name in on_list:
                    if obj.status != '运行中':
                        obj.status = '运行中'
                        obj.save()
                        msg = '%s的%s状态异常，已修正为 "运行中" !' % (kvm, obj.name)
                        self.stdout.write(self.style.SUCCESS(msg))
                        VmLog.objects.create(type='Check', content=msg, created_by='System', ip='127.0.0.1')
                elif obj.name in off_list:
                    if obj.status != '关闭':
                        obj.status = '关闭'
                        obj.save()
                        msg = '%s的%s状态异常，已修正为 "关闭" !' % (kvm, obj.name)
                        self.stdout.write(self.style.SUCCESS(msg))
                        VmLog.objects.create(type='Check', content=msg, created_by='System', ip='127.0.0.1')
                elif obj.name not in all_list:
                    if obj.status != '不存在':
                        obj.status = '不存在'
                        obj.save()
                        msg = '%s的%s状态异常，已修正为 "不存在" !' % (kvm, obj.name)
                        self.stdout.write(self.style.SUCCESS(msg))
                        VmLog.objects.create(type='Check', content=msg, created_by='System', ip='127.0.0.1')


