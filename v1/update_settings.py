#!/usr/bin/env python

#
#	This is a sysadmin helper script that does atomic modifications of the
#	core application's settings.cfg file.
#
#	NB: this is kind of a blunt instrument, in that it does not assess validity
#	or perform any other user-friendliness tasks and will definitely overwrite
#	the existing file without asking for permission. YHBW.
#

import ConfigParser
import os
import sys



def usage():
	print("\n INVALID SYNTAX: %s" % " ".join(sys.argv))
	print("\n Usage:\n\n  %s section key value\n" % sys.argv[0])

def update_file(cfg_dir, section, key, value):
	""" Get the file and try to do the update. """

	try:
		config_file = os.path.join(cfg_dir, "settings.cfg")
		settings = ConfigParser.ConfigParser()
		settings.readfp(open(config_file))
	except:
		raise Exception("Settings file could not be loaded!")

	settings.set(section, key, value)

	with open(config_file, 'wb') as c_file:
		settings.write(c_file)

if __name__=="__main__":

	# quick sanity check
	if len(sys.argv) != 4:
		usage()
		sys.exit()

	app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
	update_file(app_dir, sys.argv[1], sys.argv[2], sys.argv[3])
	sys.exit(0)
