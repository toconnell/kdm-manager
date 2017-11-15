#!/usr/bin/python2.7

from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask import Response, request
from hashlib import md5
import json
import jwt
import os
import random
import socket
import string
from werkzeug.security import safe_str_cmp

import Models
from settlements import Settlement
import user_preferences
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

    if username is None or password is None:
        return None

    user = utils.mdb.users.find_one({"login": username})
    if user is not None and safe_str_cmp(user["password"], md5(password).hexdigest()):
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
    referred to, in the field, as "meh--good enough" security.

    If you find yourself getting None back from thi sone, it's because your
    user changed his password.
    """

    decoded = jwt.decode(expired_token, secret_key, verify=False)
    user = dict(json.loads(decoded["identity"]))
    login = user["login"]
    pw_hash = user["password"]

    return utils.mdb.users.find_one({"login": login, "password": pw_hash})


def reset_password():
    """ Checks out an incoming recovery code and, if everything looks OK, loads
    up the user, changes its password, removes the code from the user and saves
    it back to the mdb. """

    user_login = request.get_json().get('username', None)
    new_password = request.get_json().get('password', None)
    recovery_code = request.get_json().get('recovery_code', None)

    for v in [user_login, new_password, recovery_code]:
        if v is None:
            return Response(response="Password reset requests require a login, password and a recovery code.", status=400)

    user = utils.mdb.users.find_one({'login': user_login, 'recovery_code': recovery_code})
    if user is None:
        return Response(response="The recovery code '%s' does not appear to be valid for '%s'." % (recovery_code, user_login))

    U = User(_id = user["_id"])
    del U.user['recovery_code']
    U.update_password(new_password)
    return utils.http_200


def initiate_password_reset():
    """ Attempts to start the mechanism for resetting a user's password.
    Unlike a lot of methods, this one handles the whole request processing and
    is very...self-contained. """

    # first, validate the post
    user_login = request.get_json().get('username', None)
    if user_login is None:
        return Response(
            response="A valid user email address must be included in password reset requests!",
            status=400
        )

    # next, validate the user
    user = utils.mdb.users.find_one({"login": user_login})
    if user is None:
        return Response(
            response="'%s' is not a registered email address." % user_login,
            status=404
        )

    # if the user looks good, set the code
    U = User(_id=user["_id"])
    user_code = U.set_recovery_code()

    # finally, send the email to the user
    try:
        tmp_file = os.path.join(settings.get("api","cwd"), "html/password_recovery.html")
        msg = string.Template(file(tmp_file, "rb").read())
        msg = msg.safe_substitute(login=user_login, recovery_code=user_code, app_url=utils.get_application_url())
        e = utils.mailSession()
        e.send(recipients=[user_login], html_msg=msg)
    except Exception as e:
        logger.error(e)
        raise

    # exit 200
    return utils.http_200


def jwt_identity_handler(payload):
    """ Bounces the authentication request payload off of the user collection.
    Returns a user object if "identity" in the request exists. """

    u_id = payload["identity"]
    user = utils.mdb.users.find_one({"_id": ObjectId(u_id)})

    if user is not None:
        U = User(_id=user["_id"])
        return U.serialize()

    return utils.http_404




def token_to_object(request, strict=True):
    """ Processes the "Authorization" param in the header and returns an http
    response OR a user object. Requires the application's initialized JWT to
    work. """
    # khoa's back door - chop this whole block when he gets CORS sorted out
    if request.method == "POST" and request.json.get('user_id', None) is not None:
        logger.warn("'user_id' key in POST body; attempting Khoa-style token-less auth...")
        try:
            user_oid = ObjectId(request.json['user_id'])
        except Exception as e:
            msg = "User OID '%s' does not look like an OID!" % request.json['user_id']
            logger.error(msg)
            logger.error(e)
            raise utils.InvalidUsage(msg, status_code=422)
        try:
            return User(_id=user_oid)
        except Exception as e:
            msg = "The OID '%s' does not belong to any known user! %s" % (user_oid, e)
            logger.error(msg)
            raise utils.InvalidUsage(msg, status_code=401)


    #   real auth workflow starts here
    # first, get the token or bail
    auth_token = request.headers.get("Authorization", None)
    if auth_token is None:
        msg = "'Authorization' header missing!"
        logger.error(msg)
        raise utils.InvalidUsage(msg, status_code=401)

    # now, try to decode the token and get a dict
    try:
        decoded = jwt.decode(auth_token, secret_key, verify=strict)
        user_dict = dict(json.loads(decoded["identity"]))
        return User(_id=user_dict["_id"]["$oid"])
    except jwt.DecodeError:
        logger.error("Incorrectly formatted token!")
        logger.error("Token contents: |%s|" % auth_token)
    except Exception as e:
        logger.exception(e)

    raise utils.InvalidUsage("Incoming JWT could not be processed!", status_code=422)



#
#   The big User object starts here
#

class User(Models.UserAsset):
    """ This is the main controller for all user objects. """

    def __repr__(self):
        return "[%s (%s)]" % (self.user["login"], self._id)


    def __init__(self, *args, **kwargs):
        self.collection="users"
        self.object_version=0.22
        Models.UserAsset.__init__(self,  *args, **kwargs)

        # JWT needs this
        self.id = str(self.user["_id"])

        # baseline/normalize
        self.normalize()

        # random initialization methods
        self.set_current_settlement()

        # assets
        self.Preferences = user_preferences.Assets()


    def new(self):
        """ Creates a new user based on request.json values. Like all UserAsset
        'new()' methods, this one returns the new user's MDB _id when it's done.
        """

        self.logger.info("Creating new user...")
        self.check_request_params(['username','password'])

        # clean up the incoming values so that they conform to our data model
        username = self.params["username"].strip().lower()
        password = self.params["password"].strip()

        # do some minimalistic validation (i.e. rely on front-end for good data)
        #   and barf if it fails #separationOfConcerns

        msg = "The email address '%s' does not appear to be a valid email address!" % username
        if not '@' in username:
            raise utils.InvalidUsage(msg)
        elif not '.' in username:
            raise utils.InvalidUsage(msg)

        # make sure the new user doesn't already exist

        msg = "The email address '%s' is already in use by another user!" % username
        if utils.mdb.users.find_one({'login': username}) is not None:
            raise utils.InvalidUsage(msg)


        # now do it
        self.user = {
            'created_on': datetime.now(),
            'login': username,
            'password': md5(password).hexdigest(),
            'preferences': {},
        }
        self._id = utils.mdb.users.insert(self.user)
        self.load()
        logger.info("New user '%s' created!" % username)

        return self.user["_id"]


    def serialize(self, return_type=None):
        """ Creates a dictionary meant to be converted to JSON that represents
        everything that the front-end might need to know about a user. """

        output = self.get_serialize_meta()

        # check if this is an application admin
        if 'admin' in self.user.keys():
            output['is_application_admin'] = True

        # now create the user dict (analogous to 'sheet' in asset exports)
        output["user"] = self.user

        # basics; all views, generic UI/UX stuff
        output["user"]["age"] = self.get_age()
        output["user"]["settlements_created"] = utils.mdb.settlements.find({'created_by': self.user['_id']}).count()
        output['user']['subscriber'] = self.get_patron_attributes()
        output["preferences"] = self.get_preferences()

        # items common to dashboard and admin_panel
        if return_type in ['dashboard']:
            output["dashboard"] = {}
#            output["dashboard"]["friends"] = self.get_friends(return_type=list)
            output["dashboard"]["campaigns"] = self.get_settlements(return_type='list_of_dicts', qualifier='player')
            output["dashboard"]["settlements"] = self.get_settlements(return_type='list_of_dicts')

        # punch the user up if we're returning to the admin panel
        if return_type in ['admin_panel']:
            output['user']["latest_activity_age"] = self.get_latest_activity(return_type='age')
            output["user"]["has_session"] = self.has_session()
            output["user"]["is_active"] = self.is_active()
            output['user']["friend_list"] = self.get_friends(list)
            output['user']["current_session"] = utils.mdb.sessions.find_one({"_id": self._id})
            output["user"]["survivors_created"] = self.get_survivors(return_type=int)
            output["user"]["survivors_owned"] = self.get_survivors(qualifier="owner", return_type=int)
            output["user"]["settlements_administered"] = self.get_settlements(qualifier="admin", return_type=int)
            output["user"]["campaigns_played"] = self.get_settlements(qualifier="player", return_type=int)

        # user assets
#        output["user_assets"] = {}
#        output["user_assets"]["survivors"] = self.get_survivors(return_type=list)


        if return_type in ['admin_panel','create_new']:
            return output

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
        failed_keys = []
        success_keys = []

        # first, check the keys to see if they're legit; bail if any of them is
        #   bogus, i.e. bail before we attempt to do anything.
        for k in self.params.keys():
            if k not in allowed_keys:
                self.logger.warn("Unknown key '%s' will not be processed!" % k)
                failed_keys.append(k)
            else:
                success_keys.append(k)

        # now, individual value handling for allow keys begins
        for k in success_keys:
            if k == "current_settlement":
                self.user[k] = ObjectId(self.params[k])
            else:
                self.user[k] = self.params[k]
            self.logger.debug("Set {'%s': '%s'} for %s" % (k, self.params[k], self))

        # build the response message
        msg = "OK!"
        if len(success_keys) >= 1:
            msg += " User attributes successfully updated: %s." % (utils.list_to_pretty_string(success_keys, quote_char="'"))
        if len(failed_keys) >= 1:
            msg += " The following user attributes are NOT supported and could not be updated: %s." % (utils.list_to_pretty_string(failed_keys, quote_char="'"))

        # finally, assuming we're still here, go ahead and save/return 200
        self.save()

        return Response(response=msg, status=200)


    def set_current_settlement(self):
        """ This should probably more accurately be called 'default_current_settlement'
        or something along those lines, because it basically tries a series of
        back-offs to set a settlement for a user who hasn't got one set. """

        if "current_settlement" in self.user.keys():
            return True

        settlements = self.get_settlements()
        if len(settlements) != 0:
            self.user["current_settlement"] = settlements[0]["_id"]
            self.logger.warn("Defaulting 'current_settlement' to %s for %s" % (settlements[0]["_id"], self))
        elif len(settlements) == 0:
            self.logger.debug("User %s does not own or administer any settlements!" % self)
            p_settlements = self.get_settlements(qualifier="player")
            if len(p_settlements) != 0:
                self.user["current_settlement"] = p_settlements[0]["_id"]
                self.logger.warn("Defaulting 'current_settlement' to %s for %s" % (p_settlements[0]["_id"], self))
            elif len(p_settlements) == 0:
                self.logger.warn("Unable to default a 'current_settlement' value for %s" % self)
                self.user["current_settlement"] = None

        self.save()


    def set_patron_attributes(self, level=0, beta=None):
        """ Updates the user's self.user['patron'] dictionary: sets the level
        (int) and the beta flag (bool)."""

        if not 'patron' in self.user.keys():
            self.user['patron'] = {'created_on': datetime.now()}

        if 'beta' in self.user['patron'].keys():
            del self.user['patron']['beta']
        self.user['patron']['updated_on'] = datetime.now()
        self.user['patron']['level'] = level

        if beta is not None:
            self.user['preferences']['beta'] = beta

        if level == 0:
            self.user['patron']['desc'] = None
        elif level == 1:
            self.user['patron']['desc'] = 'Survival +1'
        elif level == 2:
            self.user['patron']['desc'] = 'Survival +5'

        self.logger.info("%s Set patron level to %s; set beta access to %s." % (self, level, beta))
        self.save()


    def set_preferences(self):
        """ Expects a request context and will not work without one. Iterates
        thru a list of preference handles and sets them. """

        self.check_request_params(['preferences'])
        pref_list = self.params['preferences']
        if type(pref_list) != list:
            raise utils.InvalidUsage("set_preferences() endpoint requires 'preferences' to be a list!")

        for pref_dict in pref_list:
            handle = pref_dict['handle']
            value = pref_dict['value']
            self.user['preferences'][handle] = value
            self.logger.info("%s Set '%s' = %s'" % (request.User.login, handle, value))

        self.save()


    def set_recovery_code(self):
        """ Sets self.user['recovery_code'] to a random value. Returns the code
        when it is called. """

        r_code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(30))
        self.user["recovery_code"] = r_code
        self.logger.info("'%s set recovery code '%s' for their account" % (self, r_code))
        self.save()
        return self.user["recovery_code"]


    def update_password(self, new_password=None):
        """ Changes the user's password. Saves. """

        if new_password is None:
            self.check_request_params(['password'])
            new_password = self.params['password']

        if new_password is None:
            raise Exception("New password cannot be None type!")

        self.user['password'] = md5(new_password).hexdigest()
        self.logger.warn("%s Changed password!" % self)
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

        minutes_since_latest = self.get_latest_activity('minutes')
        active_horizon = settings.get("application","active_user_horizon")
        if minutes_since_latest <= active_horizon:
            return True

        return False



    #
    #   get methods
    #

    def get_age(self, return_type="years"):
        """ Returns the user's age. """

        return utils.get_time_elapsed_since(self.user["created_on"], 'age')


    def get_patron_attributes(self):
        """ Returns a dictionary of patronage information. """

        if 'patron' not in self.user.keys():
            return {'level': 0, 'beta': False}

        self.user['patron'].update({'age': utils.get_time_elapsed_since(self.user['patron']['created_on'], 'age')})
        return self.user['patron']


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


    def get_preferences(self):
        """ Not to be confused with self.get_preference(), which gets a bool for
        a single preference handle, this renders a JSON-ish return meant to be
        included in the self.serialize() call (and ultimately represented on the
        application dashboard. """

        groups = set()
        for p_dict in self.Preferences.get_dicts():
            groups.add(p_dict['sub_type'])

        output = []
        for g_name in sorted(groups):
            g_handle = g_name.lower().replace(" ","_")
            g_dict = {'name': g_name, 'handle': g_handle, 'items': []}
            for p_dict in self.Preferences.get_dicts():
                if p_dict['sub_type'] == g_name:
                    election = self.get_preference(p_dict['handle'])
                    p_dict['value'] = election
                    g_dict['items'].append(p_dict)
            output.append(g_dict)

        return output


    def get_friends(self, return_type=None):
        """ Returns all of the user's friends (i.e. people he plays in campaigns
        with) as objects. """

        friend_ids      = set()
        friend_emails   = set()

        campaigns = self.get_settlements(qualifier="player")
        if len(campaigns) > 0:
            for s in campaigns:
                friend_ids.add(s["created_by"])
                c_survivors = utils.mdb.survivors.find({"settlement": s["_id"]})
                for survivor in c_survivors:
                    friend_ids.add(survivor["created_by"])
                    friend_emails.add(survivor["email"])

            # you can't be friends with yourself
            if self.user["_id"] in friend_ids:
                friend_ids.remove(self.user["_id"])
            if self.user["login"] in friend_emails:
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
        elif return_type == list:
            if friends is None:
                return []
            else:
                return [f["login"] for f in friends]

        return friends


    def get_latest_activity(self, return_type=None):
        """ Returns the user's latest activity in a number of ways. Leave the
        'return_type' kwarg blank for a datetime stamp.
        """

        la = self.user["latest_activity"]

        if return_type is not None:
            return utils.get_time_elapsed_since(la, return_type)

        return la


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


        # change settlements to a list so we can do python post-process
        settlements = list(settlements)


	# settlement age support/freemium wall
        # first, see if we even need to be here
        # MOVE ALL OF THIS OUT OF THIS METHOD ASAP
        sub_level = self.get_subscriber_level()
        if sub_level > 1:
            pass
	else:
