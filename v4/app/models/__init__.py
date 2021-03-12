"""

    Module methods for models live here.

"""

import importlib

def get_asset_dicts(asset_module):
    """ In this one, 'asset_module' is one of the *.py files in our 'assets'
    folder. This method returns a dictionary where the key values are the
    names of thedictionaries in the module. """

    module = importlib.import_module('app.assets.%s' % asset_module)

    output = {}

    for module_dict, v in module.__dict__.items():
        if isinstance(v, dict) and not module_dict.startswith('_'):
            output[module_dict] = getattr(module, module_dict)

    return output
