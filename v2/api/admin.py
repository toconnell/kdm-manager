#!/usr/bin/python2.7

from bson.objectid import ObjectId
from collections import Counter, OrderedDict
from datetime import datetime, timedelta

from optparse import OptionParser
import os
import sys
import time

import utils
from models import monsters, users, settlements


#
#   This is an admin script and does not contain any classes that should be
#   initialized or used by other parts of the API application (or the webapp).
#
#   If you don't know what you're doing, you should probably stay out of here,
#   as the methods here have the potential to create massive havoc in the MDB if
#   used incorrectly.
#
#   YHBW
#



#
#   General purpose helper functions
#

def dump_survivor_to_cli(s_id):
    """ Dump a simplified representation of a survivor to the CLI buffer. """

    spacer = 30

    s = utils.mdb.survivors.find_one({'_id': s_id})
    print "  %s\t" % s['_id'],
    print "%s | %s" % (s['sex'], s['name']),
    print " " * (spacer - len(s['name'])),
    print "created: %s" % (s['created_on'].strftime(utils.ymd)),

    if s.get('removed',False):
        print "/ removed: %s" % (s['removed'].strftime(utils.ymd)),

    print

def dump_settlement_to_cli(s_id, verbose=False):
    """ Dump a simplified representation of a settlement dict 's' to the
    command line. """

    s = utils.mdb.settlements.find_one({'_id': s_id})

    if verbose:
        dump_doc_to_cli(s)
    else:
        s_repr = OrderedDict()
        for attr in ['_id','name','campaign','expansions','created_by','created_on']:
            try:
                s_repr[attr] = s[attr]
            except:
                s_repr[attr] = None
        dump_doc_to_cli(s_repr)

    if s.get('removed', False):
        print(' \x1b[1;31;40m Removed on %s \x1b[0m \n' % s['removed'])

    survivors = utils.mdb.survivors.find({'settlement': s['_id']})
    removed_survivors = utils.mdb.survivors.find({'settlement': s['_id'], 'removed': {'$exists': True}})
    print "  %s survivors found. %s have been removed.\n" % (survivors.count(), removed_survivors.count())

    for survivor in survivors:
        dump_survivor_to_cli(survivor['_id'])

    print


def dump_doc_to_cli(m, tab_spaces=2, gap_spaces=20, buffer_lines=0):
    """ Convenience function for this collection of CLI admin scripts.
    Dumps a single MDB record to stdout using print() statements.

    Also works for dict objects. You know. Becuase they're the same thing.
    """

    tab = " " * tab_spaces
    buffer = "%s" % "\n" * buffer_lines

    print(buffer)

    # respecognize ordered dict key order
    if type(m) == OrderedDict:
        keys = m.keys()
    else:
        keys = sorted(m.keys())

    for k in keys:
        first_spacer = " " * (gap_spaces - len(k))
        if gap_spaces >= 30:
            second_spacer = " " * (gap_spaces - len(str(m[k])))
        else:
            second_spacer = " " * ((gap_spaces * 2) - len(str(m[k])))
        print("%s%s%s%s%s%s" % (tab, k.decode('utf8'), first_spacer, m[k.decode('utf8')], second_spacer, type(m[k])))

    print(buffer)



#
#   Administration objects - DANGER: KEEP OUT
#

