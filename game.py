import random, team, player, os, math
from team import Team
from player import Player, AtkAction, DefAction, Skater, Goalie
from skillContests import SkillContestParams, Situations
from attributes import normalDis
from hocUtils import RinkGraph
from enum import Enum
import networkx as nx

RINKDIRPATH = os.path.join("Rinks","Graphs")
DEFAULTRINKFILENAME = "defaultedges.nx"

class Game(object):
    """A game of hockey!"""
    
    def __init__(self, awayTeam:Team, homeTeam:Team, threes:bool=False):
        if awayTeam is not None and homeTeam is not None:
            self.away = awayTeam
            self.home = homeTeam

            self.awayZones = RinkGraph(edgeFilename=DEFAULTRINKFILENAME)
            self.homeZones = RinkGraph(edgeFilename=DEFAULTRINKFILENAME)
            self.currentZone:int = None
            self.faceoffSpot = FaceoffDot.Center
            self.playStopped = True

            self.lineSize = 5 
            if len(awayTeam.roster) != 10 or len(homeTeam.roster) != 10 or threes:
                self.lineSize = 3 

            self.goalieHome = self.home.chooseGoalie()
            self.goalieAway = self.away.chooseGoalie()

            self.positionInPossession = None #use SkaterPosition enum
            self.teamInPossession = None
            self.loosePuck = False

            self.skatersHome = self.home.roster[:5] #LW LD C RD RW, EA; use the SkaterPosition enum for indexing. Threes uses left winger, left defenseman, center.
            self.skatersAway = self.away.roster[:5]

            self.penaltyBoxAway = []
            self.penaltyBoxHome = []
            self.pulledGoalieAway = False
            self.pulledGoalieHome = False

            self.period = 1
            self.clock = 60*20 #Time remaining in period, given in seconds

            self.eventLog = []
            self.eventLogVerbose = []

    def defendingTeam(self):
        if self.teamInPossession == self.home:
            return self.away
        else:
            return self.home

    def attackingTeam(self):
        """Alias for teamInPossession, to match defendingTeam()"""
        return self.teamInPossession

    def homeAttacking(self):
        return self.teamInPossession == self.home

    def skatersInPossession(self):
        return self.skatersHome if self.homeAttacking() else self.skatersAway

    def clockToMinutesSeconds(self):
        """Returns a string MM:SS elapsed in period."""
        elapsedSeconds = 60*20 - self.clock if self.clock >= 0 else 60*20
        minutes = str(int(math.modf(elapsedSeconds/60)[1]))
        seconds = str(elapsedSeconds % 60)
        if len(seconds) == 1:
           seconds = f"0{seconds}"
        return f"{minutes}:{seconds}"


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

    def faceoffContest(self, awayPlayer:Skater, homePlayer:Skater):
        """Hold a faceoff! True indicates home win, False is away win."""
        faceoffSkills = [('Dex',50),('Sti',50),('Pas', 10)]
        params = SkillContestParams(faceoffSkills, faceoffSkills)
        return self.skillContest(homePlayer, awayPlayer, params) if random.random() > 0.4 else random.sample([True, False], 1)[0]

    def zoneAfterFaceoff(self):
        if self.homeAttacking():
            lookupList = [35, 15, 34, 14, 23, 32, 12, 31, 11]
        else:
            lookupList = [11, 31, 12, 32, 23, 14, 34, 15, 35]
        return lookupList[self.faceoffSpot.value]

    def event(self):
        """Meat and potatoes. Everything that happens is a direct result of this being called."""
        if self.playStopped: #need a faceoff
            self.teamInPossession = self.home if self.faceoffContest(self.skatersAway[SkaterPosition.C.value], self.skatersHome[SkaterPosition.C.value]) else self.away
            self.positionInPossession = SkaterPosition(random.sample([0, 1, 1, 3, 3, 4],1)[0]) #wingers are less likely to recieve the faceoff than defensemen
            self.playStopped = False
            winningPlayer = self.skatersInPossession()[SkaterPosition.C.value]
            eventString = f"{self.clockToMinutesSeconds()} - {self.teamInPossession.shortname} {str(winningPlayer)} wins faceoff."
            self.eventLog.append(eventString)
            self.eventLogVerbose.append(eventString)
            self.clock -= random.randint(2,5)
            self.currentZone = self.zoneAfterFaceoff()

    def eventLogOut(self):
        outList = []
        while len(self.eventLog) > 0:
            outList.append(self.eventLog.pop(0))
        return outList

class FaceoffDot(Enum):
    """All orientations are given from the perspective of the defending team."""
    AwayZoneLeft = 0
    AwayZoneRight = 1
    AwayNeutralLeft = 2
    AwayNeutralRight = 3
    Center = 4
    HomeNeutralRight = 5
    HomeNeutralLeft = 6
    HomeZoneRight = 7
    HomeZoneLeft = 8

class SkaterPosition(Enum):
    """Allows easy indexing to the active skaters lists for each team."""
    LW = 0
    LD = 1
    C = 2
    RD = 3
    RW = 4
    EA = 5