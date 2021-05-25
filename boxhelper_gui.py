from tkinter import *
from tkinter import ttk, messagebox, scrolledtext
from config_manager.reg import regGetQTHZPath
from config_manager.FS_config_manager import FSConfigManager
from config_manager.consts import FS_CONF, ServiceStatus, ServiceType, WIDTH, HEIGHT, ICON_BASE64
from process_manager.process_manager import FREESWITCH_PROCESS_KEYWORD, DOCKER_PROCESS_KEYWORD, ProcessManager
from utils import makeIconFile

import copy, traceback, subprocess, os, base64

class BoxGUI(Frame):
	def __init__(self, root=None):
		Frame.__init__(self, root)
		self.root = root
		self.init_window()
		self.pack()

		self.fs_conf_manager = FSConfigManager()
		self.proc_manager = ProcessManager()

		self.conf_labels = []
		self.conf_textboxes = []
		self.fs_conf = copy.deepcopy(FS_CONF)
		self.var_texts = copy.deepcopy(FS_CONF)
		self.new_var_texts = copy.deepcopy(FS_CONF)
		self.isConfAquired = False
		self.beginRow = 3
		self.srv_status = {}
		self.fs_trigger_buttons = []
		self.qthz_status = StringVar(value=ServiceStatus.UNKNOWN.value)
		self.fs_status = StringVar(value=ServiceStatus.UNKNOWN.value)
		self.docker_status = StringVar(value=ServiceStatus.UNKNOWN.value)
		self.sofia_status = StringVar(value=ServiceStatus.UNKNOWN.value)
		
		self.init_app()
		self.create_tab()
		self.create_config_widget()
		self.create_FS_widget()
		self.create_utility_widget()
		self.create_log_widget()
		self.get_latest_fs_conf()

	def init_window(self):
		windowWidth = self.root.winfo_reqwidth()
		windowHeight = self.root.winfo_reqheight()
		self.placement = [
			int(self.root.winfo_screenwidth()/2 - WIDTH/2),
			int(self.root.winfo_screenheight()/2 - HEIGHT/2)
		]
		self.root.geometry("%ix%i+%i+%i"%(WIDTH, HEIGHT, self.placement[0], self.placement[1]))
		
		# self.icon_file = PhotoImage(data=ICON_BASE64)
		# self.root.tk.call('wm', 'iconphoto', self.root._w, self.icon_file)
		# self.rootwm_iconphoto(True, self.icon_file)
		self.icon_file = makeIconFile()
		self.root.wm_iconbitmap(self.icon_file)

	def init_app(self):
		self.root.withdraw()
		self.init_window = Toplevel(self.root)
		self.init_window.title("晴听盒子工具箱: 启动中")
		self.init_window.geometry("200x75+%i+%i"%(self.placement[0], self.placement[1]))
		self.init_window.wm_iconbitmap(self.icon_file)
		os.remove(self.icon_file)
		self.icon_file = ""
		Label(self.init_window, text="正在初始化启动中, 请稍候").pack(padx=10, pady=10)
		self.root.update()

		self.init_sequence()

		self.init_window.destroy()
		self.root.deiconify()


	def init_sequence(self):
		self.get_service_status()
		
	def change_text(self):
		self.reg_path_text.set(regGetQTHZPath())  

	def on_quit(self):
		self.root.destroy()

	def on_edit(self):
		if not self.isConfAquired:
			return

		for widget in self.conf_labels:
			widget.grid_remove()
		self.copy_var_text_list(self.var_texts, self.new_var_texts)
		self.make_config_textboxes()
		self.edit_button.pack_forget()
		self.save_button.pack(side="left")
		self.cancel_button.pack(side="left")

	def on_save(self):
		res = messagebox.askyesno("保存修改", "您确定要保存修改, 并且覆盖已有配置吗?")
		if not res:
			return

		try:
			self.fs_conf_manager.update_config(self.new_var_texts)
		except PermissionError:
			messagebox.showerror("保存失败", 
				"权限不足导致无法保存, 请使用管理员权限打开工具箱后再尝试保存配置\n"+\
				"打开方式: 右键该工具箱程序, 点击\"以管理员身份运行\"")
			return

		self.get_latest_fs_conf()
		for widget in self.conf_labels:
			widget.grid()
		for widget in self.conf_textboxes:
			widget.grid_remove()

		self.cancel_button.pack_forget()
		self.save_button.pack_forget()
		self.edit_button.pack(side="left")

	def on_cancel(self):
		res = messagebox.askyesno("取消修改", "您确定要取消修改吗?")
		if not res:
			return

		for widget in self.conf_labels:
			widget.grid()
		for widget in self.conf_textboxes:
			widget.grid_remove()

		self.get_latest_fs_conf()
		self.copy_var_text_list(self.var_texts, self.new_var_texts)
		self.cancel_button.pack_forget()
		self.save_button.pack_forget()
		self.edit_button.pack(side="left")

	def on_update_status_all(self):
		self.update_button['state'] = 'disabled'
		self.update_button['text'] = '刷新中..'
		self.root.update()
		self.get_service_status()
		self.update_button['state'] = 'normal'
		self.update_button['text'] = '刷新'
		

	def on_fs_trigger_button_pressed(self, curr_button, *operator_funcs):
		button_text = curr_button['text']
		for button in self.fs_trigger_buttons:
			button['state'] = 'disabled'
			if curr_button==button:
				button['text'] = '加载中..'
		
		self.root.update()
		for func in operator_funcs:
			func()

		for button in self.fs_trigger_buttons:	
			button['state'] = 'normal'
			if curr_button==button:
				button['text'] = button_text

	# helper function to walk thru specific config-like object
	def conf_structure_walker(self, conf_obj, operator_func, **kwargs):
		last_category_length = 0
		for i, conf_type in enumerate(conf_obj):
			sub_category = conf_obj[conf_type]
			for j, name in enumerate(sub_category):
				operator_func(i, j, last_category_length, conf_obj, conf_type, name, **kwargs)
				
			last_category_length += len(sub_category)

	#copy var_text list in place
	def copy_var_text_list(self, original, clone):
		self.conf_structure_walker(clone, self.copy_var_text_list_4each, original=original)

	def copy_var_text_list_4each(self, i, j, last_len, conf_obj, conf_type, name, **kwargs):
		text_var = conf_obj[conf_type][name]['value']
		text_var.set(kwargs['original'][conf_type][name]['value'].get())

	# acquire the latest fs config, from file
	def get_latest_fs_conf(self):
		try:
			self.fs_conf = self.fs_conf_manager.get_fs_config()
		except OSError:
			messagebox.showerror("FreeSWITCH 配置读取失败", 
				"无法读取FreeSWITCH的配置文件, 请检查FreeSWITCH是否正确安装\n"+\
				"或者FreeSWITCH是否有正确的配置文件")
			self.fs_conf = copy.deepcopy(FS_CONF)
			self.isConfAquired = False
		else:
			self.conf_structure_walker(self.fs_conf, self.get_latest_fs_conf_4each)
			self.isConfAquired = True
		# self.copy_var_text_list(self.var_texts, self.new_var_texts)

	def get_latest_fs_conf_4each(self, i, j, last_len, conf_obj, conf_type, name, **kwargs):
		# text_var = StringVar()
		# print(conf_obj[conf_type][name]['value'])
		# text_var.set(conf_obj[conf_type][name]['value'])
		self.var_texts[conf_type][name]['value'].set(conf_obj[conf_type][name]['value'])
		# self.new_var_texts[conf_type][name]['value'] = text_var
		self.new_var_texts[conf_type][name]['value'] = StringVar()

	# make config edit textboxes
	def make_config_textboxes(self):
		self.conf_structure_walker(self.fs_conf, self.make_config_textboxed_4each)

	def make_config_textboxed_4each(self, i, j, last_len, conf_obj, conf_type, name, **kwargs):
		entry = Entry(self.tab1, textvariable = self.new_var_texts[conf_type][name]['value'])
		entry.grid(column = 1, row = self.beginRow+last_len+j, padx = 30, pady = 10, sticky="w")
		self.conf_textboxes.append(entry)

	# make each config labels
	def make_config_labels(self, i, j, last_len, conf_obj, conf_type, name, **kwargs):
		text_var = StringVar()
		text_var.set(conf_obj[conf_type][name]['value'])
		self.var_texts[conf_type][name]['value'] = text_var

		Label(self.tab1, text = conf_obj[conf_type][name]['name']) \
			.grid(column = 0, row = self.beginRow+last_len+j, padx = 30, pady = 10, sticky="w")
		label = Label(self.tab1, textvariable = text_var)
		label.grid(column = 1, row = self.beginRow+last_len+j, padx = 30, pady = 10, sticky="w")
		self.conf_labels.append(label)

	def create_config_widget(self):
		# QTHZ installation path
		self.reg_path_text = StringVar()
		self.reg_path_text.set("外呼线路修改: ") 
		Label(self.tab1, textvariable = self.reg_path_text)\
			.grid(column = 0, row = 0, padx = 30, pady = 20)
		ttk.Separator(self.tab1, orient='horizontal').grid(row=1, padx=20, columnspan=2, column=0, sticky="ew")
	
		# make config labels
		self.conf_structure_walker(self.fs_conf, self.make_config_labels)

		# make button group
		self.button_frame = Frame(self.tab1)
		# edit button
		self.edit_button = Button(self.button_frame, text = "修改", command = self.on_edit)
		# cancel button
		self.cancel_button = Button(self.button_frame, text = "取消", command = self.on_cancel)
		# save button
		self.save_button = Button(self.button_frame, text = "保存", command = self.on_save)

		self.button_frame.grid(column = 1, row = 0, padx=30, pady=10, sticky="w")
		self.edit_button.pack(side="left")
		
		# quit button
		Button(self.tab1, text = "退出", 
				command = self.on_quit).place(x = 400, y = 540, height = 25, width = 40)

	def get_service_status(self):
		try:
			self.srv_status[ServiceType.QTHZ] = ServiceStatus.RUNNING if self.proc_manager.is818Running() else ServiceStatus.STOPPED 
		except subprocess.CalledProcessError:
			self.srv_status[ServiceType.QTHZ] = ServiceStatus.STOPPED
		except Exception:
			self.srv_status[ServiceType.QTHZ] = ServiceStatus.UNKNOWN
			print(traceback.format_exc())
		self.qthz_status.set(self.srv_status[ServiceType.QTHZ].value)
		
		try:
			self.srv_status[ServiceType.FS] = ServiceStatus.RUNNING if self.proc_manager.isRunning(FREESWITCH_PROCESS_KEYWORD) else ServiceStatus.STOPPED 
		except subprocess.CalledProcessError:
			self.srv_status[ServiceType.FS] = ServiceStatus.STOPPED
		except Exception:
			self.srv_status[ServiceType.FS] = ServiceStatus.UNKNOWN
			print(traceback.format_exc())
		self.fs_status.set(self.srv_status[ServiceType.FS].value) 
		

		try:
			self.srv_status[ServiceType.DOCKER] = ServiceStatus.RUNNING if self.proc_manager.isRunning(DOCKER_PROCESS_KEYWORD) else ServiceStatus.STOPPED 
		except subprocess.CalledProcessError:
			self.srv_status[ServiceType.DOCKER] = ServiceStatus.STOPPED
		except Exception:
			self.srv_status[ServiceType.DOCKER] = ServiceStatus.UNKNOWN
			print(traceback.format_exc())
		self.docker_status.set(self.srv_status[ServiceType.DOCKER].value) 
	
	def get_FS_running_status(self):
		try:
			self.srv_status[ServiceType.FS] = ServiceStatus.RUNNING if self.proc_manager.isRunning(FREESWITCH_PROCESS_KEYWORD) else ServiceStatus.STOPPED 
		except subprocess.CalledProcessError:
			self.srv_status[ServiceType.FS] = ServiceStatus.STOPPED
		except Exception:
			self.srv_status[ServiceType.FS] = ServiceStatus.UNKNOWN
			print(traceback.format_exc())
		if self.srv_status[ServiceType.FS] == ServiceStatus.RUNNING:
			self.fs_stop_button['text'] = '停止'
		else:
			self.fs_stop_button['text'] = '启动'

		self.fs_status.set(self.srv_status[ServiceType.FS].value)

	def create_utility_widget(self):
		# QTHZ
		Label(self.tab0, text ="晴听盒子网页服务:") \
			.grid(column = 0, row = 0, padx = 30, pady = 20)
		ttk.Separator(self.tab0, orient='horizontal').grid(row=1, padx=20, columnspan=2, sticky="ew")
		
		Label(self.tab0, text ="状态:") \
			.grid(column = 0, row = 2, padx = 30, pady = 10)
		Label(self.tab0, textvariable = self.qthz_status)\
			.grid(column = 1, row = 2, padx = 30, pady = 10)

		# FS
		Label(self.tab0, text ="线路服务:") \
			.grid(column = 0, row = 3, padx = 30, pady = (60,20))
		ttk.Separator(self.tab0, orient='horizontal').grid(row=4, padx=20, columnspan=2, sticky="ew")
		
		Label(self.tab0, text ="状态:") \
			.grid(column = 0, row = 5, padx = 30, pady = 10)		
		Label(self.tab0, textvariable = self.fs_status)\
			.grid(column = 1, row = 5, padx = 30, pady = 10)

		# docker
		Label(self.tab0, text ="容器服务:") \
			.grid(column = 0, row = 6, padx = 30, pady = (60,20))
		ttk.Separator(self.tab0, orient='horizontal').grid(row=7, padx=20, columnspan=2, sticky="ew")
		
		Label(self.tab0, text ="状态:") \
			.grid(column = 0, row = 8, padx = 30, pady = 10)
		Label(self.tab0, textvariable = self.docker_status)\
			.grid(column = 1, row = 8, padx = 30, pady = 10)

		# update button
		self.update_button = Button(self.tab0, text = "刷新", 
				command = self.on_update_status_all)
		self.update_button.place(x = 400, y = 20, height = 25, width = 60)

		# quit button
		Button(self.tab0, text = "退出", 
				command = self.on_quit).place(x = 400, y = 540, height = 25, width = 40)

	def validate(self, action, index, value_if_allowed,
					   prior_value, text, validation_type, trigger_type, widget_name):
		if value_if_allowed:
			try:
				int_value = int(value_if_allowed)
				return int_value <= 500 or value_if_allowed==''
			except ValueError:
				return False
		else:
			return False

	def refresh_docker_logs(self):
		log_list = self.proc_manager.getContainerLog("hello", self.log_line_count.get())
		self.log_box['state'] = 'normal'
		self.log_box.delete('1.0', END)
		self.log_box.insert(END, 
			'\n'.join(log_list) if not log_list == None else "无法获取日志, 请检查容器服务是否以启动或者晴听盒子是否已启动")
		self.log_box['state'] = 'disabled'

	def create_log_widget(self):
		# refresh button and line count setter
		Button(self.tab2, text = "刷新", command=self.refresh_docker_logs).place(x=150, y=20, height=25, width=40)
		Label(self.tab2, text="显示行数").place(x=20, y=20, height=25)
		validation_callback = (self.tab2.register(self.validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W') 
		self.log_line_count = IntVar(self.tab2, value=50)
		self.log_entry = Entry(self.tab2, validate='key', validatecommand=validation_callback, textvariable=self.log_line_count)
		self.log_entry.place(x=75, y=20, height=25, width=60)

		text = "点击刷新按钮更新最新日志"
		self.log_box = scrolledtext.ScrolledText(self.tab2)
		self.log_box.insert(INSERT, text)
		self.log_box.place(x=20, y=60, height=520, width=440)
		self.log_box['state'] = 'disabled'

	def update_FS_running_status(self, button):
		self.on_fs_trigger_button_pressed(button, self.get_FS_running_status)

	def reloadFS(self, button):
		self.on_fs_trigger_button_pressed(button, 
			self.proc_manager.reloadFreeswitch, 
			self.get_FS_running_status)

	def stopFS(self, button):
		operation = self.proc_manager.stopFreeswitch \
			if self.srv_status[ServiceType.FS] == ServiceStatus.RUNNING \
			else self.proc_manager.startFreeswitch

		self.on_fs_trigger_button_pressed(button, 
			operation, 
			self.get_FS_running_status)

	def update_sofia_status(self, button):
		self.on_fs_trigger_button_pressed(button, 
			self.get_sofia_status)
	
	def get_sofia_status(self):
		status = self.proc_manager.freeswitchStatus()
		self.sofia_status.set(ServiceStatus.UNKNOWN.value if status==None else " ".join(status))


	def create_FS_widget(self):
		# QTHZ
		Label(self.tab3, text ="线路服务详细状态:") \
			.grid(column = 0, row = 0, padx = 30, pady = 20)
		ttk.Separator(self.tab3, orient='horizontal').grid(row=1, padx=20, columnspan=2, sticky="ew")
		
		Label(self.tab3, text ="FS服务:") \
			.grid(column = 0, row = 2, padx = 30, pady = 10)
		Label(self.tab3, textvariable = self.fs_status)\
			.grid(column = 1, row = 2, padx = 30, pady = 10)

		Label(self.tab3, text ="线路状态:") \
			.grid(column = 0, row = 3, padx = 30, pady = 10)
		Label(self.tab3, textvariable = self.sofia_status)\
			.grid(column = 1, row = 3, padx = 30, pady = 10)

		# update button
		self.fs_update_button = Button(self.tab3, text = "刷新", width=7,
				command = lambda: self.update_FS_running_status(self.fs_update_button))
		self.fs_update_button.grid(column = 3, row = 0, padx = 30, pady = 20)

		# FS Triggers
		self.fs_stop_button = Button(self.tab3, text = "启动", width=5,
				command = lambda: self.stopFS(self.fs_stop_button))
		self.fs_stop_button.grid(column = 3, row = 2, pady = 10)

		self.fs_restart_button = Button(self.tab3, text = "配置重载", width=7,
				command = lambda: self.reloadFS(self.fs_restart_button))
		self.fs_restart_button.grid(column = 4, row = 2, pady = 10)
		
		
		self.fs_status_button = Button(self.tab3, text = "获取", width=5, 
				command = lambda: self.update_sofia_status(self.fs_status_button))
		self.fs_status_button.grid(column = 3, row = 3, pady = 10)

		self.fs_trigger_buttons = [self.fs_update_button, self.fs_restart_button, self.fs_stop_button, self.fs_status_button]

		# quit button
		Button(self.tab3, text = "退出", 
				command = self.on_quit).place(x = 400, y = 540, height = 25, width = 40)

	def create_tab(self):
		tabControl = ttk.Notebook(self.root)

		self.tab0 = Frame(tabControl)
		self.tab1 = Frame(tabControl)
		self.tab2 = Frame(tabControl)
		self.tab3 = Frame(tabControl)
		self.tab_list = []
			
		tabControl.add(self.tab0, text ='服务状态')
		tabControl.add(self.tab3, text ='线路详细状态')
		tabControl.add(self.tab1, text ='线路配置修改')
		tabControl.add(self.tab2, text ='容器运行日志')
		# tabControl.add(self.tab3, text ='配置修改')
		tabControl.pack(expand = 1, fill ="both")

def gui_start():
	root = Tk()
	root.title("晴听盒子工具箱")
	app = BoxGUI(root=root)
	app.mainloop()

if __name__=="__main__":
	gui_start()