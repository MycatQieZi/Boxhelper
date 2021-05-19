from winreg import *

"""
demo to get Qthz installation path in registry
"""

REG_PATH = "SOFTWARE\\Ect888\\Qthz"
INSTALL_PATH_KEY = "InstallPath"

def regGetQTHZPath():
	try:
		reg = OpenKey(HKEY_LOCAL_MACHINE, REG_PATH)
		path = QueryValueEx(reg, INSTALL_PATH_KEY)
		print("path: ",path[0])
		return path[0];
	except EnvironmentError as e:
		print(e)    
	