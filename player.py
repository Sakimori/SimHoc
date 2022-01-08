import attributes

class CreationError(Exception):
    pass

class Player(object):
    """A hockey player with attributes and various functions."""

    def __init__(self, name:str):
        if len(name) > 30:
            raise CreationError("Player name too long.")
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