class KillboardMaintenance:
    """ Initialize one of these and then use its methods to work on the
    mdb.killboard collection. """

    def __init__(self, search_criteria={"$or": [{"handle": {"$exists": False}}, {"handle": "other"}]}, force=False):
        self.logger = utils.get_logger()
        self.search_criteria = search_criteria
        self.force = force
        self.performance = {"success": 0, "failure": 0, "deferred": 0}
        print("\tInitializing maintenance object.")
        print("\tForce == %s" % self.force)
        print("\tSearch criteria: %s" % self.search_criteria)


    def dump_others(self):
        """ Dump all killboard records whose handle is "other". """
        documents = utils.mdb.killboard.find({"handle": "other"})
        print("\n\tFound %s 'other' documents!\n" % documents.count())
        for d in documents:
            dump_doc_to_cli({
                "_id": d["_id"],
                "handle": d["handle"],
                "name": d["name"],
                "created_by": d["created_by"],
                "created_on": d["created_on"],
            })


    def check_all_docs(self):
        """ Counts how many docs match to self.search_criteria and then calls
        self.check_one_doc() until there are no more docs to check. """

        documents = utils.mdb.killboard.find(self.search_criteria)
        print("\n\t%s records match search criteria." % documents.count())

        if self.force:
            answer = raw_input("\tEnter 'Y' to process all records automatically: ")
            if answer == "Y":
                for d in documents:
                    try:
                        self.check_one_doc(d)
                    except Exception as e:
                        self.logger.exception(e)
                        self.performance["failure"] += 1
                        print("Update failed! Moving on...")
            else:
                print("\tExiting...\n")
                sys.exit(0)
        else:
            print("\tProcessing interactively...")
            for d in documents:
                self.check_one_doc(d)

        print("\n\tProcessed all records. Summary:\n")
        for k in sorted(self.performance.keys()):
            spacer = " " * (15 - len(k))
            print("\t%s%s%s" % (k, spacer, self.performance[k]))
        self.logger.info("Finished mdb.killboard update run. Results:")
        self.logger.info(self.performance)
        print("\nExiting...\n")
        sys.exit()


    def check_one_doc(self, doc, mode="interactive"):
        """ Pulls one record using self.search_criteria kwarg as a query and
        tries to initialize it as a monster object in order to suggest updates.
        Prompts to do another until there are none. """

        if doc is None:
            "No documents matching '%s' were found. Exiting..." % self.search_criteria

        # first, show the record
        print("\n\tFound one document!\n\tCurrent data:")
        try:
            dump_doc_to_cli(doc)
        except Exception as e:
            print doc
            return Exception

        # next, try to make a monster object out of it, for suggested changes
        try:
            m = monsters.Monster(name=doc["name"])
        except:
            m = None
            print("\tMonster object could not be initialized!")


        # now check for a list of required attribs on the record and suggest
        #   recommended updates

        update_dict = {"raw_name": doc["name"]}
        for var in ["level","handle","comment","name"]:
            if m is not None:
                update_dict["type"] = m.type
            elif m is None:
                update_dict["handle"] = "other"
            if hasattr(m, var):
                update_dict[var] = getattr(m, var)

        # try to normalize kill_ly

        try:
            if type(doc["kill_ly"]) == unicode:
                update_dict["kill_ly"] = int(doc["kill_ly"].split("_")[1])
        except:
            print("\tUnable to normalize 'kill_ly' value!")


        # now show all proposed updates
        print("\t%s recommended updates:" % len(update_dict))
        dump_doc_to_cli(update_dict)

        doc.update(update_dict)

        print("\tProposed record:")
        dump_doc_to_cli(doc)


        # depending on our run mode, we wrap up the operation by doing a few
        #   different things. If we're forcing, we accept the update as long as
        #   we were able to get a monster object. Otherwise, we defer.
        #   If we're running interactive, however, we let the user wither take
        #   the results or pass on them.

        if self.force:
            if m is None:
                self.performance["deferred"] += 1
            else:
                utils.mdb.killboard.save(doc)
                self.performance["success"] += 1
        else:
            answer = raw_input("\n\tSave new record to MDB? ").upper()
            if answer != "" and answer[0] == "Y":
                utils.mdb.killboard.save(doc)
                print("\tSaved updated record to MDB! Moving on...")
                self.performance["success"] += 1
            else:
                self.performance["deferred"] += 1
                print("\tDeferring update. Moving on...")

        # hang for a second at the end of the operation if we're running
        #   interactively (in order to show the user what has happened).
        if not self.force:
            time.sleep(1)



#
#   research and development helper methods and one-offs
#

def COD_histogram():
    """ Dumps a CLI histogram of survivor causes of death (for R&D purposes,
    mainly, but also useful in verifying world stats. """

    the_dead = utils.mdb.survivors.find({"dead": {"$exists": True}, "cause_of_death": {"$exists": True}})
    cod_list = []
    for s in the_dead:
        cod_list.append(s["cause_of_death"])
    c = Counter(cod_list)
    for c in c.most_common():
        print "%s|%s" % (c[1],c[0].encode('utf-8').strip())



