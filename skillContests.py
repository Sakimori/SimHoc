from player import AtkAction, DefAction
from enum import Enum

class Situations(Enum):
    EvenStrength = 0
    PP1 = 1 #4v3, 5v4, or 6v5
    PP2 = 2 #5v3 or 6v4
    SH1 = -1 #3v4, 4v5, 5v6
    SH2 = -2 #3v5 or 4v6

class SkillContestParams(object):
    """Basic structure for contests of skill."""
    atkStats = []
    defStats = []
    override = None

    def __init__(self, atkAction:AtkAction, defAction:DefAction, situation:Situations):
        """Determines which skills to test, and how strongly."""
        if situation == Situations.EvenStrength:
            result = evenTable[atkAction.value][defAction.value]
            if isinstance(result, bool):
                self.override = result
                return
            self.atkStats = result[0]
            self.defStats = result[1]




#Bool overrides, or [List of (stat,weight) , List of (stat,weight)]
evenTable = [
    #Steal                                   #Poke                                     #block lane                             #Body check                      #Force off puck                         #Pin to wall                        #Body block
    [[[('Sti',100)],[('Sti',20)]],           [[('Dex',75),('Sti',35)],[('Sti',40)]], True,                                   [[('Agi',110)],[('Spe',100)]],[[('Agi',110)],[('Str',100)]],          [[('Agi',110)],[('Str',100)]],          True],                                      #Skate back
    [[[('Sti',100)],[('Sti',40)]],           [[('Dex',50),('Sti',30)],[('Sti',100)]], True,                                   [[('Str',100)],[('Str',100)]],[[('Spe',60),('Str',40)],[('Str',100)]],[[('Spe',60),('Str',40)],[('Str',100)]],True],                                      #Skate forward
    [[[('Dex',75),('Sti',25)],[('Sti',50)]], [[('Dex',70),('Sti',30)],[('Sti',100)]], [[('Ref',50),('Sti',50)],[('Sti',100)]],[[('Dex',100)],[('Str',100)]],True,                                   True,                                   [[('Sti',100)],[('Ref',100)]]],             #Skate through
    [[[('Sti',100)],[('Sti',30)]],           [[('Dex',70),('Sti',30)],[('Sti',100)]], True,                                   [[('Agi',100)],[('Str',100)]],[[('Sti',100)],[('Str',100)]],          [[('Sti',100)],[('Str',100)]],          True],                                      #Skate around
    [True,                                   [[('Pas',100)],[('Sti',100)]],           [[('Pas',100)],[('Ref',100)]],          True,                         [[('Str',80),('Pas',20)],[('Str',100)]],[[('Str',80),('Pas',20)],[('Str',100)]],True],                                      #Stretch pass
    [[[('Pas',100)],[('Ref',20),('Sti',40)]],[[('Pas',100)],[('Sti',100)]],           [[('Pas',100)],[('Ref',100)]],          True,                         [[('Str',100)],[('Str',100)]],          [[('Str',100)],[('Str',100)]],          [[('Pas',100)],[('Ref',100)]]],             #Forward pass
    [[[('Pas',100)],[('Int',20)]],          True,                                    True,                                   True,                         True,                                   [[('Sti',100)],[('Str',100)]],          True],                                      #Backward pass
    [True,                                   True,                                    [[('Wis',100)],[('Ref',100)]],          True,                         True,                                   True,                                   True],                                      #Dump/ice
    [False,                                  False,                                   True,                                   False,                        True,                                   False,                                  [[('Sho',100)],[('Ref',70),('Int',30)]]],   #Slapshot
    [[[('Dex',100)],[('Sti',40)]],          [[('Dex',100)],[('Sti',100)]],           [[('Sho',100)],[('Ref',100)]],          [[('Dex',100)],[('Str',100)]],[[('Dex',100)],[('Str',100)]],          [[('Dex',100)],[('Str',100)]],          True]                                       #Wrist shot
]