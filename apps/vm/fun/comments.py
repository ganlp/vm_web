# -*- coding: utf-8 -*-
from .sshconn import SSH
from vm_web.settings import HOST
#from sshconn import SSH

def search_vm(host, status='all'):
    cmd1 = 'virsh list | grep run | awk \'{ print $2 }\''
    cmd2 = 'virsh list --all | egrep "shut|关闭" | awk \'{ print $2 }\''
    cmd3 = 'virsh list --all | egrep "run|shut|关闭" | awk \'{ print $2 }\''
    if status == 'all':
        return SSH.conn1(cmd3, host).splitlines()
    elif status == 'on':
        return SSH.conn1(cmd1, host).splitlines()
    elif status == 'off':
        return SSH.conn1(cmd2, host).splitlines()
    else:
        raise Exception('Parameter Error:status=[all/on/off]')
    # 虚拟机共有7种状态


def get_vm_ip(host):
    cmd = '''
    sh <<EOF
    #!/bin/bash
    subnet=\`route -n|grep "UG" |awk '{print \$2}'|sed 's/..$//g'\`
    for ip in \$subnet.{1..253};do
    {
    ping -c1 \$ip >/dev/null 2>&1
    }&
    done
    running_vms=\`virsh list |grep running\`
    #echo -ne "共有\`echo "\$running_vms"|wc -l\`个虚拟机在运行.\\n"
    for i in \`echo "\$running_vms" | awk '{ print \$2 }'\`;do
    mac=\`virsh dumpxml \$i |grep "mac address"|sed "s/.*'\(.*\)'.*/\\1/g"\`
    ip=\`arp -ne |grep "\$mac" |awk '{printf \$1}'\`
    printf "%-30s %-30s\\n" \$i \$ip
    done
    EOF
    '''
    ret = SSH.conn1(cmd, host)
    return ret


def running(name, host, option):
    if option == 'on':
        cmd = 'virsh start %s' % name
        succ_msg = ['started', '已开始']
    elif option == 'off':
        cmd = 'virsh destroy %s' % name  # virsh shutdown依赖于acpid
        succ_msg = ['destroyed', '被删除', '被关闭']
    else:
        raise Exception('option参数错误[on/off]')
    ret = SSH.conn1(cmd, host, timeout=8)
    for msg in succ_msg:
        if msg in ret:
            return 0
    return ret


def autostart(name, host, option=None):
    hosts = HOST
    if option:
        cmd = 'virsh autostart %s' % name
    else:
        cmd = 'virsh autostart %s --disable' % name
    ret = SSH.conn1(cmd, hosts[host], timeout=10)
    succ_msg = ['marked', 'unmarked', '标记', '取消标记']
    for msg in succ_msg:
        if msg in ret:
            return 0
    return ret


def show_autostart():
    import re

    hosts = HOST
    cmd = 'if [ -d /etc/libvirt/qemu/autostart/ ];then ls /etc/libvirt/qemu/autostart/; fi'
    name = {}
    err = []
    for kvm, host in hosts.items():
        ret = SSH.conn1(cmd, host, timeout=10)
        if ret and re.match(r'\S+\.xml',ret) is None:
            err.append(kvm)
        else:
            name[kvm]=ret.split()
    return name, err

