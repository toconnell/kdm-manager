#!/usr/bin/env python


from ConfigParser import SafeConfigParser
import os
import sys

def load(profile="production"):
    """ Returns a ConfigParser object of the file specified with the
    'settings_path' kwarg. """

    project_root = os.path.join(os.environ["HOME"],"kdm-manager","v2")

    if profile == "production":
        config_file_abs_path = os.path.join(project_root, "sysadmin/settings_prod.cfg")
    elif profile == "development":
        config_file_abs_path = os.path.join(project_root, "sysadmin/settings_dev.cfg")
    else:
        config_file_abs_path = profile

    if not os.path.isfile(config_file_abs_path):
        raise Exception("Config file '%s' does not exist!" % config_file_abs_path)

    config = SafeConfigParser()
    config.readfp(open(config_file_abs_path))
    config.file_path = config_file_abs_path
    config.basename = os.path.basename(config_file_abs_path)
    config.profile = profile
    return config

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        settings = load(sys.argv[1])
    else:
        settings = load()
    print("\n  Loaded config info from '%s' successfully." % settings.file_path)
    print("  debug = %s\n" % settings.getboolean("application","debug"))
