import player
from random import sample

class Team(object):
    """A team of either 6 or 10 skaters and 1-3 goalies."""
    roster = [] #ordered, first line then second line; (#, name)
    goalies = [] # (#, name)

    def chooseGoalie(self):
        return sample(goalies,1)