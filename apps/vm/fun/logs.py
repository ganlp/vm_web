import time
import os
import sys


class Log:
    @staticmethod
    def write_log(msg,filename='run.log'):
        # 写入一个文件
        filePath = os.path.abspath(os.path.dirname(__file__))
        logFilePath = os.path.join(filePath, filename)
        execTime = time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
        if isinstance(msg,int):
            msg = str(msg)
        open(logFilePath, 'at', encoding='utf-8').write(execTime + ' ' + msg + '\n')

    @staticmethod
    def exe_deco(func):
        def _deco(*args, **kwargs):
            ret = None
            log = Log()
            try:
                ret = func(*args, **kwargs)
            except Exception as e:
                msg = 'Exception in '+func.__name__+' method: '+str(e)
                log.write_log(msg, 'error.log')
                #print(str(e))
            else:
                log.write_log('No exception in %s method.' % func.__name__, 'error.log')
            finally:
                return ret
        return _deco
