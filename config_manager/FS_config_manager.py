from lxml import etree
from config_manager.consts import FS_CONF, XMLS, CONF_PATH
from config_manager.write_file import write_to_FS_Conf_XML
import copy

class FSConfigManager:

	def __init__(self, FSPath=CONF_PATH):
		self.conf_path = FSPath

		self.tree_dict = {}
		self.fs_conf = copy.deepcopy(FS_CONF)
		# self.get_new_fs_config()

	def init_tree_dict_procedure(self):
		for filename in XMLS:
			try:
				tree = etree.parse(self.conf_path + filename)
			except OSError:
				raise
			else:
				self.tree_dict[tree.getroot()[0].get('name')] = tree

	def parse_fs_config(self):
		def operator_func(element, config_item): 
			config_item['value'] = element.get('value')
		
		self.trees_walker(self.tree_dict, operator_func, self.fs_conf)

	def get_new_fs_config(self):
		self.init_tree_dict_procedure()
		self.parse_fs_config()

	def get_fs_config(self):
		self.get_new_fs_config()
		return self.fs_conf

	def set_new_fs_path(self, new_path):
		self.conf_path = new_path

	def update_config(self, new_conf_obj):

		def operator_func(element, config_item): 
			element.attrib['value'] = config_item['value'].get()

		self.trees_walker(self.tree_dict,
			operator_func,
			new_conf_obj)

		for name, tree in self.tree_dict.items():
			try:
				write_to_FS_Conf_XML(self.conf_path + name + ".xml", tree)
			except PermissionError:
				raise

	# helper function to walk thru specific config-like object
	def trees_walker(self, trees, operator_func, fs_conf_obj):
		for tree_name, tree in trees.items():
			# sub_category = conf_obj[conf_type]
			gateway = tree.getroot()[0]
			for element in gateway:
				try:
					config_item = fs_conf_obj[tree_name][element.get('name')]
				except:
					continue
				else:
					operator_func(element, config_item)