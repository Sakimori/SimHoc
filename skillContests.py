from enum import Enum

class Situations(Enum):
    EvenStrength = 0
    PP1 = 1 #4v3, 5v4, or 6v5
    PP2 = 2 #5v3 or 6v4
    SH1 = -1 #3v4, 4v5, 5v6
    SH2 = -2 #3v5 or 4v6
    
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

class SkillContestParams(object):
    """Basic structure for contests of skill."""
    atkStats = []
    defStats = []
    override = None

    def __init__(self, atkStats:list=[], defStats:list=[]):
        self.atkStats = atkStats
        self.defStats = defStats

    def actionCheck(self, atkAction:AtkAction, defAction:DefAction, situation:Situations=Situations.EvenStrength):
        """Determines which skills to test, and how strongly. Returns itself."""
        if situation == Situations.EvenStrength:
            result = evenTable[atkAction.value][defAction.value]
            if isinstance(result, bool):
                self.override = result
                return self
            self.atkStats = result[0]
            self.defStats = result[1]          
        return self

#Bool overrides, or [List of (stat,weight) , List of (stat,weight)]
evenTable = [
    #Steal                                   #Poke                                     #block lane                             #Body check                      #Force off puck                         #Pin to wall                        #Body block
    [[[('Sti',100)],[('Sti',20)]],           [[('Dex',110),('Sti',35)],[('Sti',30)]], True,                                   [[('Agi',11)],[('Spe',8)]],   [[('Agi',20)],[('Str',8)]],             [[('Agi',20)],[('Str',10)]],            True],                                      #Skate back
    [[[('Sti',100)],[('Sti',40)]],           [[('Dex',70),('Sti',30)],[('Sti',100)]], True,                                   [[('Str',80)],[('Str',100)]], [[('Spe',60),('Str',40)],[('Str',80)]], [[('Spe',60),('Str',40)],[('Str',100)]],True],                                      #Skate forward
    [[[('Dex',75),('Sti',25)],[('Sti',50)]], [[('Dex',50),('Sti',30)],[('Sti',100)]], [[('Ref',20),('Sti',60)],[('Sti',100)]],[[('Dex',70)],[('Str',100)]], [[('Spe',60),('Str',40)],[('Str',120)]],True,                                   [[('Sti',1)],[('Ref',3)]]],                 #Skate through
    [[[('Sti',100)],[('Sti',40)]],           [[('Dex',70),('Sti',30)],[('Sti',100)]], True,                                   [[('Agi',100)],[('Str',100)]],[[('Sti',100)],[('Str',100)]],          [[('Sti',100)],[('Str',110)]],          True],                                      #Skate around
    [True,                                   [[('Pas',70)],[('Sti',30)]],             [[('Pas',80)],[('Ref',110)]],           True,                         [[('Pas',100)],[('Str',80)]],           [[('Pas',100)],[('Str',90)]],           True],                                      #Stretch pass
    [[[('Pas',100)],[('Ref',40),('Sti',30)]],[[('Pas',70)],[('Sti',30)]],             [[('Pas',80)],[('Ref',110)]],           True,                         [[('Pas',100)],[('Str',80)]],           [[('Pas',100)],[('Str',100)]],          [[('Pas',1)],[('Ref',3)]]],                 #Forward pass
    [[[('Pas',100)],[('Int',30)]],           True,                                    True,                                   True,                         True,                                   [[('Sti',100)],[('Str',100)]],          True],                                      #Backward pass
    [True,                                   True,                                    [[('Wis',100)],[('Ref',20)]],           True,                         True,                                   True,                                   True],                                      #Dump/ice
    [False,                                  False,                                   True,                                   False,                        True,                                   False,                                  [[('Sho',120)],[('Ref',70),('Int',30)]]],   #Slapshot
    [[[('Dex',120)],[('Sti',40)]],           [[('Dex',100)],[('Sti',40)]],            [[('Sho',50)],[('Ref',25)]],            [[('Dex',80)],[('Str',60)]],  [[('Dex',100)],[('Str',90)]],           [[('Dex',100)],[('Str',100)]],          [[('Sho',1)],[('Ref',2),('Int',1)]]]        #Wrist shot
]