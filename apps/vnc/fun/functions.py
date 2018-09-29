from apps.vm.fun.sshconn import SSH
from vm_web.settings import HOST
import re


def get_etime(kvm, name):
    # 直接打印秒数
    # cmd = "ps -eo etime,cmd | grep '%s' | grep -v grep | awk 'BEGIN{split(\"1,60,3600,86400\",a,\",\");}NR==1 && NF=1{n=split($1,b,\":|-\");for(i=n;i>=1;i--)c+=b[i]*a[n-i+1];$1=c;c=0;print}'" % name
    # 打印 [[dd-]hh:]mm:ss
    cmd = "ps -eo etime,cmd | grep 'qemu-kvm -name %s ' | grep -v grep | awk '{print $1}'" % name  # 注意%s后面有空格，防止有相似的名字
    result = SSH.conn1(cmd,HOST[kvm],1) # 1秒超时，防止页面响应时间过长
    etime = {'second': 0, 'minute': 0, 'hour': 0, 'day': 0}
    if re.match(r'\d+[-:]\d+',result):
        date = re.split('[:-]',result)
        for t, key in zip(reversed(date), etime.keys()):
            if t:
                etime[key] = int(t)
    #else:
    #    return 'unknown'
    return etime