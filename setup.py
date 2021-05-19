from distutils.core import setup # Need this to handle modules
import py2exe
# from config_manager import *
# lxml, tkinter, copy, elevate, ctypes, os
# import FS_config_manager, reg, consts, write_file

setup(
	name="BoxHelper",
	windows = [{
    	'script': "main.py",
    	'uac_info': "requireAdministrator",
	}],
	options= {
            'py2exe':{
                'includes': ['lxml.etree', 'lxml._elementpath'],
                # 'package_dir': {'','config_manager'},
                'packages': ['config_manager'],

                'bundle_files': 3,
                # 'compressed'  : True
        }
    },
    # zipfile=None
)