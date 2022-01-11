import player
from random import sample

class Team(object):
    """A team of either 6 or 10 skaters and 1-3 goalies."""
    roster = [] #ordered, first line then second line; (#, name)
    goalies = [] # (#, name)
    name = None
    shortname = None

    def __init__(self, skaters, goalies, name:str, shortname:str):
        self.roster = skaters
        self.goalies = goalies
        self.name = name
        self.shortname = shortname

    def chooseGoalie(self):
        return sample(self.goalies,1)