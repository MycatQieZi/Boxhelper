from lxml import etree
import ctypes, os, sys

def write_to_FS_Conf_XML(path, xml_tree):
	xml_tree.write(path, pretty_print = True)
	


