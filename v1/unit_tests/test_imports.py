#!/usr/bin/env python

import glob
import os
import unittest

class testModuleImports(unittest.TestCase):
    """ Tests here are all written against the main 'style.css' file in the
    project. Beyond basic linting on the fly, we do some more...complex/project-
    specific tests here. """

    def setUp(self):
        all_files = glob.glob("*")
        self.application_files = [f for f in all_files if os.path.isfile(f) and os.path.splitext(f)[1] != '.pyc']
        pass

    def test_deprecated_modules(self):
        """ - Check for imports of deprecated modules """

        deprecated_modules_present = False

        deprecated_modules = [
            "game_assets",
            "models",
        ]

        for path in self.application_files:
            for module in deprecated_modules:
                module_text = open(path).read()
                found_reference = False
                if "import %s" % module in module_text:
                    found_reference = True
                if "from %s" % module in module_text:
                    found_reference = True

                if found_reference:
                    print("Found '%s' reference in %s" % (module, path))
                    deprecated_modules_present = True

        self.assertFalse(deprecated_modules_present)