#
#   one-off methods for CLI management of user subscriptions
#


def update_user(oid, level=None, beta=None, admin=None):
    """ Loads a user from the MDB, initializes it and calls the methods that set
    the patron level and the beta flag, etc. """

    if not ObjectId.is_valid(oid):
        print("The user ID '%s' is not a valid Object ID." % (oid))

    # initialize the user and show preferences
    U = users.User(_id=oid)

    # toggle admin if we're doing that
    if admin is not None:
        if 'admin' in U.user.keys():
            del U.user["admin"]
        else:
            U.user["admin"] = datetime.now()
        U.save()

    # now show me what you got
    print("\n Working with user \x1b[1;33;40m %s \x1b[0m [%s]" % (U.user['login'], U.user['_id']))
    U_serialized = U.serialize(dict)['user']
    mini_repr = OrderedDict()
    if 'admin' in U.user.keys():
        mini_repr['admin'] = U.user['admin']
    for time_attr in ['created_on','latest_sign_in', 'latest_activity']:
        mini_repr[time_attr] = utils.get_time_elapsed_since(U_serialized[time_attr], 'age')
    for attr in ['settlements_created','survivors_created']:
        mini_repr[attr] = U_serialized[attr]
    dump_doc_to_cli(mini_repr, gap_spaces=25)


    # coerce beta to a boolean
    if type(beta) == bool:
        pass
    elif beta is None:
        pass
    elif beta[0].upper() == 'T':
        beta = True
    else:
        beta = False

    # set patron attributes, if we're doing that
    if level is not None or beta is not None:
        print(" Updated subscriber attributes:")
        U.set_patron_attributes(level, beta)
        dump_doc_to_cli(U.user['patron'])

    if U.user['preferences'] != {}:
        print(' User Preferences:')
        dump_doc_to_cli(U.user['preferences'], gap_spaces=35)


def get_user_id_from_email(email):
    """ Pulls the user from the MDB (or dies trying). Returns its email. """

    u = utils.mdb.users.find_one({'login': email.lower().strip()})
    if u is None:
        raise Exception("Could not find user data for %s" % email)
    return u['_id']


#
#   work with settlement methods
#


def unremove_settlement(s_id):
    """ Un-sets 'removed' on the settlement and all of its survivors.

    We have to initialize the settlement to do this and we have to initialize
    whatever survivors need to be un-removed as well, so this one is here (and
    not exposed via API) because it's never going to be efficient/pretty.
    """

    S = settlements.Settlement(_id=s_id)

    if not S.settlement.get("removed",False):
        print("  Settlement '%s' [%s] has not been removed!\n  Aborting unremove request...\n" % (S.settlement['name'], s_id))
        return False

    proceed = raw_input(" \x1b[1;33;40m Unremove this settlement (including all removed survivors)? [N/y] \x1b[0m ")
    if len(proceed) > 0 and proceed.upper()[0] == "Y":
        proceed = True
    else:
        proceed = False

    if not proceed:
        print("\n  Aborting unremove request...\n")
        return False

    print("\n  Unremoving settlement...")
    S.unremove(unremove_survivors=True)
    time.sleep(1)
    print "   done!\n"
    time.sleep(1)
    dump_settlement_to_cli(s_id)




#
#   API Response Time record methods/helpers
#

def remove_api_response_data():
    """ Drops all documents from the mdb.api_response_times collection."""
    removed = utils.mdb.api_response_times.remove()
    print("\n  Removed %s API response time records." % removed)



#
#   Misc. research
#


def dump_removed_settlements():
    """ Dumps a digest/summary of info about settlements that have been marked
    removed. """

    settlements = utils.mdb.settlements.find({'removed': {'$exists': True}})
    if settlements.count() == 0:
        print('\n No removed settlements in MDB!\n')
        return True

    s_index = 0
    while s_index != settlements.count():
        s = settlements[s_index]

        # print a spacer from the second settlement onward
        if s_index > 0:
            print " ", "-" * 80

        dump_settlement_to_cli(s['_id'])
        s_index += 1


