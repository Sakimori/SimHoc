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
            #initial setup
            self.away = awayTeam
            self.home = homeTeam
            
            self.awayScore = 0
            self.homeScore = 0

            self.awayZones = RinkGraph(edgeFilename=DEFAULTRINKFILENAME)
            self.homeZones = RinkGraph(edgeFilename=DEFAULTRINKFILENAME)
            self.currentZone = 23 #home defensive center
            self.faceoffSpot = FaceoffDot.Center
            self.playStopped = True
            self.gameOver = False

            #determine skater/goalie linups
            self.lineSize = 5 
            if len(awayTeam.roster) != 10 or len(homeTeam.roster) != 10 or threes:
                self.lineSize = 3 

            self.goalieHome = self.home.chooseGoalie()
            self.goalieAway = self.away.chooseGoalie()
            self.skatersHome = self.home.roster[:5] #LW LD C RD RW, EA; use the SkaterPosition enum for indexing. Threes uses left winger, left defenseman, center.
            self.skatersAway = self.away.roster[:5]

            self.positionInPossession = SkaterPosition.C #use SkaterPosition enum
            self.teamInPossession = self.home
            self.loosePuck = True

            self.penaltyBoxAway = []
            self.penaltyBoxHome = []
            self.pulledGoalieAway = False
            self.pulledGoalieHome = False

            self.period = 1
            self.startClock = 60*20 #Set clock to zhis value after each period
            self.clock = self.startClock*1 #Time remaining in period, given in seconds
            self.powerPlayEndTimes = []

            self.eventLog = []
            self.eventLogVerbose = []
            
            #event affecting next event tracking
            self.noDefender = False #breakaways
            self.ineligibleDefenders = [] #prevent defender continuing to cause issues after being neutralized
            self.space = False #give space-making passes and skates an advantage
            self.loosePuckDefAdv = False #if attacker gets removed from play, defending team more likely to retrieve loose puck
                  
    def attackingSkater(self):
        return self.skatersInPossession()[self.positionInPossession.value]
    
    def defendingSkater(self):
        """Randomly selects a defensive skater to act as defender based on node"""
        left = self.currentZone >= 30 #defensive LW or LD
        if self.positionInPossession not in [SkaterPosition.LD, SkaterPosition.RD]:
            #FW in possession
            if left:
                counts = [2,5,3,4,1]
            else:
                counts = [1,4,3,5,2]
        else:
            #D in possession
            if left:
                counts = [5,3,4,1,2]
            else:
                counts = [2,1,4,3,5]       
        return self.skatersDefending()[random.sample(self.allPositions(), 1, counts=counts)[0].value]

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
    
    def skatersDefending(self):
        return self.skatersHome if not self.homeAttacking() else self.skatersAway 

    def defendingGoalie(self):
        return self.goalieAway if self.homeAttacking() else self.goalieHome
    
    def activeGraph(self):
        return self.homeZones if self.homeAttacking() else self.awayZones

    def clockToMinutesSeconds(self):
        """Returns a string MM:SS elapsed in period."""
        elapsedSeconds = 60*20 - self.clock if self.clock >= 0 else 60*20
        minutes = str(int(math.modf(elapsedSeconds/60)[1]))
        seconds = str(elapsedSeconds % 60)
        if len(seconds) == 1:
           seconds = f"0{seconds}"
        return f"{minutes}:{seconds}"
    
    def allPositions(self):
        """Get a list of all SkaterPosition enums."""
        return [
                SkaterPosition.LW, SkaterPosition.LD, SkaterPosition.C, SkaterPosition.RD, SkaterPosition.RW
            ]


    def currentSituation(self):
        """Returns a Situations enum based on current skater counts."""
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
        return str(lookupList[self.faceoffSpot.value])

    def event(self):
        """Meat and potatoes. Everything that happens is a direct result of this being called."""
        if self.clock < 0: #period/game over
            if self.period >= 3 and self.homeScore != self.awayScore: #game over
                self.gameOver = True
                self.addEventLog(f"Final score: {self.away.shortname} {self.awayScore} - {self.homeScore} {self.home.shortname}")
            else: #increment period, reset values
                self.period += 1
                self.clock = self.startClock*1
                self.playStopped = True
                self.faceoffSpot = FaceoffDot.Center
                self.addEventLog(f"Period {self.period} begins!")              
                
        elif self.playStopped: #need a faceoff
            self.teamInPossession = self.home if self.faceoffContest(self.skatersAway[SkaterPosition.C.value], self.skatersHome[SkaterPosition.C.value]) else self.away
            self.positionInPossession = SkaterPosition(random.sample([0, 1, 1, 3, 3, 4],1)[0]) #wingers are less likely to recieve the faceoff than defensemen
            self.playStopped = False
            winningPlayer = self.skatersInPossession()[SkaterPosition.C.value]
            receivingPlayer = self.skatersInPossession()[self.positionInPossession.value]
            eventString = f"{self.clockToMinutesSeconds()} - {self.teamInPossession.shortname} {str(winningPlayer)} wins faceoff to {str(receivingPlayer)}"
            self.addEventLog(eventString)
            self.clock -= random.randint(2,5)
            self.currentZone = self.zoneAfterFaceoff()
            
        elif self.loosePuck: #who gets it
            #first pick skaters chasing puck
            defenders = self.currentZone % 10 <= 3
            if defenders: #offensive team needs defensemen
                validPosO = [SkaterPosition.LD, SkaterPosition.RD]
                validPosD = [SkaterPosition.RW, SkaterPosition.LW]
            else:
                validPosO = [SkaterPosition.RW, SkaterPosition.LW]
                validPosD = [SkaterPosition.LD, SkaterPosition.RD]                   
            validPosO.append(SkaterPosition.C)
            validPosD.append(SkaterPosition.C) #center can always chase :>
            atkPos = random.sample(validPosO,1)[0]
            defPos = random.sample(validPosD,1)[0]
            atkChaser = self.skatersInPossession()[atkPos.value]
            defChaser = self.skatersDefending()[defPos.value]
            puckChaseSkills = [('Spe',50), ('Int',25), ('Agi',25)]
            params = SkillContestParams(puckChaseSkills, puckChaseSkills)
            result = self.skillContest(atkChaser, defChaser, params)
            if result: #offensive skater gets it
                self.positionInPossession = atkPos
            else:
                self.positionInPossession = defPos
                self.changePossession()
            self.addEventLog(f"{self.clockToMinutesSeconds()} - {self.attackingSkater()} chases za puck down for {self.attackingTeam().shortname}")
            self.clock -= random.randint(3,8)
            
        else: #run za state machine
            validActions = self.activeGraph().getAllReachableFrom(self.currentZone)
            attacker = self.attackingSkater()
            defender = self.defendingSkater()
            while defender in self.ineligibleDefenders:
                defender = self.defendingSkater() #reroll until eligible defender found
            self.ineligibleDefenders = [] #clear ineligible defs
                
            atkAction, nodeTarget = attacker.chooseAtkAction(validActions, defender) 
            defAction = defender.chooseDefAction()
            
            scParams = SkillContestParams().actionCheck(atkAction, defAction, self.currentSituation())
            result = self.skillContest(attacker, defender, scParams)
            if result: #attacker succeeded               
                if atkAction in [AtkAction.ShotS, AtkAction.ShotW]: #shot
                    self.addEventLog(f"{attacker.name} takes a shot!")
                    self.goalieCheck(atkAction, attacker) #shot goes zhrough                 
                else:
                    self.currentZone = int(nodeTarget)
                    if atkAction in [AtkAction.PassB, AtkAction.PassF, AtkAction.PassS]: #pass
                        self.space = atkAction == AtkAction.PassB #backpasses create space for next action                          
                        #successful pass, determine new possession
                        allPos = self.allPositions()
                        allPos.remove(self.positionInPossession) #cant pass to yourself
                        if nodeTarget % 10 >= 6: #D wouldnt be behind net, ever
                            allPos.remove(SkaterPosition.RD)
                            allPos.remove(SkaterPosition.LD)
                        #emphasize pass side attacker
                        if nodeTarget < 30: #attacking left
                            if self.positionInPossession != SkaterPosition.LW:
                                allPos.append(SkaterPosition.LW)
                            else:
                                allPos.append(SkaterPosition.C)
                        else:
                            if self.positionInPossession != SkaterPosition.RW:
                                allPos.append(SkaterPosition.RW)
                            else:
                                allPos.append(SkaterPosition.C)
                        self.positionInPossession = random.sample(allPos, 1)[0]
                        self.ineligibleDefenders.append(defender)
                        self.addEventLog(f"{attacker.name} passes to {self.attackingSkater().name}.")
                        self.clock -= random.randint(1,3) #passes are quick
                    elif atkAction in [AtkAction.SkateA, AtkAction.SkateF, AtkAction.SkateT, AtkAction.SkateB]:
                        if atkAction == AtkAction.SkateB:
                            self.space = True
                        else:
                            self.space = False
                            self.ineligibleDefenders.append(defender) #got around 'em
                        self.addEventLog(f"{attacker.name} skates around.", verbose=True)
                        self.clock -= random.randint(3,6) #skating is slow                       
                    else: #dumped puck
                        raise NotImplementedError           
            else: #defender won
                if defAction in [DefAction.Force, DefAction.Steal, DefAction.Body]: #actions zat grant defender puck at start of action
                    self.changePossession()
                    self.positionInPossession = SkaterPosition(self.skatersDefending().index(defender))
                    if defAction == DefAction.Body:
                        self.addEventLog(f"{defender.name} bodies {attacker.name} off za puck.")
                    else:
                        self.addEventLog(f"{defender.name} takes it away cleanly.")
                    self.clock -= random.randint(4,6)
                elif defAction in [DefAction.Pin, DefAction.Poke]: #actions zat cause loose puck at start of action
                    self.loosePuck = True
                    self.loosePuckDefAdv = defAction == DefAction.Poke
                    self.currentZone = int(random.sample(self.activeGraph().getAdjacentNodes(), 1)[0])
                    self.addEventLog(f"{defender.name} forces za puck loose!")
                    self.clock -= random.randint(2,4)
                elif defAction == DefAction.BlockSlot: #grants defender puck at end of action
                    self.currentZone = nodeTarget
                    self.changePossession()
                    self.positionInPossession = SkaterPosition(self.skatersDefending().index(defender))
                    self.addEventLog(f"{defender.name} blocks a shot and picks up za puck!")
                    self.clock -= random.randint(1,3)
                elif defAction == DefAction.BlockLn: #pass fuckery
                    self.passCheck(nodeTarget, defender, atkAction)
                    self.clock -= random.randint(3,6)
                   
    def passCheck(self, target, blockingDefender, passType):
        if passType == AtkAction.PassS or random.random()*100 < normalDis(blockingDefender.getAttribute("Ref"),30,20,80): #stretch pass always intercepted, chance for interception based on defender's reflexes
            self.currentZone = target
            self.changePossession()
            self.positionInPossession = SkaterPosition(self.skatersDefending().index(blockingDefender))
            self.addEventLog(f"{blockingDefender.name} intercepts a pass and takes it cleanly!")
        else: #loose puck!
            if random.random() > 0.5:
                self.currentZone = target
            self.loosePuck = True
            self.loosePuckDefAdv = True
            self.addEventLog(f"Za pass is knocked loose!")
        
        
            
    def goalieCheck(self, shotType, shooter):
        atkMult = self.activeGraph().shotDanger(self.currentZone)/100 #worse shots furzher out
        if shotType == AtkAction.ShotS: #slapshot
            shooterSkills = [('Sho', 80*atkMult), ('Str', 30*atkMult)]
            goalieSkills = [('Ref', 90)]
        else: #wristshot
            shooterSkills = [('Sho', 50*atkMult), ('Dex', 30*atkMult)]
            goalieSkills = [('Ref', 80),('Agi', 20)]
        params = SkillContestParams(shooterSkills, goalieSkills)
        result = self.skillContest(shooter,self.defendingGoalie(),params)
        if result: #GOAL
            if self.homeAttacking():
                self.homeScore += 1
            else:
                self.awayScore += 1
            self.playStopped = True
            self.addEventLog(f"{self.clockToMinutesSeconds()} - {shooter.name} scores! New score: {self.away.shortname} {self.awayScore} - {self.homeScore} {self.home.shortname}")
            self.faceoffSpot = FaceoffDot.Center
        elif random.randint(0,100) < normalDis(self.defendingGoalie().getAttribute('Dex'),75,0,100): #caught puck
            self.saveMadeStop(shooter, shotType)
        else: #blocked shot
            self.loosePuck = True
            self.loosePuckDefAdv = True
            self.currentZone = random.sample(self.activeGraph().getAdjacentNodes(27),1)[0]
            self.addEventLog(f"{self.clockToMinutesSeconds()} - shot knocked aside by {self.defendingGoalie().name}.")
        self.clock -= random.randint(2,6)
            
    def changePossession(self):
        self.teamInPossession = self.away if self.homeAttacking() else self.home
        #gotta flip node
        self.currentZone = 47 - self.currentZone

    def saveMadeStop(self, shootingPlayer, shotType):
        """Stops play due to a save made by a goalie, and sets the faceoff dot to be used."""
        self.playStopped = True
        eventText = f"{self.clockToMinutesSeconds()} - {str(self.defendingGoalie)} saves shot from {str(shootingPlayer)}, stops play."
        self.eventLog.append(eventText)
        self.eventLogVerbose.append(eventText)
        options = [FaceoffDot.AwayZoneLeft, FaceoffDot.AwayZoneRight] if self.homeAttacking() else [FaceoffDot.HomeZoneLeft, FaceoffDot.HomeZoneRight]
        self.faceoffSpot = random.sample(options,1)[0]

    def stopPlay(self):
        """Stops play due to a knocked down puck, puck in the netting or benches, or otherwise generic call that needs the closest dot."""
        self.playStopped = True
        self.eventLogVerbose.append("Play whistled dead.")
        if self.homeAttacking():
            defenseDots = [FaceoffDot.HomeZoneRight, FaceoffDot.HomeZoneLeft]
            neutralDefDots = [FaceoffDot.HomeNeutralRight, FaceoffDot.HomeNeutralLeft, FaceoffDot.Center]
            neutralOffDots = [FaceoffDot.AwayNeutralRight, FaceoffDot.AwayNeutralLeft, FaceoffDot.Center]
            offenseDots = [FaceoffDot.AwayZoneRight, FaceoffDot.AwayZoneLeft]
        else:
            offenseDots = [FaceoffDot.HomeZoneRight, FaceoffDot.HomeZoneLeft]
            neutralOffDots = [FaceoffDot.HomeNeutralRight, FaceoffDot.HomeNeutralLeft, FaceoffDot.Center]
            neutralDefDots = [FaceoffDot.AwayNeutralRight, FaceoffDot.AwayNeutralLeft, FaceoffDot.Center]
            defenseDots = [FaceoffDot.AwayZoneRight, FaceoffDot.AwayZoneLeft]
        if int(self.currentZone[1]) <= 2: #defensive end
            dots = defenseDots
        elif int(self.currentZone[1]) >= 5: #offensive end
            dots = offenseDots
        elif int(self.currentZone[1]) == 3:
            dots = neutralDefDots
        else:
            dots = neutralOffDots
        self.faceoffSpot = random.sample(dots, 1)[0]

    def stopPlayOffsides(self):
        """Stops play due to an offsides call."""
        self.playStopped = True
        eventText = f"{self.teamInPossession.shortname} goes offsides."
        self.eventLog.append(eventText)
        self.eventLogVerbose(eventText)
        if self.homeAttacking():
            dots = [FaceoffDot.AwayNeutralLeft, FaceoffDot.AwayNeutralRight]
        else:
            dots = [FaceoffDot.HomeNeutralLeft, FaceoffDot.HomeNeutralRight]
        self.faceoffSpot = random.sample(dots, 1)[0]

    def stopPlayIcing(self):
        """Stops play due to an icing call."""
        self.playStopped = True
        eventText = f"{self.teamInPossession.shortname} ices the puck."
        self.eventLog.append(eventText)
        self.eventLogVerbose(eventText)
        if self.homeAttacking():
            dots = [FaceoffDot.HomeZoneLeft, FaceoffDot.HomeZoneRight]
        else:
            dots = [FaceoffDot.AwayZoneLeft, FaceoffDot.AwayZoneRight]
        self.faceoffSpot = random.sample(dots, 1)[0]

    def stopPlayPenalty(self, offendingPlayer:Player, penaltyText:str):
        """Stops play due to an icing call."""
        self.playStopped = True
        ppTeam = self.home if self.away.isPlayerOnTeam(offendingPlayer) else self.away
        eventText = f"{str(self.offendingPlayer)} is called for {penaltyText}. {ppTeam.shortname} is on the powerplay."
        self.powerPlaySetup()
        self.eventLog.append(eventText)
        self.eventLogVerbose(eventText)
        if self.homeAttacking():
            dots = [FaceoffDot.HomeZoneLeft, FaceoffDot.HomeZoneRight]
        else:
            dots = [FaceoffDot.AwayZoneLeft, FaceoffDot.AwayZoneRight]
        self.faceoffSpot = random.sample(dots, 1)[0]

    def powerPlaySetup(self):
        raise NotImplementedError()
    
    def addEventLog(self, eventString, verbose:bool=False):
        if not verbose:
            self.eventLog.append(eventString)
        self.eventLogVerbose.append(eventString)

    def eventLogLength(self):
        count = 0
        for line in self.eventLog:
            count += len(line)+1 #the extra 1 is for the newline at the end
        return count

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