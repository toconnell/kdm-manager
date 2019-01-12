"""

    This module is used to manage API documentation.


"""

from collections import OrderedDict

import api
import public, private, sections


class DocumentationObject:

    """ Initialize one of these to work with the documentation, e.g.
    D = DocumentationObject() or similar. """


    def __init__(self):
        """ Sets self.items dictionary. """

        # set default API methods from settings
        defaults = api.settings.get('api','default_methods').split(",")
        self.default_api_methods = [i.strip() for i in defaults]

        self.docs = {}
        for module in [public, private]:
            self.set_docs_from_module(module)

        self.sections = sections.sections


    def set_docs_from_module(self, module):
        """ Creates an entry in the self.items dict for each item in
        'module'. Only goes one level deep. """

        for module_dict, v in module.__dict__.items():
            if isinstance(v, dict) and not module_dict.startswith('_'):
                for dict_key in sorted(v.keys()):

                    doc = v[dict_key]
                    doc['handle'] = dict_key
                    doc['type'] = module.__name__.split('.')[-1]
                    doc['section'] = module_dict

                    # set defaults
                    if 'subsection' not in doc.keys():
                        doc['subsection'] = '__main__'

                    if not 'key' in doc.keys():
                         doc['key'] = False

                    if not 'methods' in doc.keys():
                        doc['methods'] = self.default_api_methods

                    self.docs[dict_key] = doc


    def dump_sections(self):
        """ Dumps self.sections. """
        return self.sections


    def get_sections(self, render_as=list, item_type=None):
        """ Returns a list of section handles used by items whose 'type' attrib
        matches 'item_type'. The list starts out as a set and is unique."""

        sections = set()
        for doc_handle, doc in self.docs.items():
            if item_type is not None:
                if doc['type'] == item_type:
                    sections.add(doc['section'])
            else:
                sections.add(doc['section'])

        if render_as == list:
            return sorted(list(sections))

        return sections


    def get_subsections(self, section=None):
        """ Returns a list of subsection handles found on docs whose section
        matches 'section'. """

        subsections = set()

        for doc_handle, doc in self.docs.items():
            if doc['section'] == section:
                subsections.add(doc['subsection'])

        return sorted(list(subsections))


    def render_as_json(self):
        """ Spits out a JSON representation of the documentation library meant
        to be iterated and displayed, e.g. as HTML. """

        output = {"public": [], "private": []}

        for item_type in output.keys():
            output[item_type] = OrderedDict()
            sections = self.get_sections(item_type=item_type)
            for section in sections:
                output[item_type][section] = OrderedDict()
                subsections = self.get_subsections(section)
                for subsection in subsections:
                    docs = []
                    for doc_handle in sorted(self.docs.keys()):
                        doc = self.docs[doc_handle]
                        if doc['section'] == section and doc['subsection'] ==\
                        subsection:
                            docs.append(doc)
                    output[item_type][section][subsection] = docs

        return output
