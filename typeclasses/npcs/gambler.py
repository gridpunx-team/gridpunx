"""
gambler.py

Copyright 2020, Michael J. Freidel under the BSD 3-Clause License (See LICENSE file)

This is an NPC with a dialogue tree that initiates a gambling game.
"""


from typeclasses.npc import RealTalkingNPC
from random import randint


# ==============================================================
# ==
# == Gambler's dialogue tree - Win big. REAL big.
# ==
# ==============================================================

def _player_has_money(caller, raw_string, **kwargs):
    if (caller.db.gridbits == 0 or caller.db.gridbits == None):
        caller.msg("|rYou have no money.")
        return "no_money"
    else:
        return "gamble_init"


def dialogue_start(caller, raw_string, **kwargs):
    text = "'Wanna bet on a game? You could win big. REAL big! Whadduya say, punk?'"

    options = (
        {"desc": "Sure.", "goto": _player_has_money},
        {"desc": "No thanks.", "goto": "END"}
    )

    return text, options


def no_money(caller, raw_string, **kwargs):
    text = "'How you gonna gamble if ya aint got no money? Get outta my face, ya moron.'"

    options = ()

    return text, options


def gamble_init(caller, raw_string, **kwargs):
    text = "'The game is duodo.'"

    options = (
        {"desc": "What's duodo?", "goto": "duodo_rules"},
        {"desc": "Alright, let's play.", "goto": "duodo_set_bet"}
    )

    return text, options

def duodo_rules(caller, raw_string, **kwargs):
    text = \
    """
    Ok, so the rules go like this...

    I have a set of two dice with twelve side on 'em. I'll roll them 
    together in 'rounds.' A round is over once either the total of the 
    dice is 13 or when your bet pays out.

    Each round has these steps:

    1. You bet on a set of doubles. Either a particular set of doubles (pays
       4x your wager), or any doubles (pays 2x your wager). You can only 
       place one bet per round.
    2. I shoot the dice until they total 13.
    3. If I shoot something that you betted on before that, then your bet
       pays out and the round is over.
    """

    options = (
        {"desc": "Alright, let's play.", "goto": "duodo_set_bet"},
        {"desc": "Sounds like a scam.", "goto": "END"}
    )

    return text, options


def _duodo_check_bet(caller, raw_string, **kwargs):
    valid_bet = False
    caller.ndb._menutree.player_bet = {}
    if raw_string.strip().lower() == 'any':
        valid_bet = True
        caller.ndb._menutree.player_bet['doubles'] = 'any'
        caller.ndb._menutree.player_bet['payout'] = 2
    elif raw_string == '':
        caller.msg("|rYou must specify a wager.")
    else:
        try:
            bet = int(raw_string)
        except ValueError:
            caller.msg("|rYou can only bet on 'any' or a specific number.")
            return None
        if bet in list(range(1,12)):
            valid_bet = True
            caller.ndb._menutree.player_bet['doubles'] = int(raw_string)
            caller.ndb._menutree.player_bet['payout'] = 4
        else:
            caller.msg("|rYou can only choose 1-12.")

    if not valid_bet:
        caller.msg("|rTry again.")
        return None
    else:
        return "duodo_set_wager"


def duodo_set_bet(caller, raw_string, **kwargs):
    text = \
        """
        Which set of doubles do you want to bet on?

        Type 'any' for any doubles (Pays out 2x your wager), or type a
        number from '1' to '12' to indicate a specific set of doubles (pays 
        4x your wager).
        """

    options = (
        {"key": "_default", "goto": _duodo_check_bet}
    )

    return text, options


def _duodo_check_wager(caller, raw_string, **kwargs):
    valid_wager = False
    try:
        wager = int(raw_string)
    except ValueError:
        caller.msg("|rYour wager needs to be a number. Try again.")
        return None
    
    if 0 < wager <= caller.db.gridbits:
        valid_wager = True
        caller.ndb._menutree.player_bet['wager'] = wager
    elif wager == 0:
        caller.msg("|rYou must specify a wager.")
    elif wager < 0:
        caller.msg("|rYou can only bet positive numbers.")
    else:
        caller.msg("|rYou can't bet more than you have.")

    if not valid_wager:
        caller.msg("|rTry again.")
        return None
    else:
        return "duodo_confirm_bet"


def duodo_set_wager(caller, raw_string, **kwargs):
    text = "'What's your wager?' (You have " + str(caller.db.gridbits) + " gridbits)"

    options = (
        {'key': '_default', 'goto': _duodo_check_wager}
    )

    return text, options


def _duodo_shoot(caller, raw_string, **kwargs):
    caller.db.gridbits -= caller.ndb._menutree.player_bet['wager']
    player_bet = caller.ndb._menutree.player_bet['doubles']
    while True:
        # Get outcomes
        die_1 = randint(1,12)
        die_2 = randint(1,12)
        dice_sum = die_1 + die_2

        # Display outcomes.
        caller.location.msg_contents("|rDuodo Shoot: |y(" + str(die_1) + " & " + str(die_2) + ")")

        # Check for lose condition
        if dice_sum == 13:
            caller.location.msg_contents("The gambler says 'That's 13! Round over.'")
            return "duodo_lose"
        
        # Check for win conditions
        if die_1 == die_2:
            if (player_bet == 'any') or (player_bet == die_1):
                caller.location.msg_contents("The gambler says 'We have a winner!'")
                return "duodo_win"


def duodo_confirm_bet(caller, raw_string, **kwargs):
    wager = str(caller.ndb._menutree.player_bet['wager'])
    doubles = str(caller.ndb._menutree.player_bet['doubles'])
    
    text = "So, you wanna bet " + wager + " on doubles of '" + doubles + "'?"

    options = (
        {"desc": "Yeah, shoot the dice!", "goto": _duodo_shoot},
        {"desc": "No, I want to change my bet.", "goto": "duodo_set_bet"}
    )

    return text, options


def duodo_lose(caller, raw_string, **kwargs):
    text = "'Looks like you loose. Wanna try again?'"

    options = (
        {"desc": "Yeah, sure.", "goto": "gamble_init"},
        {"desc": "No thanks.", "goto": "END"}
    )

    return text, options


def duodo_win(caller, raw_string, **kwargs):
    wager = caller.ndb._menutree.player_bet['wager']
    payout = wager * caller.ndb._menutree.player_bet['payout']
    caller.db.gridbits += payout
    
    text = "'You win. Here's your " + str(payout) + " gridbits. How about another round, punk?'"

    options = (
        {"desc": "Yeah, sure.", "goto": "gamble_init"},
        {"desc": "No thanks.", "goto": "END"}
    )

    return text, options


def END(caller, raw_string, **kwargs):
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
