#!/usr/bin/env python

#
#   Interactive module query tool
#

import glob
import os

import models

class queryObject(object):

    def __init__(self):
        modules = set()
        pathname = os.path.join(models.__path__[0], "*.py")
        for m in glob.glob(pathname):
            module = os.path.splitext(os.path.basename(m))[0]
            modules.add(module)
        modules.remove('__init__')
        self.modules = sorted(modules)

    def prompt_for_module(self):
        """ Prompts to see which module to import. """
        option_dict = {}
        n= 0
        for m in self.modules:
            option_dict[n] = m
            n+=1
        for k in sorted(option_dict.keys()):
            print(" %s  %s" % (k, option_dict[k]))
        m_string = raw_input('\n --> Model? ')
        query_module = option_dict[int(m_string)]
        self.import_module(query_module)

    def run_cmd(self, A, cmd):
        """ Runs a command against A (which should be imported by now). """
        exec "print A.%s()" % cmd
        again = raw_input('\n --> Run another command? ')
        if again in dir(A):
            self.run_cmd(A, again)

    def import_module(self, module_string=None):
        """ Imports a module and initializes its assets. """

        exec "import models.%s as %s" % (module_string, module_string)
        exec "A = %s.Assets()" % module_string
        print(A)
        for method in dir(A):
            print(method)

        # do a command
        cmd = raw_input('\n --> Command? ')
        self.run_cmd(A, cmd)

        again = raw_input(' --> Query another module? ')
        if again.upper() in ['Y','YES','']:
            self.prompt_for_module()


if __name__ == "__main__":
    Q = queryObject()
    Q.prompt_for_module()

