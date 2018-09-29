import paramiko
import time
import sys
import os
from .logs import Log
import re

kvm_logfile = 'kvm.log'

def checkip(ip):
    pingret = os.system('ping ' + ip + ' -c 3')
    if pingret == 0:
        return True
    else:
        return False

@Log.exe_deco
def sshcmd(cmds,host,time_freq=0):
    trans = paramiko.Transport(host[0], 22)
    trans.connect(username=host[1], password=host[2])
    chan = trans.open_session()
    chan.settimeout(200)
    chan.get_pty(width=150,height=32)
    chan.invoke_shell()

    result = ''
    for cmd in cmds:
        chan.send(cmd + '\r')
        if time_freq:
            time.sleep(time_freq)
        then = time.time()
        while True:
            if time.time()-then >(3*chan.gettimeout()): # 防止死循环
                raise TimeoutError('执行 %s 命令期间未能在预期时间内执行完成！' % cmd)
            if chan.recv_ready():
                ret = chan.recv(65535).decode('utf-8',errors='ignore')
                result += ret
                # Log.write_log(ret, monitor.log)
                if 'console' in cmd:
                    if ret.endswith('^]\r\n'):
                        chan.send('\r')
                        continue
                    if ret.endswith('密码：') or ret.endswith('login: ') or ret.endswith('Password: '):
                        break
                else:
                    if ret.endswith(']# ') or ret.endswith(']$ ') or ret.endswith(': '): # 命令执行结束或等待输入
                        break

    trans.close()
    Log.write_log('本组命令的执行结果：\n%s' % result, kvm_logfile)
    return result


def set_network(ipaddr,netmask='255.255.255.0',dns1='192.168.6.93',dns2='114.114.114.114',gateway=None,eth='eth0'):
    path = '/etc/sysconfig/network-scripts/ifcfg-' + eth
    if gateway is None:
        gateway = ipaddr[:ipaddr.rfind('.') + 1] + '1'
    set1 = 'sed -i "/^IPADDR/c IPADDR=%s" %s' % (ipaddr,path)
    set2 = 'sed -i "/^NETMASK/c NETMASK=%s" %s' % (netmask, path)
    set3 = 'sed -i "/^DNS1/c DNS1=%s" %s' % (dns1, path)
    set4 = 'sed -i "/^DNS2/c DNS2=%s" %s' % (dns2, path)
    set5 = 'sed -i "/^GATEWAY/c GATEWAY=%s" %s' % (gateway,path)
    set6 = 'service network restart '
    set7 = 'ntpdate 202.108.6.95'
    return [set1,set2,set3,set4,set5,set6,set7]


@Log.exe_deco
def installiso(isover,host=None):
    if host is None:
        host = ['192.168.18.246', 'root', 'justiso']
    cmd = 'find /data/ -name %s' % isover
    if not checkip(host[0]):
        Log.write_log('ping不通镜像文件服务器的网络！', kvm_logfile)
        return
    findresult = sshcmd([cmd],host,1)
    if findresult is None:
        Log.write_log('查找镜像文件时出错！' ,kvm_logfile)
        raise Exception
    isopath = re.findall(r'^/data/\S*%s\s$' % isover, findresult, re.M)
    filenum = len(isopath)
    if filenum == 0:
        Log.write_log('在 %s 上未找到待安装的iso镜像文件%s!' % (host[0],isover),kvm_logfile)
        raise Exception('iso镜像未找到，不能安装！')
    elif filenum == 1:
        isopath = ''.join(isopath)
    else:
        Log.write_log('在 %s 的多个位置找到该iso镜像文件%s，仅选择找到的第一个!'  % (host[0],isover), kvm_logfile)
        isopath = ''.join(isopath[0])

    install = ['cd /home','wget http://%s%s' % (host[0],isopath), 'tar -zxf %s' % isover,
               'cd %s' % ''.join(re.findall(r'\S+(?=\.tar\.gz)', isover)),
               'nohup ./just_in install just *.jbin >/dev/null 2>&1 &']  #这里不考虑盒子的安装
    return install


@Log.exe_deco
def createvm(newvm,origvm,imgpath,vmip,kvmhost,isover=None):
    clonevm = 'virt-clone -o %s -n %s -f %s' % (origvm,newvm,imgpath)
    #runvm = 'virsh start ' + newvm
    setnetwork = set_network(vmip)
    if 'v70' in origvm:
        console = ['virsh start --console %s' % newvm, 'root', 'adminJUST2015']
    elif 'v80' in origvm:
        console = ['virsh start --console %s' % newvm, 'root', 'justcall']
    else: raise Warning('母盘 %s 不存在!' % origvm)

    Log.write_log('开始在 %s 创建镜像 %s ,并初始化ip为 %s 。' % (kvmhost[0],newvm,vmip), kvm_logfile)
    then = time.time()
    status = sshcmd([clonevm] + console + setnetwork + ['logout'], kvmhost)
    if status is None:
        Log.write_log('虚拟机创建失败，在创建过程中命令执行出错！')
        sshcmd(['virsh undefine %s --storage %s' % (newvm,imgpath), kvmhost])
        raise Exception
    Log.write_log('虚拟机创建完毕!\n', kvm_logfile)

    net_fail = 0 if checkip(vmip) else 1
    if net_fail:
        Log.write_log('新建的虚拟机网络异常，无法ping通！', kvm_logfile)

    if isover is not None and not net_fail:
        Log.write_log('开始安装镜像文件...', kvm_logfile)
        status = sshcmd(installiso(isover),[vmip,console[1],console[2]], 1)
        if status is None:
            Log.write_log('镜像文件安装失败！', kvm_logfile)
            raise Exception
        else:
            Log.write_log('iso镜像文件%s已进行安装,请等待安装，手动查看安装进程是否执行完毕！' % isover, kvm_logfile)

    interval = time.time() - then
    Log.write_log('---------创建脚本已执行完毕,耗时 %d分%d秒!\n'  % (int(interval/60),int(interval%60)) , kvm_logfile)


if __name__ == '__main__':
    # 母盘：v80clean、v70clean
    # $1 新镜像名称   $2 被克隆母盘名称   $3 新镜像待保存的img文件
    # $4 新镜像的IP   $5 kvm主机信息([ip,user,passwd])
    createvm(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    #createvm('v80-20180511-IM-hur','v80clean','/home/vhost/v80-20180511-IM-hur.img','192.168.18.199',['192.168.18.15','root','justkvmtest'])

