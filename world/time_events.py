"""
time_events.py

This file contains various time-based events that happen in
the gridpunx world. These will need to be manually enabled
on new servers as global scripts.

The best way to do this is by logging into the game with
Developer or superuser privileges and running the following
command:

@py from world import time_events; time_events.start_[event-name]

"""

from evennia.utils import gametime 
from typeclasses.rooms import RealOutside

def at_sunrise():
    """When the sun rises, display a message in every RealOutside room."""
    # Browse all outside rooms
    for room in RealOutside.objects.all():
        room.msg_contents("The sun is rising.")

def start_sunrise_event():
    """Schedule an sunrise event to happen every day at 6:30 AM."""
    script = gametime.schedule(at_sunrise, repeat=True, hour=6, min=30, sec=0)
    script.key = "sunrise"

def at_sunset():
    """When the sun rises, display a message in every RealOutside room."""
    # Browse all outside rooms
    for room in RealOutside.objects.all():
        room.msg_contents("The sun is setting.")

def start_sunset_event():
    """Schedule an sunrise event to happen every day at 7:30 PM."""
    script = gametime.schedule(at_sunrise, repeat=True, hour=19, min=30, sec=0)
    script.key = "sunset"
