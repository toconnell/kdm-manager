#!/usr/bin/python2.7

import Models
import json
from bson import json_util
import utils



class Survivor(Models.UserAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):
        self.collection="survivors"
        Models.UserAsset.__init__(self,  *args, **kwargs)

    def __repr__(self):
        return "%s [%s] (%s)" % (self.survivor["name"], self.survivor["sex"], self.survivor["_id"])

    def as_json(self):
        """ Dumps the survivor as JSON. """
        return json.dumps(self.survivor, default=json_util.default)

    @utils.error_log
    def update_from_dict(self, d):
        """ Updates the survivor's MDB record from a dictionary. Saves it. Be
        REAL careful with this one. """

        for k in d:
            self.survivor[k] = d[k]
        utils.mdb.survivors.save(self.survivor)
