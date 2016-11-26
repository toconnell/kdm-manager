#!/usr/bin/python2.7

from bson import json_util
import json

import Models
import utils



class Survivor(Models.UserAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """


    def __repr__(self):
        return "%s [%s] (%s)" % (self.survivor["name"], self.survivor["sex"], self.survivor["_id"])


    def __init__(self, *args, **kwargs):
        self.collection="survivors"
        self.object_version = 0.1
        Models.UserAsset.__init__(self,  *args, **kwargs)


    def serialize(self, return_type="JSON"):
        """ Renders the settlement, including all methods and supplements, as
        a monster JSON object. This one is the gran-pappy. """

        output = self.get_serialize_meta()
        output.update(self.survivor)
        output.update({"cursed_items": self.get_cursed_items()})
        return json.dumps(output, default=json_util.default)


    def get_cursed_items(self):
        """ Returns a list of cursed item handles on the survivor. """
        if not "cursed_items" in self.survivor.keys():
            return []
        else:
            return self.survivor["cursed_items"]



    #
    #   UPDATE and POST Methods below here!
    #

    @utils.error_log
    def update_from_dict(self, d):
        """ Updates the survivor's MDB record from a dictionary. Saves it. Be
        REAL careful with this one. """

        for k in d:
            self.survivor[k] = d[k]
        utils.mdb.survivors.save(self.survivor)
