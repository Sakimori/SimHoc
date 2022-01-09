import attributes
from enum import Enum

class CreationError(Exception):
    pass

class Player(object):
    """A hockey player with attributes and various functions."""

    def __init__(self, name:str):
        if name is None:
            self.attributes = []
        elif len(name) > 30:
            raise CreationError("Player name too long.")
        else:
            self.name = name
            self.attributes = self.loadAttributes()

    def loadAttributes(self):
        """Generates attributes based on name, or loads from database if present."""
        rawAtrs = attributes.attributesFromName(self.name)
        self.attributesVersion = rawAtrs[0]
        return rawAtrs[1:]

    def twitterString(self): 
        """Generates a twitter-formatted string representing the player."""
        send = f"{self.name}:\n"
        for attr in self.attributes:
            if attr.name not in attributes.noPrint:
                send += attr.twitterFormat()
                send += "\n"
        return send

    def getAttribute(self, shortname:str):
        """Returns an Attribute object with given shortname."""
        for attr in self.attributes:
            if attr.name.lower().startswith(shortname.lower()):
                return attr
        return None

    def setAttribute(self, shortname:str, value:float):
        for attr in self.attributes:
            if attr.name.lower().startswith(shortname.lower()):
                attr.value = value
                return True
        self.attributes.append(attributes.Attribute(attributes.singleAttribute(shortname)[0],value))

    def __eq__(self, value):
        if isinstance(value, Player):
            return self.name == value.name
        elif isinstance(value, str):
            return self.name == value
        else:
            return False


class Skater(Player):
    """A hockey player that is not a goalie."""


class Goalie(Player):
    """A hockey player that *is* a goalie."""

class AtkAction(Enum):
    SkateB = 0
    SkateF = 1
    SkateT = 2
    SkateA = 3
    PassS = 4
    PassF = 5
    PassB = 6
    Dump = 7
    ShotS = 8
    ShotW = 9

class DefAction(Enum):
    Steal = 0
    Poke = 1
    BlockLn = 2
    Body = 3
    Force = 4
    Pin = 5
    BlockSlot = 6