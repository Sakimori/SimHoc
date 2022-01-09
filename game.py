import random, team, player
from team import Team
from player import Player, AtkAction, DefAction
from skillContests import SkillContestParams, Situations
from attributes import normalDis

class Game(object):
    """A game of hockey!"""
    
    def __init__(self, awayTeam:Team, homeTeam:Team, threes:bool=False):
        if awayTeam is not None and homeTeam is not None:
            self.away = awayTeam
            self.home = homeTeam

            self.lineSize = 5 
            if len(awayTeam.roster) != 10 or len(homeTeam.roster) != 10 or threes:
                self.lineSize = 3 

            self.goalieHome = self.home.chooseGoalie()
            self.goalieAway = self.away.chooseGoalie()

            self.playerInPossession = None
            self.teamInPossession = None

            self.skatersHome = [] #LW LD C RD RW
            self.skatersAway = []

            self.penaltyBoxAway = []
            self.penaltyBoxHome = []
            self.pulledGoalieAway = False
            self.pulledGoalieHome = False

            self.period = 1
            self.clock = 60*20 #clock will be given in seconds

            self.eventLog = []

    def defendingTeam(self):
        if teamInPossession == self.home:
            return self.away
        else:
            return self.home

    def homeAttacking(self):
        return teamInPossession == self.home

    def currentSituation(self):
        skatersH = self.lineSize + self.pulledGoalieHome - len(self.penaltyBoxHome)
        skatersA = self.lineSize + self.pulledGoalieAway - len(self.penaltyBoxAway)
        if self.teamInPossession == self.home:
            return Situations(skatersH - skatersA)
        else:
            return Situations(skatersA - skatersH)

    def skillContest(self, atkPlayer:Player, defPlayer:Player, params:SkillContestParams):
        """Contests the two players with the given stats and stat weights. Returns True on offensive success."""
        if params.override is not None:
            return params.override
        else:
            atkValue = 0
            defValue = 0
            for attr, weight in params.atkStats:
                atkValue += atkPlayer.getAttribute(attr).value * weight/100
            for attr, weight in params.defStats:
                defValue += defPlayer.getAttribute(attr).value * weight/100

            atkRoll = normalDis(atkValue, atkValue/2, 0)
            defRoll = normalDis(defValue, defValue/2, 0)
            return atkRoll-defRoll > 0