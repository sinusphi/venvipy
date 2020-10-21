"""
venvipy configuration

This module manages a venvipy configuration file that is created in the root
of a venv beside the 'pyvenv.cfg' file.

The data in this config file is primarily used to:
	1. Provide a home for the venv comment field that shows up in the VenvTable
	2. Maintain a list of development projects that have had venv access scripts
	   generated to access the venv
"""
import os
import sys
import json	  # unfortunately, trying to keep our package dependency count low
import logging 

logger = logging.getLogger(__name__)

# https://docs.python.org/3/library/dataclasses.html
from dataclasses import dataclass
from dataclasses import field
from dataclasses import asdict

import get_data

@dataclass
class VenvConfig:
	venvdir : str
	venvname : str
	comment : str
	projects : []

	def __post_init__(self):
		self.version = get_data.__version__

class VenvConfigMgr:

	def __init__(self, venvdir, venvname, comment=None, projects=[]):
		self.vc = VenvConfig(venvdir, venvname, comment, projects)
		self.cfgfile = os.path.join(venvdir, venvname, 'venvipy.cfg')

	def write(self):
		self.serialized = asdict(self.vc)
		# version is not serialized by asdict() since its added
		# post init
		self.serialized['version'] = self.vc.version
		with open(self.cfgfile, 'w') as jfp:
			json.dump(self.serialized, jfp, indent=4, sort_keys=True)

	def read(self):
		self.serialized = None
		if os.path.exists(self.cfgfile):

			try:
				with open(self.cfgfile, 'r') as jfp:
					self.serialized = json.load(jfp)
			except Exception:
				logger.exception(f"Exception reading Venvipy.cfg file at '{self.cfgfile}'")

			# De-Serialize
			self.vc.venvdir  = self.serialized['venvdir'] 
			self.vc.venvname = self.serialized['venvname'] 
			self.vc.comment  = self.serialized['comment']
			self.vc.projects = self.serialized['projects']
			self.vc.version  = self.serialized['version']

		return self.serialized

#-------------------------------------------------------------------------------
if __name__ == "__main__":
	from tempfile import mkdtemp
	from shutil import rmtree

	venv_name = 'TEST_VENV'

	venv_dir = mkdtemp(prefix='VENVIPY_', suffix='_TESTING')

	venv_path = os.path.join(venv_dir, venv_name)

	os.mkdir(venv_path)

	vcm = VenvConfigMgr(venv_dir, venv_name, "This venv is for testing only" )

	print(vcm.vc.venvdir)
	print(vcm.vc.venvname)
	print(vcm.vc.comment)
	print(vcm.vc.version)
	print(vcm.vc.projects)
	print(vcm.cfgfile)

	vcm.vc.projects.append("D:\\dev\\projects\\PyQtMessageBar")

	print(vcm.vc.projects)

	vcm.vc.projects.append("D:\\dev\\projects\\PyQtCmdSeqProcessor")

	print(vcm.vc.projects)

	print("WRITING VENVIPY.CFG")
	vcm.write()

	vcm.vc.vendir = None
	vcm.vc.venname = None
	vcm.vc.comment = None
	vcm.vc.version = None
	vcm.vc.projects = None

	print(vcm.vc.venvdir)
	print(vcm.vc.venvname)
	print(vcm.vc.comment)
	print(vcm.vc.version)
	print(vcm.vc.projects)
	print(vcm.cfgfile)

	print("READING VENVIPY.CFG")
	o = vcm.read()

	print(o['venvdir'])
	print(o['venvname'])
	print(o['comment'])
	print(o['version'])
	print(o['projects'])

	print("VENVCONFIG OBJECT RE-INITED FROM READ")
	print(vcm.vc.venvdir)
	print(vcm.vc.venvname)
	print(vcm.vc.comment)
	print(vcm.vc.version)
	print(vcm.vc.projects)
	print(vcm.cfgfile)


	with open(vcm.cfgfile, 'r') as vcf:
		lines = vcf.readlines()
	for line in lines:
		print(f"{line}")

	rmtree(venv_dir)
