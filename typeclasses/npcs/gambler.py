"""
gambler.py

Copyright 2020, Michael J. Freidel under the BSD 3-Clause License (See LICENSE file)

This is an NPC with a dialogue tree that initiates a gambling game.
"""


from typeclasses.npc import RealTalkingNPC


# ==============================================================
# ==
# == Gambler's dialogue tree - Win big. REAL big.
# ==
# ==============================================================

def dialogue_start(caller):
    text = "'Wanna play a game? You could win big. REAL big! Whadduya say, punk?'"

    options = (
        {"desc": "No thanks.", "goto": "END"}
    )

    return text, options

# This is obviously not complete yet...

def END(caller):
    text = "'Fine. How 'bout you just step back and let someone else take a chance, then?'"

    options = ()

    return text, options



# ==============================================================
# ==
# == RealGamblerNPC - Nothing special.
# ==
# ==============================================================

class RealGamblerNPC(RealTalkingNPC):
    """
    This simply inherits the standard RealTalkingNPC typeclass.
    """
    pass
