#!/usr/bin/python2.7

from bson import json_util
from bson.objectid import ObjectId
from flask import Response
from hashlib import md5
import json
import jwt
from werkzeug.security import safe_str_cmp

import Models
import settings
import utils



# laaaaaazy
logger = utils.get_logger()
secret_key = settings.get("api","secret_key","private")


#
#   JWT helper methods here!
#

def authenticate(username, password):
    """ Returns None unless a.) there's a real user for 'username' and b.) the
    MD5 hash of the user's password matches the hash of 'password', in which
    case we return a user document from the MDB. """

    user = utils.mdb.users.find_one({"login": username})
    if user and safe_str_cmp(user["password"], md5(password).hexdigest()):
        U = User(_id=user["_id"])
        return U

def check_authorization(token):
    """ Tries to decode 'token'. Returns an HTTP 200 if it works, returns a 401
    if it doesn't. """

    try:
        jwt.decode(token, secret_key, verify=True)
        return utils.http_200
    except Exception as e:
        decoded = json.loads(jwt.decode(token, secret_key, verify=False)["identity"])
        logger.info("[%s (%s)] authorization check failed: %s!" % (decoded["login"], decoded["_id"]["$oid"], e))
        return utils.http_401


def refresh_authorization(expired_token):
    """ Opens an expired token, gets the login and password hash, and checks
    those against mdb. If they match, we return the user. This is what is
    referred to, in the field, as "meh--good enough" security. """

    decoded = jwt.decode(expired_token, secret_key, verify=False)
    user = dict(json.loads(decoded["identity"]))
    login = user["login"]
    pw_hash = user["password"]

    return utils.mdb.users.find_one({"login": login, "password": pw_hash})


def jwt_identity_handler(payload):
    """ Bounces the authentication request payload off of the user collection.
    Returns a user object if "identity" in the request exists. """

    u_id = payload["identity"]
    user = utils.mdb.users.find_one({"_id": ObjectId(u_id)})

    if user is not None:
        U = User(_id=user["_id"])
        return U.serialize()

    return utils.http_404


def token_to_object(request):
    """ Processes the "Authorization" param in the header and returns an http
    response OR a user object. Requires the application's initialized JWT to
    work. """

    # first, get the token or bail

    auth_token = request.headers.get("Authorization", None)
    if auth_token is None:
        logger.error("Authorization header missing!")
        return utils.http_401

    # now, try to decode the token and get a dict

    try:
        decoded = jwt.decode(auth_token, secret_key)
        user_dict = dict(json.loads(decoded["identity"]))
        return User(_id=user_dict["_id"]["$oid"])
    except jwt.DecodeError:
        logger.error("Incorrectly formatted token!")
    except Exception as e:
        logger.exception(e)

    return utils.http_401




#
#   The big User object starts here
#

class User(Models.UserAsset):
    """ This is the main controller for all user objects. """

    def __init__(self, *args, **kwargs):
        self.collection="users"
        self.object_version=0.13
        Models.UserAsset.__init__(self,  *args, **kwargs)

        # JWT needs this
        self.id = str(self.user["_id"])

        # random initialization methods
        self.set_current_settlement()


    def __repr__(self):
        return "[%s (%s)]" % (self.user["login"], self._id)


    def serialize(self):
        """ Creates a dictionary meant to be converted to JSON that represents
        everything that the front-end might need to know about a user. """

        output = self.get_serialize_meta()
        output["user"] = self.user

        # user assets
