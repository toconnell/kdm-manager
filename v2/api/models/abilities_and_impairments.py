#!/usr/bin/python2.7


from assets import abilities_and_impairments
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):

        self.assets = {}
        for k, v in abilities_and_impairments.__dict__.iteritems():
            if isinstance(v, dict) and not k.startswith('_'):
                for dict_key in v.keys():
                    v[dict_key]["type"] = k
                self.assets.update(v)

        Models.AssetCollection.__init__(self,  *args, **kwargs)
