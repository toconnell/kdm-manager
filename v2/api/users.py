#!/usr/bin/env python

from datetime import datetime
from hashlib import md5

import settings


class User():

    """ The User class contains all of our methods for manipulating users;
    initializing a new User object gives full access to mdb attribs, etc."""

    def __init__(self, _id=None, logger=None):
        """ Initialize a user object. """

        self.attribs = None
        if _id is not None:
            self.attribs = settings.MDB.users.find_one({"_id": _id})

        # every asset class should have one of these
        self.logger = logger
        if self.logger is None:
            self.logger = settings.default_logger


    def __repr__(self):
        """ If we're initialized with an actual user, our repr changes. If we
        are initialized with no user, do the normal repr. """
        if self.attribs is None:
            return "User object initialized without user data."
        else:
            return "'%s' (%s)" % (self.attribs["login"], self.attribs["_id"])


    def new(self, login=False, password=False, attribs={}, password_is_hashed=True):
        """ Inserts a new user into mdb based on provided kwargs. Any key/value
        pair passed to the 'attribs' kwarg will be added to the object's
        self.attribs. """

        if settings.MDB.users.find_one({"login": login}) is not None:
            self.logger.warn("Unable to create user '%s': the login already exists!" % login)
            return None

        if not password_is_hashed:
            password = md5(password).hexdigest()

        new_user = {
            "role": ["user"],
            "active": True,
            "login": login,
            "password": password,
            "created_on": datetime.now(),
            "preferences": {},
            "user_agents": [],
        }
        for k,v in attribs.iteritems():
            new_user[k] = v
        user_id = settings.MDB.users.insert(new_user)
        settings.MDB.users.create_index("login", unique=True)

        self.__init__(_id=user_id)
        self.logger.info("Created new user %s" % self)

        return True


    def update(self, update_dict=None):
        """ Updates a user from a dictionary. Returns True if it succeeds;
        returns False if it fails for some reason. """
        if type(update_dict) == dict and update_dict != {}:
            for k, v in update_dict.iteritems():
                self.attribs[k] = v
            settings.MDB.users.save(self.attribs)
            self.logger.debug("Updated %s: %s keys modified." % (self, len(update_dict.keys())))
            return True
        else:
            return False


    def remove_attrib(self, k):
        """ Removes/deletes a key/value pair from a user's mdb entry. Returns
        True if it works, returns None if there's nothing to delete/remove. """
        if k in self.attribs.keys():
            del self.attribs[k]
            self.logger.debug("Removed '%s' key from %s" % (k,self))
            return True
        else:
            return None


    def authenticate(self, login, password, password_is_hashed=True):
        """ Tries to authenticate a user based on login and password. Initializes
        a new User obejct if successful.

        Returns True if everything goes according to plan; returns False if
        something fails.

        Returns None if the user is bogus. """

        if not password_is_hashed:
            password = md5(password).hexdigest()

        mdb_user = settings.MDB.users.find_one({"login": login})
        if mdb_user is None:
            self.logger.debug("No such user as '%s'" % login)
            return None
        elif mdb_user["password"] != password:
            self.logger.warn("Could not authenticate '%s' (bad password)." % login)
            return False
        else:
            self.__init__(_id=mdb_user["_id"])
            self.attribs["last_sign_in"] = datetime.now()
            settings.MDB.users.save(self.attribs)
            self.logger.debug("%s authenticated successfully." % self)
            return True


if __name__ == "__main__":
    print("Unit tests here?")