def dump_subscriber_info():
    """ Dumps generic subscription stats/info. """
    subscribers = utils.mdb.users.find({'patron': {'$exists': True}})
    print("\n %s subscribers:" % subscribers.count())
    for level in sorted(subscribers.distinct("patron.level")):
        print("  %s level %s" % (utils.mdb.users.find({'patron.level': level}).count(), level))
    print



if __name__ == "__main__":
    parser = OptionParser()

    # work with Settlements
    parser.add_option("-S", dest="work_with_settlement", default=None, help="Work with a settlement.", metavar="5a1485164af5ca67035bea03")
    parser.add_option('--unremove', dest="unremove_settlement", default=False, help="Use with -S to un-remove a settlement and any removed survivors in that settlement.", action="store_true")

    # Work with Users / manage subscriptions
    parser.add_option("-U", dest="work_with_user", default=None, help="Work with a user.", metavar="demo@kdm-manager.com")
    parser.add_option("--level", dest="user_level", default=None, metavar=2, help="Use with -U to set a user's patron/subscriber level.")
    parser.add_option("--beta", dest="user_beta", default=None, metavar="True", help="Use with -U to set a user's Beta preference.")
    parser.add_option("--admin", dest="user_admin", default=None, action="store_true", help="Use with -U to toggle a user's 'admin' status on/off.")

    # work with API response times
    parser.add_option("-A", dest="work_with_api_response_data", default=False, action="store_true", help="Work with API response time data.")
    parser.add_option("--reset_api_response_data", dest="reset_api_response_data", action="store_true", default=False, help="Use with -A to remove ALL DOCUMENTS from the mdb.api_response_times collection.")

    # Killboard
    parser.add_option("-K", dest="killboard", action="store_true", default=False, help="Clean up the Killboard.")
    parser.add_option("-o", dest="others", action="store_true", default=False, help="Use with -K to dump killboard entries whose handle is 'other'. Prevents -K from making any changes.")

    # misc research/admin
    parser.add_option("--removed_settlements", dest="dump_removed_settlements", action="store_true", default=False, help="Dump a summary of all removed settlements in mdb.")
    parser.add_option("--subscriptions", dest="subscribers", action="store_true", default=False, help="Dump subscriber stats")
    parser.add_option("--cod_histogram", dest="cod_histo", action="store_true", default=False, help="Dump a histogram of causes of death.")

    # meta
    parser.add_option("-f", dest="force", action="store_true", default=False, help="Skips interactive pauses.")
    parser.add_option("-v", dest="verbose", action="store_true", default=False, help="Incrases verbosity of certain types of output. Use with -S for full settlement details (rather than a summary), for example.")

    (options, args) = parser.parse_args()



    # work with settlements
    if options.work_with_settlement is not None:
        s_id = ObjectId(options.work_with_settlement)
        dump_settlement_to_cli(s_id, verbose=options.verbose)
        if options.unremove_settlement:
            unremove_settlement(s_id)

    # work with user
    if options.work_with_user is not None:
        if ObjectId.is_valid(options.work_with_user) and not '@' in options.work_with_user:
            user_oid = ObjectId(options.work_with_user)
        else:
            # assume it's an email if it's not an oid
            user_oid = get_user_id_from_email(options.work_with_user)

        update_user(user_oid, level=options.user_level, beta=options.user_beta, admin=options.user_admin)


    # manage API response times data
    if options.work_with_api_response_data and options.reset_api_response_data:
        remove_api_response_data()

    # killboard admin
    if options.killboard:
        K = KillboardMaintenance(force=options.force)
        K.logger.warn("%s is performing mdb.killboard maintenance!" % os.environ["USER"])
        if options.others:
            K.dump_others()
        else:
            K.check_all_docs()

    # misc research and admin
    if options.dump_removed_settlements:
        dump_removed_settlements()
    if options.subscribers:
        dump_subscriber_info()
    if options.cod_histo:
        COD_histogram()

