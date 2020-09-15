"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom

# ==============================================================
# ==
# == Default Evennia Room
# ==
# ==============================================================

class Room(DefaultRoom):
    """
    Evennia details
    ===============
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.

    gridpunx details
    ================
    The Room class will be used for any game mechanics which will 
    be shared between realms. Currently, this has nothing defined.
    """
    pass


# ==============================================================
# ==
# == Real Rooms
# ==
# ==============================================================

class RealRoom(Room):
    """
    This is the basic room type for the physical realm. It is 
    currently just used as a means of establishing a hierarchy of 
    classes to separate the physical and digital realms.
    """
    pass



class RealInside(RealRoom):
    """
    Rooms that are "inside" a structure in the physical realm. These
    could also have varying levels of safety from the harsh conditions 
    of RealOutside rooms and would have special properties, like 
    access control or a connection to The Global Grid.
    """
    pass



class RealOutside(RealRoom):
    """
    Rooms that are "outside" of structures in the physical realm 
    will have harsh conditions which harm the player -- accomplished 
    via a Script object (based on the Weather script from Evennia's
    documentation (/path/to/your/evennia/docs/source/Scripts.md).
    """
    def at_object_creation(self):
        # Add the HarshClimate script these rooms
        self.scripts.add('scripts.HarshClimate')

        
