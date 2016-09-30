#!/usr/bin/python2.7

from ConfigParser import SafeConfigParser
import os


class Settings:

    def __init__(self, settings_type=None):
        """ Initialize a Settings object as public or private. """

        if settings_type == "private":
            filename = "settings_private.cfg"
        else:
            filename = "settings.cfg"

        self.config = SafeConfigParser()
        self.config.readfp(open(filename))
        self.config.settings_type = settings_type
        self.config.file_path = os.path.abspath(filename)

    def get(self, section, key):
        """ Gets a value. Tries to do some duck-typing. """

        raw_value = self.config.get(section,key)
        if raw_value in ["True","False"]:
            return self.config.getbool(section,key)
        else:
            try:
                return self.config.getint(section,key)
            except:
                pass

        return raw_value
