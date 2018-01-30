#!/usr/bin/env python

import glob
import os
import unittest

class testStyleCSS(unittest.TestCase):
    """ Tests here are all written against the main 'style.css' file in the
    project. Beyond basic linting on the fly, we do some more...complex/project-
    specific tests here. """

    def setUp(self):
        """ Initialize with the relative path to the style.css file and a set
        that contains relative paths to all HTML template files in the project.
        """

        self.path = 'media/style.css'
        self.html_files = set(['html.py'])
        for template in glob.glob('templates/*.html'):
            self.html_files.add(template)

    def test_file_exists(self):
        """ - Check for existance of media/style.css """
        self.assertTrue(os.path.isfile(self.path))

    def test_classes(self):
        """ - Check for vestigial CSS class selectors

        Iterates through HTML files in the project and determines whether
        class selectors in the main CSS are used in at least one file. """

        print('checking %s HTML template files!' % (len(self.html_files)))

        # find classes (this code is ugly, but at least it doesn't use regexes,
        # right? Could be way worse.
        all_classes_in_use = True
        vestigial_classes = set()
        classes = set()
        with open(self.path) as f:
            for line in f.readlines():
                for w in line.split(" "):
                    if w.startswith('.'):
                        raw = w[1:].split(':')[0].strip().replace(",","")
                        for c in raw.split('.'):
                            classes.add(c)
        print("%s CSS classes found in %s" % (len(classes), self.path))

        # loop through classes and, for each, loop through our template files
        for c in classes:
            class_used = False
            for f in self.html_files:
                if c in open(f).read():
                    class_used = True
            if not class_used:
                print("CSS Class '%s' is not used in any HTML file!"  % c)
                vestigial_classes.add(c)
                all_classes_in_use = False

        # finally, report vestigial classes and run the actual test
        if len(vestigial_classes) > 0:
            percent = 100 * float(len(vestigial_classes)) / len(classes)
            print('Found %s vestigial class selectors! (approx. %s%%)' % (len(vestigial_classes), int(percent)))
        self.assertTrue(all_classes_in_use)
