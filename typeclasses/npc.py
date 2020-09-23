"""
npc.py

Copyright Notice:
The code here is largely based on Evennia's contribution module
for a talking NPC object (talking_npc.py).

Evennia Talkative NPC

Contribution - Griatch 2011, grungies1138, 2016

Modifications - Copyright 2020, Michael J. Freidel under the BSD 3-Clause License (See LICENSE file)

Description:
This is a custom typeclass file for gridppunx. Classes defined 
here are meant to be used for objects that represent interactive
characters with dialogue trees. They may be friendly or hostile, 
but all should have the ability to talk with a player. 
Alternatively, NPC objects here may be designed to be puppeted 
by a GameMaster or Builder.
"""


from evennia import CmdSet, default_cmds
from evennia.utils.evmenu import EvMenu
from typeclasses.objects import RealObject


# ==============================================================
# ==
# == Example Dialogue -- Goes nowhere, does nothing.
# ==
# ==============================================================

def dialogue_start(caller):
    text = "'I don't have anything to say.'"

    options = (
        {"desc": "OK", "goto": "END"}
    )

    return text, options


def END(caller):
    text = "'Goodbye.'"

    options = ()

    return text, options


# ==============================================================
# ==
# == The 'talk' command (sits on talking NPC objects)
# ==
# ==============================================================

class CmdTalk(default_cmds.MuxCommand):
    """
    Talks to an NPC

    Usage:
    talk

    This command is only available if a talkative non-player-character
    (NPC) is actually present. It will strike up a conversation with
    that NPC and give you options on what to talk about.
    
    Note:
    This simple command is designed to be attached to Objects, and *not* 
    Characters or Sessions. This means that multiple instances of this 
    command will be available when multiple NPCs are in the same room.
    When this happens, issuing "talk" in the room will ask the caller 
    to narrow the target. The caller must then choose 1-talk, 2-talk, etc, 
    according to the displayed target options.
    """

    key = "talk"
    locks = "cmd:all()"
    help_category = "General" 

    def func(self):
        """
        Implements the command in a way which allows for adding new 
        NPCs with their own unique dialogue trees. This is accomplished 
        by passing a dynamically assigned module path to EvMenu. See 
        documentation for RealTalkingNPC for details about adding new NPCs.
        """
        
        # This is weird... but it works!
        dialogue_module = str(self.obj.typeclass_path.rstrip(self.obj.typename).rstrip("."))
        # This dynamically assigns the module path of the dialogue tree
        # based on the typeclass_path of the object it is assigned to.
        # Steps:
        # 1. Ensure it's a string.
        # 2. Remove the object's typename from the object's typeclass_path.
        # 3. Remove the remaining dot.

        # self.obj is the NPC object this command is defined on.
        self.caller.msg("(You walk up and talk to %s.)" % self.obj.key)
        
        # Initiate the menu by passing the object's module path to it.
        EvMenu(self.caller, dialogue_module, startnode="dialogue_start")
        # All dialogue trees must start at a function named 'dialogue_start'

class TalkingCmdSet(CmdSet):
    "Stores the 'talk' command."
    key = "talkingcmdset"

    def at_cmdset_creation(self):
        "populates the cmdset"
        self.add(CmdTalk())


# ==============================================================
# ==
# == RealTalkingNPC - The standard object for NPCs that talk.
# ==
# ==============================================================

class RealTalkingNPC(RealObject):
    """
    This class inherits the RealObject typeclass and adds the talk 
    command and using the default conversation defined above.

    Note: This typeclass is not meant to be utilized directly 
    when creating NPC objects inside the game.

    In order to create NPCs based on this standard object with 
    their own unique dialog trees, each NPC that is added to the 
    game *must* have its own .py file that contains a class which 
    inherits from this one. That .py file will also contain the
    EvMenu functions which define the structure of the NPC's 
    dialogue tree. The tree *must* begin at a function named 
    'dialogue_start', but can otherwise be modified to do 
    anything within the limitiations of the EvMenu utility.
    """
    
    def at_object_creation(self):
        "This is called when object is first created."

        # Assign a default description
        self.db.desc = "This person has something to say."

        # Assign the commandset containing the talk command
        self.cmdset.add_default(TalkingCmdSet, permanent=True)

        # Only Builders and higher can '@get' an NPC by default
        self.locks.add('get: perm(Builders)')

