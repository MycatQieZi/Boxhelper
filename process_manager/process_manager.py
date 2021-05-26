'''
该程序是为了实现进程模块的相关功能，进程相关模块主要包括以下几个方面

- 查看进程状态
    - freeswitch
    - docker
    - 818project

- 获取进程的输出日志
    - docker内容器的输出日志
    - fs_cli的输出日志

- 查看fs的连接状态等信息
    - 集成sofia status
    - 集成reload sofia_mod
    - 集成restart的操作
'''
import os, sys, traceback
import subprocess
import time
import psutil

# try:
#     from subprocess import DEVNULL
# except ImportError:
#     DEVNULL = os.open(os.devnull, os.O_RDWR)

FREESWITCH_PROCESS_KEYWORD = "FreeSwitch"
DOCKER_PROCESS_KEYWORD = "docker"


class ProcessManager:

    def __init__(self):
        bonk = 'bonk'

    def is818Running(self):
        if self.isRunning(DOCKER_PROCESS_KEYWORD):
            hello_info = self.getContainerInfo()
            if hello_info:
                hello_id = hello_info[0]
                hello_name = hello_info[-1]
                return hello_id and hello_name=="hello"

        return False

    def isRunning(self, progress_name):
        '''
        该函数是一个判断函数，返回的是True、False的bool值判断
        输入应该是准确的进程名docker、FreeSwitch
        '''
        #print('tasklist | findstr ' + progress_name)
        #print(os.popen('tasklist | findstr ' + progress_name).readlines())
        # process = len(os.popen('tasklist | findstr ' + progress_name).readlines())
        try:

            # p1 = subprocess.check_output(["tasklist"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            # p2 = subprocess.Popen(["findstr", progress_name], stdin=p1.stdout, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
            # p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
            # output = p2.communicate()[0]
            # print(output)
            # process = len(output)
            process = len(subprocess.check_output(["tasklist", "|", "findstr", progress_name], shell=True, stdin=subprocess.DEVNULL, stderr=subprocess.STDOUT))
        except subprocess.CalledProcessError:
            print(progress_name + " is not running")
            raise
        except Exception:
            raise 
        else:
            if process >= 1:
                print(progress_name + " is running")
                return True
            else: 
                print(progress_name + " is not running")
                return False
       

    def getContainerInfo(self):
        '''
        该函数功能是查看目前的长在运行的容器的ContainerID，没有输入，输出为uContainerID
        '''
        #proc = subprocess.Popen('cmd.exe',creationflags=subprocess.CREATE_NEW_CONSOLE, shell = True, stdout =  subprocess.PIPE)
        #time.sleep(5)
        try:
            proc = subprocess.check_output(["docker", "ps"], shell = True, stdin=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print('check_output on "docker ps" command returned nothing' )
            return None  

        if proc != None:
            result = proc.decode('utf-8')
            result_list = result.split('\n')
            return result_list[1].split(' ') if len(result_list)>=2 else None
        return None

    def getContainerLog(self, containerID, line_count=100):
        '''
        该函数是依据上一个函数得到的ContainerID查看器日志内容并按行输出
        输入：ContainerID
        输出：<list>logs
        '''
        try:
            cmd = ["docker", "logs", "--tail", str(line_count), containerID]
            cmd_test = ['type', 'test.log']
            proc = subprocess.check_output(cmd, shell = True, stdin=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print('check_output on "docker logs %s" command returned nothing' %(containerID) )
            return None
        
        result = proc.decode('utf-8')
        result_list = result.split('\n')
        # for i in result_list:
        #     print(i)
        return result_list
            
    def freeswitchStatus(self):
        '''
        该函数是用来查看本地fs的双向注册状态，即为callbox的注册状态和numconvert的注册状态
        输入：
        输出：<str>callbox注册状态，<str>numconvert注册状态
        '''
        try:
            self.isRunning(FREESWITCH_PROCESS_KEYWORD)
        except subprocess.CalledProcessError:
            print('FreeSWITCH is not running')
            return None
        
        try:
            proc = subprocess.check_output(['C:\\Program Files\\FreeSWITCH\\fs_cli.exe', '-x', 'sofia status'], shell = True, stdin=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print('sofia status returned nothing')
            return None

        #proc.communicate()
        remote_fs_conn_status = ''
        callbox_conn_status = ''
        if proc != 0:
            result = proc.decode('utf-8')
            result_list = result.split(' ')
            result_list_final = []
            for i in result_list:
                if i == '':
                    pass
                else:
                    result_list_final.append(i)
            for i in result_list_final:
                if i == 'external::numconvert\tgateway\t':
                    remote_fs_conn_status = result_list_final[result_list_final.index(i) + 1]
                elif i == 'external::callbox\tgateway\t':
                    callbox_conn_status = result_list_final[result_list_final.index(i) + 1]
        remote_fs_conn_status_list = remote_fs_conn_status.split('\t')
        callbox_conn_status_list = callbox_conn_status.split('\t')
        return remote_fs_conn_status_list[-1][:-2], callbox_conn_status_list[-1][:-2]

    def reloadFreeswitch(self):
        '''
        该函数是重新加载fs配置文件
        输入：
        输出：fs重新加载的输出日志
        '''
        try:
            proc = subprocess.check_output(['C:\\Program Files\\FreeSWITCH\\fs_cli.exe', '-x', 'reload mod_sofia'], shell = True, stdin=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print('reload mod_sofia returned nothing')
            return 
        else:
            print(proc.decode('utf-8'))

    def stopFreeswitch(self):
        '''
        该函数是重关闭fs
        输入：
        输出：
        '''
        try:
            proc = subprocess.check_output(['C:\\Program Files\\FreeSWITCH\\fs_cli.exe', '-x', 'shutdown'], shell = True, stdin=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print("fs_cli -x shutdown returned nothing")
            return 0
        else:
            try:
                self.isRunning(FREESWITCH_PROCESS_KEYWORD)
            except subprocess.CalledProcessError:
                print("fs console not stopped")
                return 0
            else:
                print("fs console stopped")
                return 1

    def startFreeswitch(self):
        try:
            proc = subprocess.Popen(['C:\\Program Files\\FreeSWITCH\\FreeSwitchConsole.exe', '-nc'], creationflags=subprocess.DETACHED_PROCESS)
        except Exception:
            print(traceback.format_exc())
            return 0
        else:
            try:
                self.isRunning(FREESWITCH_PROCESS_KEYWORD)

            except subprocess.CalledProcessError:
                print("fs is stopped")
            else:
                print("fs is running")
                # print(proc.decode('utf-8'))
                return 1

# isRunning('docker')
# isRunning('FreeSwitch')
# if getContainerID() != None:
#     print("容器正在运行中，正在获取日志")
#     getContainerLog(getContainerID())
# if __name__ == '__main__':
#     fs_con_status, callbox_con_status = freeswitchStatus()
#     print(fs_con_status, callbox_con_status)
#a = subprocess.check_call('C:\\Program Files\\FreeSWITCH\\fs_cli.exe')
#startFreeswitch()