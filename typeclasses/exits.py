"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from evennia import DefaultExit

# Hashlib is used by AuthenticatedExit
import hashlib


class Exit(DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property. It also does work in the
    following methods:

     basetype_setup() - sets default exit locks (to change, use `at_object_creation` instead).
     at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and should
                              rebuild the Exit cmdset along with a command matching the name
                              of the Exit object. Conventionally, a kwarg `force_init`
                              should force a rebuild of the cmdset, this is triggered
                              by the `@alias` command when aliases are changed.
     at_failed_traverse() - gives a default error message ("You cannot
                            go there") if exit traversal fails and an
                            attribute `err_traverse` is not defined.

    Relevant hooks to overload (compared to other types of Objects):
        at_traverse(traveller, target_loc) - called to do the actual traversal and calling of the other hooks.
                                            If overloading this, consider using super() to use the default
                                            movement implementation (and hook-calling).
        at_after_traverse(traveller, source_loc) - called by at_traverse just after traversing.
        at_failed_traverse(traveller) - called by at_traverse if traversal failed for some reason. Will
                                        not be called if the attribute `err_traverse` is
                                        defined, in which case that will simply be echoed.
    """
    pass


class AuthenticatedExit(DefaultExit):
    """
    AuthenticatedExit
    =================
    
    A door that only allows characters with tokens that are granted access.
    """

    def at_object_creation(self):
        """
        Called when object is created and updated.
        """

        # Custom traverse error that instructs a player to try the 'use' command.
        self.db.err_traverse = "It's locked, but it looks like you can|r use|n the door|r with|n an|r identity token."

        # Builders and higher can traverse normally without authentication.
        # The default traverse string is configured as an object attribute
        # because it gets re-written after every traverse. This allows a builder
        # to change the default lockstring in a way that doesn't get re-written.
        self.db.default_traverse = "traverse:perm(Builders)"
        self.locks.add(self.db.default_traverse)

        # The exit's use_mode opitons are:
        #    * 'checking' -- Checks a secured list of keys (not viewable by builders)
        #    * 'granting' -- Allows all tokens, AND adds each to the granted keys list
        #    * 'allowing' -- Allows all tokens, but does not add them to the granted keys list
        #    * 'denying' -- Denies all tokens.
        self.db.use_mode = "checking"

        # Set sensitive attribute
        if self.db.granted_keys == None:
            self.db.granted_keys = []
        
        # Set lockstring for sensitive attribute
        attr_lockstring = "attrread:perm(Admins);attredit:perm(Admins)"

        # Apply lockstring for sensitive attribute
        self.attributes.get("granted_keys", return_obj=True).locks.add(attr_lockstring)


    def at_after_traverse(self, traversing_object, source_location, **kwargs):
        """
        Called just after an object successfully used this object to
        traverse to another object.
        """
        # Reset the traverse lock every time to avoid making a mess of the lockstrings.
        # This also forces players to '@use' the exit with their token every time, rather
        # than simply calling the object to traverse.
        self.locks.add(self.db.default_traverse)

        return


    def add_granted_key(self, token_key, **kwargs):
        # Hash the given key.
        token_hash = str(hashlib.sha3_256(token_key.encode('utf-8')).hexdigest())

        # Add the token hash to the locked-down granted_keys attribute.
        self.db.granted_keys.append(token_hash)
        return


    def add_token_to_lock(self, token_dbref, **kwargs):
        """
        Adds a specified token_dbref to this exit's 'traverse:'
        lock in a 'holds()' lock function
        """

        # Append a 'holds()' lock function with the specified token_dbref
        # to the existing 'traverse:' lockstring.
        for lock in self.locks.get().split(";"):
            if "traverse" in lock.lower().strip():
                lockstring = lock + " or holds(" + token_dbref + ")"

        # Assign the new lockstring, overwriting the old one.
        self.locks.add(lockstring)
        return
        

    def at_use(self, user, with_obj, **kwargs):
        """
        The at_use method allows characters to use other objects
        with this object via the '@use' command and specifying
        this object as a target.
        """
        # Nothing happens by default.
        message_string = "Nothing happens."

        # Get the current 'use_mode' attribute of the object.
        use_mode = self.db.use_mode

        # Only using with objects of the 'IdentityToken' typeclass will do anything.
        if (str(with_obj.typename) == "IdentityToken"):
            # Let user know they are using the correct type of object.
            user.msg("You place your token against the door.")

            # Hash the token ID. Salting of hashes is not implemented (yet?)
            token_hash = str(hashlib.sha3_256(with_obj.db.id_key.encode('utf-8')).hexdigest())

            # Perform actions based on the object's configurable "use_mode" attribute.
            if use_mode == "allowing":
                message_string = "Access Granted!"

            elif use_mode == "checking":
                if token_hash in self.db.granted_keys:
                    message_string = "Access Granted!"
                else:
                    message_string = "Access Denied!"

            elif use_mode == "granting":
                if token_hash in self.db.granted_keys:
                    # Don't add existing granted keys to the 'granted_keys' attribute.
                    message_string = "Access Granted!"

                else:
                    # Grant access.
                    message_string = "Access Granted!"

                    # Add the token's id to the granted_keys list.
                    self.add_granted_key(with_obj.db.id_key)
                    # Inform user their token was added to the list of granted keys.
                    user.msg("This token's key has been added to the list of granted keys.")
                    
            elif use_mode == "denying":
                # No tokens are allowed to traverse.
                message_string = "Access Denied!"
                
            else:
                # The exit is misconfigured.
                message_string = "The token reader realeases a puff of bluish-gray smoke."

        # Send the final message string to the user
        user.msg(message_string)

        # Perform a traverse if the message was 'Access Granted!'
        if message_string == 'Access Granted!':
            self.add_token_to_lock(with_obj.dbref)
            self.at_traverse(user, self.destination)
        return

    
