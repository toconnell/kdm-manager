#!/usr/bin/python2.7

from bson import json_util
from hashlib import md5
import json
from werkzeug.security import safe_str_cmp

import Models
import settings
import utils


#
#   JWT helper methods here!
#

def authenticate(username, password):
    """ Returns None unless a.) there's a real user for 'username' and b.) the
    MD5 hash of the user's password matches the hash of 'password', in which
    case we return a user document from the MDB. """

    user = utils.mdb.users.find_one({"login": username})
    if user is not None and safe_str_cmp(user["password"], md5(password).hexdigest()):
        U = User(_id=user["_id"])
        return U

def jwt_identity_handler(payload):
    """ Bounces the authentication request payload off of the user collection.
    Returns a user object if "identity" in the request exists. """

    logger.debug("here")
    u_id = payload["identity"]
    return utils.mdb.users.find_one({"_id": ObjectId(u_id)})



class User(Models.UserAsset):
    """ This is the main controller for all user objects. """

    def __init__(self, *args, **kwargs):
        self.collection="users"
        self.object_version=0.0
        Models.UserAsset.__init__(self,  *args, **kwargs)

        # JWT needs this
        self.id = str(self.user["_id"])


    def serialize(self):
        """ Creates a dictionary meant to be converted to JSON that represents
        everything that the front-end might need to know about a user. """


        output = self.get_serialize_meta()
        output["user_attr"] = self.user

        # user assets
#        output["user_stat"] = {}

        # user facts
        output["user_fact"] = {}
        output["user_fact"]["has_session"] = self.has_session()
        output["user_fact"]["is_active"] = self.is_active()
        output["user_fact"]["settlements_created"] = self.get_settlements(return_type=int)
        output["user_fact"]["settlements_administered"] = self.get_settlements(qualifier="admin", return_type=int)
        output["user_fact"]["campaigns"] = self.get_settlements(qualifier="player", return_type=int)
        output["user_fact"]["survivors_created"] = self.get_survivors(return_type=int)
        output["user_fact"]["survivors_owned"] = self.get_survivors(qualifier="owner", return_type=int)
        output["user_fact"]["friends"] = self.get_friends(return_type=int)

        return json.dumps(output, default=json_util.default)


    def has_session(self):
        """ Returns a bool representing whether there is a session in the mdb
        for the user."""

        if utils.mdb.sessions.find_one({"created_by": self.user["_id"]}) is not None:
            return True
        return False


    def is_active(self):
        """ Returns a bool representing whether the user has logged an activity
        within our 'active user' horizon/cutoff window. """

        if not self.has_session():
            return False
        if self.user["latest_activity"] > utils.active_user_cutoff:
            return True
        return False


    def get_friends(self, return_type=None):
        """ Returns all of the user's friends (i.e. people he plays in campaigns
        with) as objects. """

        friend_ids      = set()
        friend_emails   = set()

        campaigns = self.get_settlements(qualifier="player")
        for s in campaigns:
            friend_ids.add(s["created_by"])
            c_survivors = utils.mdb.survivors.find({"settlement": s["_id"]})
            for survivor in c_survivors:
                friend_ids.add(survivor["created_by"])
                friend_emails.add(survivor["email"])

        # you can't be friends with yourself
        friend_ids.remove(self.user["_id"])
        friend_emails.remove(self.user["login"])

        # they're only your friend if they're a registered email
        friends = utils.mdb.users.find({"$or":
            [
                {"_id": {"$in": list(friend_ids)}},
                {"login": {"$in": list(friend_emails)}},
            ]
        })

        if return_type == int:
            return friends.count()

        return friends


    def get_settlements(self, qualifier=None, return_type=None):
        """ By default, this returns all settlements created by the user. Use
        the qualifiers thus:

            'player' - returns all settlements where the user is a player or
                admin or whatever. This casts the widest possible net.
            'admin' - returns only the settlements where the user is an admin
                but is NOT the creator of the settlement.

        """

        if qualifier is None:
            settlements = utils.mdb.settlements.find({"created_by": self.user["_id"]})
        elif qualifier == "player":
            settlement_id_set = set()

            survivors = self.get_survivors(qualifier="player")
            for s in survivors:
                settlement_id_set.add(s["settlement"])

            settlements_owned = self.get_settlements()
            for s in settlements_owned:
                settlement_id_set.add(s["_id"])

            settlements = utils.mdb.settlements.find({"_id": {"$in": list(settlement_id_set)}})

        elif qualifier == "admin":
            settlements = utils.mdb.settlements.find({
                "admins": {"$in": [self.user["login"]]},
                "created_by": {"$ne": self.user["_id"]},
            })
        else:
            raise Exception("'%s' is not a valid qualifier for this method!" % qualifier)

        if return_type == int:
            return settlements.count()

        return settlements


    def get_survivors(self, qualifier=None, return_type=None):
        """ Returns all of the settlements created by the user. """

        if qualifier is None:
            survivors = utils.mdb.survivors.find({"created_by": self.user["_id"]})
        elif qualifier == "player":
            survivors = utils.mdb.survivors.find({"$or":
                [
                    {"created_by": self.user["_id"]},
                    {"email": self.user["login"]},
                ]
            })
        elif qualifier == "owner":
            survivors = utils.mdb.survivors.find({
                "email": self.user["login"],
                "created_by": {"$ne": self.user["_id"]},
            })
        else:
            raise Exception("'%s' is not a valid qualifier for this method!" % qualifier)

        if return_type == int:
            return survivors.count()

        return survivors


    #
    #   Do not write model methods below this one.
    #

    def request_response(self, action=None):
        """ Initializes params from the request and then response to the
        'action' kwarg appropriately. This is the ancestor of the legacy app
        assets.Survivor.modify() method. """

        self.get_request_params()

        if action == "get":
            return self.get_json()
        else:
            # unknown/unsupported action response
            self.logger.warn("Unsupported survivor action '%s' received!" % action)
            return utils.http_400


        # finish successfully
        return utils.http_200





# ~fin
