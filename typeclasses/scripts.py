"""
Evennnia Details for Scripts
============================

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""

from evennia import DefaultScript
import random

# ==============================================================
# ==
# == Default Evennia Script
# ==
# ==============================================================


class Script(DefaultScript):
    """
    Evennnia Details
    ================
    A script type is customized by redefining some or all of its hook
    methods and variables.

    * available properties

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved
              to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     desc (string)      - optional description of script, shown in listings
     obj (Object)       - optional object that this script is connected to
                          and acts on (set automatically by obj.scripts.add())
     interval (int)     - how often script should run, in seconds. <0 turns
                          off ticker
     start_delay (bool) - if the script should start repeating right away or
                          wait self.interval seconds
     repeats (int)      - how many times the script should repeat before
                          stopping. 0 means infinite repeats
     persistent (bool)  - if script should survive a server shutdown or not
     is_active (bool)   - if script is currently running

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                        self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not
                        create a database entry when storing data

    * Helper methods

     start() - start script (this usually happens automatically at creation
               and obj.script.add() etc)
     stop()  - stop script, and delete it
     pause() - put the script on hold, until unpause() is called. If script
               is persistent, the pause state will survive a shutdown.
     unpause() - restart a previously paused script. The script will continue
                 from the paused timer (but at_start() will be called).
     time_until_next_repeat() - if a timed script (interval>0), returns time
                 until next tick

    * Hook methods (should also include self as the first argument):

     at_script_creation() - called only once, when an object of this
                            class is first created.
     is_valid() - is called to check if the script is valid to be running
                  at the current time. If is_valid() returns False, the running
                  script is stopped and removed from the game. You can use this
                  to check state changes (i.e. an script tracking some combat
                  stats at regular intervals is only valid to run while there is
                  actual combat going on).
      at_start() - Called every time the script is started, which for persistent
                  scripts is at least once every server start. Note that this is
                  unaffected by self.delay_start, which only delays the first
                  call to at_repeat().
      at_repeat() - Called every self.interval seconds. It will be called
                  immediately upon launch unless self.delay_start is True, which
                  will delay the first call of this method by self.interval
                  seconds. If self.interval==0, this method will never
                  be called.
      at_stop() - Called as the script object is stopped and is about to be
                  removed from the game, e.g. because is_valid() returned False.
      at_server_reload() - Called when server reloads. Can be used to
                  save temporary variables you want should survive a reload.
      at_server_shutdown() - called at a full server shutdown.

    """
    # This currently has no customized options for gridpunx
    pass


# ==============================================================
# ==
# == Real Room Scripts - Meant to be attached to rooms in the
# == pysical realm
# ==
# ==============================================================

class HarshClimate(Script): 
    """
    This script is based on the Weather script from Evennia's documentation 
    (/path/to/your/evennia/docs/source/Scripts.md) and modified to harm the 
    player at regular intervals. Meant to be attached to a RealOutside room to 
    establish a setting with a harmful climate. 
    """
    
    def at_script_creation(self):
        self.key = "harsh_climate"
        self.desc = "Harms an unprotected player at regular intervals."
        self.interval = 60 * 2  # every 2 minutes
        self.persistent = True  # will survive reload

    def at_repeat(self):
        "called every self.interval seconds."        
        rand = random.random()
        if rand < 0.5:
            climate_damage = 2
            climate_message = "Foul air of the concrete jungle lingers around you."
        elif rand < 0.8:
            climate_damage = 4
            climate_message = "The already dense smog thickens some more."
        else:
            climate_damage = 8
            climate_message = "A gentle breeze brings in some more toxic industrial fumes."

        # send the climate_message string to everyone inside the room
        self.obj.msg_contents(climate_message)

        # Damage all unprotected humans in the room:
        # Loop through all objects in room.  
        for list_item in self.obj.contents:
            if list_item.db.is_human == True:
                # Check if it's a human and if they have protection from climate damage
                if list_item.get_climate_protection() == True:
                    # Let protected humans know they avoided damage.
                    list_item.msg("Fortunately, you have climate protection and aren't harmed.")
                else:
                    # Hurt unprotected humans, and then let them know how much it hurts.
                    list_item.db.hitpoints -= climate_damage
                    list_item.msg("You take " + str(climate_damage) + " damage.")
                    
