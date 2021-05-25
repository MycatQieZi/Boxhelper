from config_manager.consts import ICON_BASE64, TMP_ICON_FILENAME

import base64, os

def makeIconFile():
	icondata = base64.b64decode(ICON_BASE64)
	## The temp file is icon.ico
	tempFile = TMP_ICON_FILENAME
	with open(tempFile,"wb") as iconfile:
	## Extract the icon
		iconfile.write(icondata)
		return tempFile
