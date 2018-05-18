#!/usr/bin/env python

import aux

from bs4 import BeautifulSoup
import glob
import os
import sys
import unittest

class testJSimports(unittest.TestCase):
    """ We check our HTML template files for references to JS files and then
    make sure those exist. Some other JS stuff happens here too. """

    def setUp(self):
        """ Initialize with the relative path to the style.css file and a set
        that contains relative paths to all HTML template files in the project.
        """
        self.html_files = aux.get_HTML_templates()
        self.js_files = aux.get_JS_files()

        self.js_file_basenames = set()
        for f in self.js_files:
            self.js_file_basenames.add(os.path.basename(f))


    def test_js_imports(self):
        """ - Check that all JS script import references exist """

        for h in self.html_files:
            h_file = file(h, 'rb').read()
            soup = BeautifulSoup(h_file, 'html.parser')
            script_elements = soup.findAll('script')
            if script_elements != []:
                for s in script_elements:
                    if s.has_attr('src'):
                        if s.get('src')[:4] == "http":
                            pass
                        else:
                            js_file_name = os.path.basename(s.get('src').split('?')[0])
                            self.assertTrue(
                                js_file_name in self.js_file_basenames,
                                "JS file '%s' not found in /js folder!" % js_file_name
                            )
