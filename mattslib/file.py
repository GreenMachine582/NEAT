import json
import logging

__file__ = 'file'
__version__ = '1.3'
__date__ = '10/03/2022'


def read(file=""):
	try:
		extension = file[-4:]
		if "txt" in extension:
			with open(file, "r") as f:
				contents = f.readlines()
		elif "json" in extension:
			with open(file,) as f:
				contents = json.load(f)
		f.close()
		return contents
	except Exception as e:
		logging.exception(e)
	return None


def write(contents=None, file=""):
	if contents is None:
		contents = []
	try:
		with open(file, "w") as f:
			if ".txt" in file:
				f.writelines(contents)
			elif ".json" in file:
				if not isinstance(contents, dict):
					json.dump(contents.__dict__, f)
				else:
					json.dump(contents, f)
		f.close()
	except Exception as e:
		logging.exception(e)


def append(file="", contents=None):
	if contents is None:
		contents = []
	try:
		with open(file, "a") as f:
			f.writelines(contents)
		f.close()
	except Exception as e:
		logging.exception(e)
