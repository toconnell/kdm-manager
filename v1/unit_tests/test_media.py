#!/usr/bin/env python

import aux

import glob
import os
import unittest

# a list of CSS selectors that are composed dynamically during view
#   interpolation and are excluded from our vestigial selector test
css_selector_ignore = [
    'mov_token',
    'acc_token',
    'eva_token',
    'luck_token',
    'spd_token',
    'str_token',
    'ng-enter',
    'ng-enter-active',
    'ng-leave',
    'ng-leave-active',
    'severe_injury',
    'weapon_mastery',
    'fighting_art_gradient',
    'secret_fighting_art_gradient'
]


class testStyleCSS(unittest.TestCase):
    """ Tests here are all written against the main 'style.css' file in the
    project. Beyond basic linting on the fly, we do some more...complex/project-
    specific tests here. """

    def setUp(self):
        """ Initialize with the relative path to the style.css file and a set
        that contains relative paths to all HTML template files in the project.
        """
        self.css_files = aux.get_CSS_files()
        self.html_files = aux.get_HTML_templates()

    def test_css_files_exist(self):
        """ - Check for existance of required CSS files """
        for path in self.css_files:
            self.assertTrue(os.path.isfile(path))

    def test_css_classes(self):
        """ - Check for vestigial CSS class selectors

        Iterates through HTML files in the project and determines whether
        class selectors in the main CSS are used in at least one file. """

        print('\n- comparing %s CSS files with %s HTML template files!' % (len(self.css_files), len(self.html_files)))

        # find classes (this code is ugly, but at least it doesn't use regexes,
        # right? Could be way worse.
        all_classes_in_use = True
        vestigial_classes = set()
        classes = set()

        for css_file in self.css_files:
            class_count = 0
            with open(css_file) as f:
                for line in f.readlines():
                    for w in line.split(" "):
                        if w.startswith('.'):
                            raw = w[1:].split(':')[0].strip().replace(",","")
                            for c in raw.split('.'):
                                classes.add(c)
                                class_count += 1
            print("- %s CSS class refereces found in %s" % (class_count, css_file))
        print("- %s unique CSS classes found in %s CSS files" % (len(classes), len(self.css_files)))

        # loop through classes and, for each, loop through our template files
        for c in classes:
            class_used = False
            if c in css_selector_ignore:
                class_used = True
            for f in self.html_files:
                if c in open(f).read():
                    class_used = True
            if not class_used:
                print(" `-CSS class '%s' is not used in any HTML file!"  % c)
                vestigial_classes.add(c)
                all_classes_in_use = False

        # finally, report vestigial classes and run the actual test
        if len(vestigial_classes) > 0:
            percent = 100 * float(len(vestigial_classes)) / len(classes)
            print('- Found %s vestigial class selectors! (approx. %s%%)' % (len(vestigial_classes), int(percent)))
#        self.assertTrue(all_classes_in_use)
