import paramiko
import time


class SSH:
    @staticmethod
    def conn1(comm, host, timeout=300):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        result = None
        try:
            ssh.connect(hostname=host[0], port=22, username=host[1], password=host[2], timeout=timeout)
            stdin, stdout, stderr = ssh.exec_command(comm)
            result = stdout.read().decode('utf-8-sig')
            if not result.strip():
                result = stderr.read().decode('utf-8-sig')
        except Exception as e:
            result = str(e)

        finally:
            ssh.close()
            return result.strip()

    @staticmethod
    def conn2(cmd,host,time_freq=0):
        trans = paramiko.Transport(host[0], 22)
        trans.connect(username=host[1], password=host[2])
        chan = trans.open_session(timeout=20)

        chan.exec_command(cmd)
        result = ''
        # TODO 如果输入错误命令或没标准输出的命令，会无限循环
        while True:
            if chan.recv_ready():
                result += chan.recv(65535).decode()
                time.sleep(0.1)
                if not chan.recv_ready():
                    #chan.recv_exit_status()    # TODO 会一直等待命令状态返回（命令执行结束），如果输出内容太多导致无限挂起怎办？
                    #result += chan.recv(65535).decode()
                    break
        trans.close()
        return result

    @staticmethod
    def conn3(cmds,host,time_freq=0):
        trans = paramiko.Transport(host[0], 22)
        trans.connect(username=host[1], password=host[2])
        chan = trans.open_session()
        chan.settimeout(30)
        chan.get_pty(width=150,height=32)
        chan.invoke_shell()

        result = ''
        for cmd in cmds:
            chan.send(cmd + '\r')
            if time_freq:
                time.sleep(time_freq)
            then = time.time()
            while True:
                if time.time()-then >(2*chan.gettimeout()): # 防止死循环
                    break
                if chan.recv_ready():
                    ret = chan.recv(65535).decode('utf-8-sig')
                    result += ret
                    if ret.endswith(']# ') or ret.endswith(']$ ') or ret.endswith(': '): # 命令执行结束或等待输入
                       break


        trans.close()
        return result