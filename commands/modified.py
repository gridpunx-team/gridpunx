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

# Used by default commands in source code.
from django.conf import settings
from evennia.utils import utils

# Also used by default commands.
COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)


# ==============================================================
# ==
# == CmdGive - The '@give' command. Modified to for gridpunx to 
# == check a 'receive' access_type lock.
# ==
# == From Evennia source file: 
# == evennia/evennia/commands/default/general.py
# ==
# ==============================================================

class CmdGive(COMMAND_DEFAULT_CLASS):
    """
    give away something to someone
    Usage:
      give <inventory obj> <-to||=> <target>
    Gives an item from your inventory to another character, NPC,
    or container.
    """
    
    
    key = "give"
    rhs_split = ("=", " -to ")  # Prefer '=' delimiter, but allow '-to' usage.
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement give"""

        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Usage: give <inventory object> -to <target>")
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


# ==============================================================
# ==
# == CmdGet - The '@get' command. Modified for gridpunx to allow
# == specifying a target object which contains other objects.
# ==
# == From Evennia source file: 
# == evennia/evennia/commands/default/general.py
# ==
# ==============================================================

class CmdGet(COMMAND_DEFAULT_CLASS):
    """
    pick up something

    Usage:
      get <object> [=||-from <container>]

    Picks up an object and puts it in your inventory. Specify
    '-from <container>' or '= <container>' to get an item from a
    container. If no container is specified, the target defaults
    to 'here'
    """
    
    key = "get"
    aliases = "grab"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    # MODIFICATION (start)
    #
    # Parse args a similar way to how '@give' works
    rhs_split = ("=", " -from ")  # Prefer '=' delimiter, but allow '-from' usage.
    # MODIFICATION (end)

    def func(self):
        """implements the command."""

        caller = self.caller

        # MODIFICATION (start)
        # Show simple help if there are no args
        if not self.args:
            caller.msg("Usage: get <object> [= <target>]")
            return

        if not self.rhs:
            # Set target to 'here' if not specified.
            target = caller.location
        else:
            target = caller.search(self.rhs, location=caller.location)

        if not target:
            return
        if not (str(target.typename) == "RealContainer" or target.location == None ):
            # Only allowed on container objects (verified by typename) and rooms (verified by location -- only rooms have a 'None' location)
            caller.msg("You can only get objects from containers and the ground.")
            return

        obj = caller.search(
            self.lhs,
            location=target,
            nofound_string="There's no %s in here." % self.lhs,
            multimatch_string="There's more than one %s:" % self.lhs,
        )
        # MODIFICATION (end)

        # Unused original code:
        #
        #if not self.args:
        #    caller.msg("Get what?")
        #    return
        # obj = caller.search(self.args, location=caller.location)
        
        if not obj:
            return
        if caller == obj:
            caller.msg("You can't get yourself.")
            return
        if not obj.access(caller, "get"):
            if obj.db.get_err_msg:
                caller.msg(obj.db.get_err_msg)
            else:
                caller.msg("You can't get that.")
            return

        # calling at_before_get hook method
        if not obj.at_before_get(caller):
            return
        
        success = obj.move_to(caller, quiet=True)
        if not success:
            caller.msg("This can't be picked up.")
        else:
            caller.msg("You pick up %s." % obj.name)
            caller.location.msg_contents(
                "%s picks up %s." % (caller.name, obj.name), exclude=caller
            )
            # calling at_get hook method
            obj.at_get(caller)
