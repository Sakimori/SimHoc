import attributes
from enum import Enum

class CreationError(Exception):
    pass

class Player(object):
    """A hockey player with attributes and various functions."""

    def __init__(self, name:str, number:int=0):
        if name is None:
            self.attributes = []
        elif len(name) > 30:
            raise CreationError("Player name too long.")
        elif number < 0 or number > 99:
            raise CreationError("Player number not valid.")
        else:
            self.name = name
            self.attributes = self.loadAttributes()
        self.number = number

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

    def __str__(self):
        return f"#{str(self.number)} {self.initials()}"

    def initials(self):
        names = self.name.split()
        outString = ""
        for name in names:
            outString += f"{name[0]}."
        return outString

class Skater(Player):
    """A hockey player that is not a goalie."""
    pass


class Goalie(Player):
    """A hockey player that *is* a goalie."""
    pass

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