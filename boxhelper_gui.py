from tkinter import *
from tkinter import ttk, messagebox
from config_manager.reg import regGetQTHZPath
from config_manager.FS_config_manager import FSConfigManager
from config_manager.consts import FS_CONF
from process_manager.process_manager import FREESWITCH_PROCESS_KEYWORD, DOCKER_PROCESS_KEYWORD, Process_Manager

import copy

class BoxGUI(Frame):
	def __init__(self, root=None):
		Frame.__init__(self, root)
		self.root = root
		self.pack()
		self.fs_conf_manager = FSConfigManager()
		self.proc_manager = Process_Manager()
		self.conf_labels = []
		self.conf_textboxes = []
		self.fs_conf = copy.deepcopy(FS_CONF)
		self.var_texts = copy.deepcopy(FS_CONF)
		self.new_var_texts = copy.deepcopy(FS_CONF)
		self.isConfAquired = False
		self.beginRow = 3
		self.create_tab()
		self.create_config_widget()
		self.create_utility_widget()
		self.get_latest_fs_conf()
		
	
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
		self.update_button['text'] = '获取中..'
		self.root.update()
		self.fs_status.set(
			'运行中' 
			if self.proc_manager.isRunning(FREESWITCH_PROCESS_KEYWORD)
			else '未启动')
		self.docker_status.set(
			'运行中' 
			if self.proc_manager.isRunning(DOCKER_PROCESS_KEYWORD)
			else '未启动')
		self.update_button['state'] = 'normal'
		self.update_button['text'] = '更新状态'

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
	
		# Button(self.tab1,text = "FreeSWITCH", command = self.change_text)\
		#   .grid(column = 0, row = 0, padx = 30, pady = 30)

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

		self.button_frame.grid(column = 0, row = 8, padx=30, pady=10, sticky="w")
		self.edit_button.pack(side="left")
		
		# quit button
		Button(self.tab1, text = "退出", 
				command = self.on_quit).place(x = 400, y = 540, height = 25, width = 40)

	def create_utility_widget(self):
		# QTHZ
		Label(self.tab0, text ="晴听盒子网页服务:") \
			.grid(column = 0, row = 0, padx = 30, pady = 20)
		ttk.Separator(self.tab0, orient='horizontal').grid(row=1, padx=20, columnspan=2, sticky="ew")
		
		Label(self.tab0, text ="状态:") \
			.grid(column = 0, row = 2, padx = 30, pady = 10)

		self.qthz_status = StringVar()
		self.qthz_status.set("未知") 
		Label(self.tab0, textvariable = self.qthz_status)\
			.grid(column = 1, row = 2, padx = 30, pady = 10)


		# FS
		Label(self.tab0, text ="软交换线路:") \
			.grid(column = 0, row = 3, padx = 30, pady = (60,20))
		ttk.Separator(self.tab0, orient='horizontal').grid(row=4, padx=20, columnspan=2, sticky="ew")
		
		Label(self.tab0, text ="状态:") \
			.grid(column = 0, row = 5, padx = 30, pady = 10)

		self.fs_status = StringVar()
		self.fs_status.set("未知") 
		Label(self.tab0, textvariable = self.fs_status)\
			.grid(column = 1, row = 5, padx = 30, pady = 10)


		# docker
		Label(self.tab0, text ="容器服务:") \
			.grid(column = 0, row = 6, padx = 30, pady = (60,20))
		ttk.Separator(self.tab0, orient='horizontal').grid(row=7, padx=20, columnspan=2, sticky="ew")
		
		Label(self.tab0, text ="状态:") \
			.grid(column = 0, row = 8, padx = 30, pady = 10)

		self.docker_status = StringVar()
		self.docker_status.set("未知") 
		Label(self.tab0, textvariable = self.docker_status)\
			.grid(column = 1, row = 8, padx = 30, pady = 10)

		# update button
		self.update_button = Button(self.tab0, text = "更新状态", 
				command = self.on_update_status_all)
		self.update_button.place(x = 400, y = 20, height = 25, width = 60)

		# quit button
		Button(self.tab0, text = "退出", 
				command = self.on_quit).place(x = 400, y = 540, height = 25, width = 40)

	def create_tab(self):
		tabControl = ttk.Notebook(self.root)

		self.tab0 = Frame(tabControl)
		self.tab1 = Frame(tabControl)
			
		tabControl.add(self.tab0, text ='服务状态')
		tabControl.add(self.tab1, text ='配置修改')
		tabControl.pack(expand = 1, fill ="both")

def gui_start():
	root = Tk()
	root.title("晴听盒子工具箱")
	root.geometry("480x640")
	app = BoxGUI(root=root)
	app.mainloop()

if __name__=="__main__":
	gui_start()