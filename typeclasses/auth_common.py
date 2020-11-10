"""
auth_common.py

This module contains functions that are designed to be used by
objects which require players to authenticate with an Identity 
Token.
"""

import hashlib

def add_granted_key(used_obj, token_obj):
    # Hash the given key.
    token_hash = str(hashlib.sha3_256(token_obj.db.id_key.encode('utf-8')).hexdigest())

    # Add the token hash to the locked-down granted_keys attribute.
    used_obj.db.granted_keys.append(token_hash)


def add_holds_token_to_lock(used_obj, token_obj, access_type):
    """
    Adds a specified token_dbref to a used object's 'access_type'
    lock in a 'holds()' lock function. 

    NOTE: This is meant to be reset after every time an object is
    used. Resetting the lock every time allows for a given token
    object's credentials to be copied to another object. This is
    essentially an intended security flaw 
    """

    # Initialize lockstring as None
    lockstring = None

    # Append a 'holds()' lock function with the specified token_dbref
    # to the existing 'traverse:' lockstring.
    for lock in used_obj.locks.get().split(";"):
        if access_type in lock.lower().strip():
            lockstring = lock + " or holds(" + token_obj.dbref + ")"

    # If the specified access type wasn't already defined on the object,
    # then create it with only the 
    if lockstring == None:
        lockstring = access_type + ": holds(" + token_dbref + ")"

    # Assign the new lockstring, overwriting the old one.
    used_obj.locks.add(lockstring)


def use_with_token(used_obj, token_obj, auth_mode):
    # Hash the token ID. Salting of hashes is not implemented (yet?)
    token_hash = str(hashlib.sha3_256(token_obj.db.id_key.encode('utf-8')).hexdigest())

    # Perform actions based on "auth_mode"
    if auth_mode == "allowing":
        return True

    elif auth_mode == "checking":
        if token_hash in used_obj.db.granted_keys:
            return True
        else:
            return False

    elif auth_mode == "granting":
        # Check if token was already added
        if token_hash in used_obj.db.granted_keys:
            # Allow access, but don't add pre-existing granted keys.
            return True
        else:
            # Add the token's id to the granted_keys list.
            add_granted_key(used_obj, token_obj)

            # Allow access.
            return True
                
    else:
        # Bad auth_mode
        return None
