import attributes
from enum import Enum
from random import sample
from skillContests import AtkAction, DefAction, SkillContestParams

class CreationError(Exception):
    pass

class Player(object):
    """A hockey player with attributes and various functions."""

    def __init__(self, name:str, number:int=0):
        if name is None:
            self.attributes = []
        elif len(name) > 20:
            raise CreationError("Player name too long.")
        elif number < 0 or number > 99:
            raise CreationError("Player number not valid.")
        else:
            self.name = name
            self.attributes = self.loadAttributes()
        self.number = number
        scoutLevel = 0 #how well scouted opposing team is; not changing
        confidenceStage = 0 #how well the player can judge enemy skill; builds over game

    def loadAttributes(self):
        """Generates attributes based on name, or loads from database if present."""
        rawAtrs = attributes.attributesFromName(self.name)
        self.attributesVersion = rawAtrs[0]
        return rawAtrs[1:]

    def statsString(self): 
        """Generates a formatted string representing the player's stats."""
        send = ""
        for attr in self.attributes:
            if attr.name not in attributes.noPrint:
                send += attr.twitterFormat()
                send += "\n"
        return send

    def idString(self):
        """Generates a formatted string of player name and number."""
        if self.number < 10:
            return f"#0{self.number}: {self.name}"
        else:
            return f"#{self.number}: {self.name}"

    def getAttribute(self, shortname:str):
        """Returns an Attribute object with given shortname."""
        for attr in self.attributes:
            if attr.name.lower().startswith(shortname.lower()):
                return attr
        return None
    
    def getAttributes(self):
        """Returns a list of all Attributes."""
        return self.attributes

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
        if len(names) >= 2:
            for name in names:
                outString += f"{name[0]}."
        else:
            outString = f"{self.name[:3]}."
        return outString

    def predictOpposingAction(self, opposingSkater, graph, currentNode):
        oppAttributes = opposingSkater.getAttributes()
        #TODO: Fuzzy opponent attributes based on wisdom
        return self.chooseDefAction(statsOverride=oppAttributes)
        raise NotImplementedError()

    def chooseAtkAction(self, actionDic, currentNode, graph, opposingSkater):
        """TODO: Make actual AI. Picks an action/target node combo."""
        predAction = self.predictOpposingAction(opposingSkater, graph, currentNode)
        targetNode = sample(actionDic.keys(),1)[0] #random target node
        action = AtkAction[sample(actionDic[targetNode],1)[0]]
        ovr = SkillContestParams().actionCheck(action,predAction).override
        while ovr is not None and ovr is False: #don't pick an autofail
            targetNode = sample(actionDic.keys(),1)[0] #random target node
            action = sample(actionDic[targetNode],1)[0]
            ovr = SkillContestParams().actionCheck(action,predAction).override
        return (action, targetNode)

    def chooseDefAction(self, currentNode, graph, statsOverride = None):
        """TODO: Make actual AI. Returns random possible defensive action."""
        attrs = self.attributes if statsOverride is None else statsOverride
        possibleActions = graph.getPossibleDefensiveActions(currentNode)
        return sample(possibleActions,1)[0]

class Skater(Player):
    """A hockey player that is not a goalie."""
    pass


class Goalie(Player):
    """A hockey player that *is* a goalie."""
    pass