#        output["user_stat"] = {}
        output["user_assets"] = {}
        output["user_assets"]["survivors"] = self.get_survivors(return_type=list)
        output["user_assets"]["settlements"] = self.get_settlements(return_type=list)

        # user facts
        output["user_facts"] = {}
        output["user_facts"]["has_session"] = self.has_session()
        output["user_facts"]["is_active"] = self.is_active()
        output["user_facts"]["settlements_created"] = self.get_settlements(return_type=int)
        output["user_facts"]["settlements_administered"] = self.get_settlements(qualifier="admin", return_type=int)
        output["user_facts"]["campaigns"] = self.get_settlements(qualifier="player", return_type=int)
        output["user_facts"]["survivors_created"] = self.get_survivors(return_type=int)
        output["user_facts"]["survivors_owned"] = self.get_survivors(qualifier="owner", return_type=int)
        output["user_facts"]["friend_count"] = self.get_friends(return_type=int)

        return json.dumps(output, default=json_util.default)


    def jsonize(self):
        """ Returns JSON of the user's MDB dict. """
        return json.dumps(self.user, default=json_util.default)


    #
    #   set/update/modify methods
    #

    def set_attrib(self):
        """ Parses and processes request JSON and attempts to set user attrib
        key/value pairs. Returns an http response. """

        allowed_keys = ["current_settlement"]

        # first, check the keys to see if they're legit; bail if any of them is
        #   bogus, i.e. bail before we attempt to do anything.
        for k in self.params.keys():
            if k not in allowed_keys:
                self.logger.warn("Unknown key '%s' will not be processed!" % k)
                return Response(response="Unknown user attribute '%s' cannot be set!" % k, status=400)

        # now, individual value handling for allow keys begins
        for k in self.params.keys():
            if k == "current_settlement":
                self.user[k] = ObjectId(self.params[k])
            else:
                self.user[k] = self.params[k]
            self.logger.debug("Set {'%s': '%s'} for %s" % (k, self.params[k], self))

        # finally, assuming we're still here, go ahead and save/return 200
        self.save()

        return utils.http_200


    def set_current_settlement(self):
        """ This should probably more accurately be called 'default_current_settlement'
        or something along those lines, because it basically tries a series of
        back-offs to set a settlement for a user who hasn't got one set. """

        if "current_settlement" in self.user.keys():
            return True

        settlements = self.get_settlements()
        if settlements.count() != 0:
            self.user["current_settlement"] = settlements[0]["_id"]
            self.logger.warn("Defaulting 'current_settlement' to %s for %s" % (settlements[0]["_id"], self))
        elif settlements.count() == 0:
            self.logger.debug("User %s does not own or administer any settlements!" % self)
            p_settlements = self.get_settlements(qualifier="player")
            if p_settlements.count() != 0:
                self.user["current_settlement"] = p_settlements[0]["_id"]
                self.logger.warn("Defaulting 'current_settlement' to %s for %s" % (p_settlements[0]["_id"], self))
            elif p_settlements.count() == 0:
                self.logger.warn("Unable to default a 'current_settlement' value for %s" % self)
                self.user["current_settlement"] = None

        self.save()



    #
    #   query/assess methods
    #

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



    #
    #   get methods
    #

    def get_preference(self, p_key):
        """ Ported from the legacy app: checks the user's MDB document for the
        'preference' key and returns its value (which is a bool).

        If the key is NOT present on the user's MDB document, return the default
        value from settings.cfg. """

        default_value = settings.get("users", p_key)

        if "preferences" not in self.user.keys():
            return default_value

        if p_key not in self.user["preferences"].keys():
            return default_value

        return self.user["preferences"][p_key]



    def get_friends(self, return_type=None):
        """ Returns all of the user's friends (i.e. people he plays in campaigns
        with) as objects. """

        friend_ids      = set()
        friend_emails   = set()

        campaigns = self.get_settlements(qualifier="player")
        if campaigns.count() > 0:
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
        else:
            friends = None

        if return_type == int:
            if friends is not None:
                return friends.count()
            else:
                return 0

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
            settlements = utils.mdb.settlements.find({"$or": [
                {"created_by": self.user["_id"], "removed": {"$exists": False}, },
                {"admins": {"$in": [self.user["login"], ]}, "removed": {"$exists": False}, },
            ]})
        elif qualifier == "player":
            settlement_id_set = set()

            survivors = self.get_survivors(qualifier="player")
            for s in survivors:
                settlement_id_set.add(s["settlement"])

            settlements_owned = self.get_settlements()
            for s in settlements_owned:
                settlement_id_set.add(s["_id"])
            settlements = utils.mdb.settlements.find({"_id": {"$in": list(settlement_id_set)}, "removed": {"$exists": False}})
        elif qualifier == "admin":
            settlements = utils.mdb.settlements.find({
                "admins": {"$in": [self.user["login"]]},
                "created_by": {"$ne": self.user["_id"]},
                "removed": {"$exists": False},
            })
        else:
            raise Exception("'%s' is not a valid qualifier for this method!" % qualifier)

        if return_type == int:
            return settlements.count()
        elif return_type == list:
            output = [s["_id"] for s in settlements]
            output = list(set(output))
            return output

        return settlements


    def get_survivors(self, qualifier=None, return_type=None):
        """ Returns all of the survivors created by the user. """

        if qualifier is None:
            survivors = utils.mdb.survivors.find({"$or": [
                {"created_by": self.user["_id"], "removed": {"$exists": False}},
                {"email": self.user["login"], "removed": {"$exists": False}},
            ]})

        elif qualifier == "player":
            survivors = utils.mdb.survivors.find({"$or": [
                {"created_by": self.user["_id"], "removed": {"$exists": False}},
                {"email": self.user["login"], "removed": {"$exists": False}},
            ]})
        elif qualifier == "owner":
            survivors = utils.mdb.survivors.find({
                "email": self.user["login"],
                "created_by": {"$ne": self.user["_id"]},
                "removed": {"$exists": False},
            })
        else:
            raise Exception("'%s' is not a valid qualifier for this method!" % qualifier)

        if return_type == int:
            return survivors.count()
        elif return_type == list:
            output = [s["_id"] for s in survivors]
            output = list(set(output))
            return output

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
            return self.return_json()
        elif action == "set":
            return self.set_attrib()
        else:
            # unknown/unsupported action response
            self.logger.warn("Unsupported survivor action '%s' received!" % action)
            return utils.http_400


        # finish successfully
        return utils.http_200





# ~fin
