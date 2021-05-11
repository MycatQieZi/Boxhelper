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
    #proc = subprocess.Popen('cmd.exe',creationflags=subprocess.CREATE_NEW_CONSOLE, shell = True, stdout =  subprocess.PIPE)
    #time.sleep(5)
    proc = subprocess.check_output(["docker", "ps"], shell = True)
    if proc != None:
        result = proc.decode('utf-8')
        result_list = result.split('\n')
        return result_list[1].split(' ')[0]
    return None

def getContainerLog(ContainerID):
    proc = subprocess.check_output(["docker", "logs", ContainerID], shell = True)
    result = proc.decode('utf-8')
    result_list = result.split('\n')
    for i in result_list:
        print(i)
        

# isRunning('docker')
# isRunning('FreeSwitch')
if getContainerID() != None:
    print("容器正在运行中，正在获取日志")
    getContainerLog(getContainerID())