#!/usr/bin/python2.7


from optparse import OptionParser
import os
import sys
import time

import utils
from models import monster



#
#   This is an admin script and does not contain any classes that should be
#   initialized or used by other parts of the API application (or the webapp).
#
#   If you don't know what you're doing, you should probably stay out of here,
#   as this script has the potential to create massive havoc in the MDB if used
#   incorrectly.
#
#   YHBW
#



#
#   General purpose helper functions
#

def dump_doc_to_cli(m, tab_spaces=2, gap_spaces=20, buffer_lines=0):
    """ Convenience function for this collection of CLI admin scripts.
    Dumps a single MDB record to stdout using print() statements.

    Also works for dict objects. You know. Becuase they're the same thing.
    """

    tab = " " * tab_spaces
    buffer = "%s" % "\n" * buffer_lines

    print(buffer)

    for k in sorted(m.keys()):
        first_spacer = " " * (gap_spaces - len(k))
        second_spacer = " " * ((gap_spaces * 2) - len(str(m[k])))
        print("%s%s%s%s%s%s" % (tab, k, first_spacer, m[k], second_spacer, type(m[k])))


    print(buffer)



#
#   Administration objects - DANGER: KEEP OUT
#

class KillboardMaintenance:
    """ Initialize one of these and then use its methods to work on the
    mdb.killboard collection. """

    def __init__(self, search_criteria={"handle": {"$exists": False}}, force=False):
        self.logger = utils.get_logger()
        self.search_criteria = search_criteria
        self.force = force
        self.performance = {"success": 0, "failure": 0, "deferred": 0}
        print("\tInitializing maintenance object.")
        print("\tForce == %s" % self.force)
        print("\tSearch criteria: %s" % self.search_criteria)

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
                        print("\tUnable to update _id=%s" % doc["_id"])
                        print("Moving on...")
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
        dump_doc_to_cli(doc)

        # next, try to make a monster object out of it, for suggested changes
        try:
            m = monster.Monster(name=doc["name"])
        except:
            m = None
            print("\tMonster object could not be initialized!")


        # now check for a list of required attribs on the record and suggest
        #   recommended updates

        update_dict = {"raw_name": doc["name"]}
        for var in ["level","handle","comment","name"]:
            if m is not None:
                update_dict["type"] = m.__type__
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


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", dest="force", action="store_true", default=False, help="Skips interactive pauses.")
    parser.add_option("-K", dest="killboard", action="store_true", default=False, help="Clean up the Killboard.")
    (options, args) = parser.parse_args()

    if options.killboard:
        K = KillboardMaintenance(force=options.force)
        K.logger.warn("%s is performing mdb.killboard maintenance!" % os.environ["USER"])
        K.check_all_docs()
