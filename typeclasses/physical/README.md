# typeclasses/physical/

The gridpunx game separates Evennia's generic object into
several new types, and many features will require some further
customizations to those generic typeclasses for specific objects.
This directory holds the modules for those customized typeclasses
which are meant to be used in the game's physical realm. Each
module here will be named according to one of the more generic
typeclasses from typeclasses/objects.py. All classes in a module
here should be based on the typeclass which it is named after.
