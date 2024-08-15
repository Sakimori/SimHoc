from player import Skater, Goalie, Player
from random import sample

class Team(object):
    """A team of either 6 or 10 skaters and 1-3 goalies."""
    roster:list[Player] = [] #ordered, first line then second line; (#, name)
    goalies:Player = [] # (#, name)
    name = None
    shortname = None

    def __init__(self, skaters, goalies, name:str, shortname:str):
        self.roster = skaters
        self.goalies = goalies
        self.name = name
        self.shortname = shortname

    def isPlayerOnTeam(self, player:Player):
        return player in self.roster or player in self.goalies


    def chooseGoalie(self):
        return sample(self.goalies,1)[0]