#            self.logger.debug("%s Subscriber level is %s. Checking settlement asset ages..." % (self, sub_level))
            for s in settlements:
                asset_age = datetime.now() - s['created_on']
                if asset_age.days > settings.get('application','free_user_settlement_age_max'):
                    self.logger.warn("%s settlement '%s' is more than %s days old!" % (self, s['name'], settings.get('application','free_user_settlement_age_max')))
                    msg = utils.html_file_to_template('html/auto_remove_settlement.html')

                    # in case the admin panel hits it before the actual user
                    if not hasattr(request, 'User'):
                        request.User = utils.noUser()

                    msg = msg.safe_substitute(
                        settlement_name=s['name'],
                        settlement_age = asset_age.days,
                        settlement_dict = s,
                        user_email = request.User.login,
                        user_id = request.User._id,
                    )
                    e = utils.mailSession()
                    e.send(subject="Settlement auto-remove! [%s]" % socket.getfqdn(), recipients=settings.get('application','email_alerts').split(','), html_msg=msg)
                    s['removed'] = datetime.now()
                    utils.mdb.settlements.save(s)
                    settlements.remove(s)

        #
        # now start handling returns
        #

        if return_type == int:
            return len(settlements)
        elif return_type == list:
            output = [s["_id"] for s in settlements]
            return output
        elif return_type == 'list_of_dicts':
            return settlements
        elif return_type == "asset_list":
            output = []
            for s in settlements:
                try:
                    S = Settlement(_id=s["_id"], normalize_on_init=False)
                    sheet = json.loads(S.serialize('dashboard'))
                    output.append(sheet)
                except Exception as e:
                    logger.error("Could not serialize %s" % s)
                    logger.exception(e)
                    raise

            return output

        return settlements


    def get_subscriber_level(self):
        """ Returns the user's subscriber level as an int. """
        p = self.get_patron_attributes()
        return p['level']


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
    #   baseline/normalize
    #

    def normalize(self):
        """ Force/coerce the user into compliace with our data model for users. """

        self.perform_save = False

        if not 'preferences' in self.user.keys():
            self.user['preferences'] = {'preserve_sessions': False}
            self.logger.warn("%s has no 'preferences' attrib! Normalizing..." % self)
            self.perform_save = True


        if self.perform_save:
            self.save()




    #
    #   Do not write model methods below this one.
    #


    def request_response(self, action=None):
        """ Initializes params from the request and then response to the
        'action' kwarg appropriately. This is the ancestor of the legacy app
        assets.Survivor.modify() method. """

        self.get_request_params()

        if action == "get":
            return Response(response=self.serialize(), status=200, mimetype="application/json")
        elif action == "dashboard":
            return Response(response=self.serialize('dashboard'), status=200, mimetype="application/json")
        elif action == "set":
            return self.set_attrib()

        elif action == "update_password":
            self.update_password()
        elif action == 'set_preferences':
            self.set_preferences()

        else:
            # unknown/unsupported action response
            self.logger.warn("Unsupported survivor action '%s' received!" % action)
            return utils.http_400


        # finish successfully
        return Response(response="Completed '%s' action successfully!" % action, status=200)





# ~fin
