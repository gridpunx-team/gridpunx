"""
Physical Things
===============

This file contains typeclasses for customized objects in the
game's physical realm that use the 'RealThing' object typeclass.
"""

# All classes here should inherit the 'RealThing' class
from typeclasses.objects import RealThing

# urandom and hashlib are used by 'IdentityToken' class for authentication components
from os import urandom
import hashlib


class IdentityToken(RealThing):
    """
    The IdentityToken typeclass is meant to be used as a general
    purpose key to access various things in the game.
    """
    def at_object_creation(self):
        """
        Runs when object is created and updated.
        """

        # Avoid changing the id_key value at object updates
        if self.db.id_key == None:
            self.set_id_key()
        
        # Values used by the get_condition() function
        self.db.hitpoints = 64
        self.db.damage = 0
        
        
    def at_use(self, user, with_obj, **kwargs):
        """
        The at_use method allows characters to use other objects
        with this object via the '@use' command and specifying
        this object as a target.
        """

        # Default message is: 'Nothing happens.'
        message_string = "Nothing happens."
        
        if (with_obj == None) or (with_obj == self):
            # Use token by itself.

            # Change message to show the user's identity.
            message_string = "Your name is %s" % str(user)

        # Display message to user
        user.msg(message_string)


    def set_id_key(self):
        """
        Sets the id_key persistent attribute. This is only meant
        to be called the first time it is created.
        """
        id_key_hash = hashlib.sha3_256(urandom(16))
        self.db.id_key = str(id_key_hash.hexdigest())
