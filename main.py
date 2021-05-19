import sys
# sys.path.insert(0, './config_manager')

from elevate import elevate
from boxhelper_gui import gui_start

def is_admin():
	try:
		return ctypes.windll.shell32.IsUserAnAdmin()
	except:
		return False

if not is_admin():
	elevate(show_console=False)

gui_start()