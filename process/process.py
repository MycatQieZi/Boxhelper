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
import os
import subprocess
import time
import psutil

def isRunning(progress_name):
    '''
    该函数是一个判断函数，返回的是True、False的bool值判断
    输入应该是准确的进程名docker、FreeSwitch
    '''
    try:
        #print('tasklist | findstr ' + progress_name)
        #print(os.popen('tasklist | findstr ' + progress_name).readlines())
        process = len(os.popen('tasklist | findstr ' + progress_name).readlines())
        #print(process)
        if process >= 1:
            print(progress_name + " is running")
            return True
        else: 
            print(progress_name + " is not running")
            return False
    except:
        print("程序错误")
        return False

def getContainerID():
    '''
    该函数功能是查看目前的长在运行的容器的ContainerID，没有输入，输出为uContainerID
    '''
    #proc = subprocess.Popen('cmd.exe',creationflags=subprocess.CREATE_NEW_CONSOLE, shell = True, stdout =  subprocess.PIPE)
    #time.sleep(5)
    proc = subprocess.check_output(["docker", "ps"], shell = True)
    if proc != None:
        result = proc.decode('utf-8')
        result_list = result.split('\n')
        return result_list[1].split(' ')[0]
    return None

def getContainerLog(ContainerID):
    '''
    该函数是依据上一个函数得到的ContainerID查看器日志内容并按行输出
    输入：ContainerID
    输出：<list>logs
    '''
    proc = subprocess.check_output(["docker", "logs", ContainerID], shell = True)
    result = proc.decode('utf-8')
    result_list = result.split('\n')
    for i in result_list:
        print(i)
        
def freeswitchStatus():
    '''
    该函数是用来查看本地fs的双向注册状态，即为callbox的注册状态和numconvert的注册状态
    输入：
    输出：<str>callbox注册状态，<str>numconvert注册状态
    '''
    if isRunning('FreeSwitch'):
        proc = subprocess.check_output(['C:\\Program Files\\FreeSWITCH\\fs_cli.exe', '-x', 'sofia status'], shell = True)
    else:
        proc = 0
        print('m')
    #proc.communicate()
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

def reloadFreeswitch():
    '''
    该函数是重新加载fs配置文件
    输入：
    输出：fs重新加载的输出日志
    '''
    proc = subprocess.check_output(['C:\\Program Files\\FreeSWITCH\\fs_cli.exe', '-x', 'reload mod_sofia'], shell = True)
    print(proc.decode('utf-8'))

def stopFreeswitch():
    '''
    该函数是重关闭fs
    输入：
    输出：
    '''
    proc = subprocess.check_output(['C:\\Program Files\\FreeSWITCH\\fs_cli.exe', '-x', 'shutdown'], shell = True)
    time.sleep(5)
    if isRunning('FreeSwitch'):
        print("not stopped")
    else:
        print("stopped")
# def startFreeswitch():
#     proc = subprocess.run(['C:\\Program Files\\FreeSWITCH\\FreeSwitchConsole.exe'], shell = True)
#     time.sleep(5)
#     if isRunning('FreeSwitch'):
#         print("not stopped")
#     else:
#         print("stopped")
    #print(proc.decode('utf-8'))




# isRunning('docker')
# isRunning('FreeSwitch')
# if getContainerID() != None:
#     print("容器正在运行中，正在获取日志")
#     getContainerLog(getContainerID())
remote_fs_conn_status, callbox_conn_status = freeswitchStatus()
print(remote_fs_conn_status, callbox_conn_status)
#a = subprocess.check_call('C:\\Program Files\\FreeSWITCH\\fs_cli.exe')
#startFreeswitch()