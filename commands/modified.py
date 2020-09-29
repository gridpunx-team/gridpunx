"""
Modified Commands

Commands defined here are modified versions of Evennia's default commands.


COPYRIGHT NOTICE:
Commands here are taken directly from the Evennia source for default commands.
(typically: evennia/evennia/commands/default/general.py).

Copyright (c) 2012-, Griatch (griatch <AT> gmail <DOT> com), Gregory Taylor
All rights reserved.
See NOTICE.txt file for full Evennia license details.


MODIFICATIONS:
Copyright (c) 2020, Michael J. Freidel
All rights reserved.
See LICENSE file for full gridpunx license details.

"""


# Used by modified default commands.
from django.conf import settings
from evennia.utils import utils

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

class CmdGive(COMMAND_DEFAULT_CLASS):
    """
    give away something to someone
    Usage:
      give <inventory obj> <to||=> <target>
    Gives an items from your inventory to another character,
    placing it in their inventory.
    """
    

    key = "give"
    rhs_split = ("=", " to ")  # Prefer = delimiter, but allow " to " usage.
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement give"""

        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Usage: give <inventory object> = <target>")
            return
        to_give = caller.search(
            self.lhs,
            location=caller,
            nofound_string="You aren't carrying %s." % self.lhs,
            multimatch_string="You carry more than one %s:" % self.lhs,
        )
        target = caller.search(self.rhs)
        if not (to_give and target):
            return
        if target == caller:
            caller.msg("You keep %s to yourself." % to_give.key)
            return
        if not to_give.location == caller:
            caller.msg("You are not holding %s." % to_give.key)
            return

        # MODIFICATION (start)
        # Add a check for "receive" access_type
        if not target.access(caller, "receive"):
            caller.msg("%s cannot receive things." % target.key)
            return
        # MODIFICATION (end)

        # calling at_before_give hook method
        if not to_give.at_before_give(caller, target):
            return

        # give object
        success = to_give.move_to(target, quiet=True)
        if not success:
            caller.msg("This could not be given.")
        else:
            caller.msg("You give %s to %s." % (to_give.key, target.key))
            target.msg("%s gives you %s." % (caller.key, to_give.key))
            # Call the object script's at_give() method.
            to_give.at_give(caller, target)

