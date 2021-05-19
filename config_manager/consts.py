CONF_PATH = "C:\\Program Files\\FreeSWITCH\\conf\\sip_profiles\\external\\"

XMLS = [
	"callbox.xml",
	"numconvert.xml"
]

FS_CONF = {
	"callbox":{
		"username": {
			'name':'模拟分机号', 'value':''
		},
		"realm" : {
			'name':'盒子IP地址', 'value':''
		}
	},
	"numconvert": {
		"username" : {
			'name':'线路名称', 'value':''
		},
		"realm" : {
			'name':'证通远程地址', 'value':''
		},
		"password" : {
			'name':'线路密码', 'value':''
		}
	}
}