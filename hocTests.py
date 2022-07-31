import skillContests, player, team, game, attributes, os


class AttributeTest(object):
    def __init__(self):
        self.atkAction = player.AtkAction.ShotW
        self.defAction = player.DefAction.BlockSlot

        self.atkPlayer = player.Player(None)
        self.defPlayer = player.Player(None)

        self.fakeGame = game.Game(None, None)

        self.params = skillContests.SkillContestParams().actionCheck(self.atkAction, self.defAction)

    def lowStats(self):
        """Tests attacker and defender with minimum stats."""
        for i in [0,1]:
            setPlayer = [self.atkPlayer, self.defPlayer][i]
            statSet = [self.params.atkStats, self.params.defStats][i]
            for shortname, weight in statSet:
                longname, value = attributes.singleAttribute(shortname)
                setPlayer.setAttribute(longname, attributes.attributeMinMax(longname)[0]+5)
        self.getAvg("mutual minimum stats")

    def lowAtkHighDef(self):
        for shortname, weight in self.params.atkStats:
            longname, value = attributes.singleAttribute(shortname)
            self.atkPlayer.setAttribute(longname, attributes.attributeMinMax(longname)[0]+5)
        for shortname, weight in self.params.defStats:
            longname, value = attributes.singleAttribute(shortname)
            self.defPlayer.setAttribute(longname, attributes.attributeMinMax(longname)[1]-5)
        self.getAvg("bad attack, good defence")

    def highAtkLowDef(self):
        for shortname, weight in self.params.atkStats:
            longname, value = attributes.singleAttribute(shortname)
            self.atkPlayer.setAttribute(longname, attributes.attributeMinMax(longname)[1]-5)
        for shortname, weight in self.params.defStats:
            longname, value = attributes.singleAttribute(shortname)
            self.defPlayer.setAttribute(longname, attributes.attributeMinMax(longname)[0]+5)
        self.getAvg("good attack, bad defence")

    def highStats(self):
        for i in [0,1]:
            setPlayer = [self.atkPlayer, self.defPlayer][i]
            statSet = [self.params.atkStats, self.params.defStats][i]
            for shortname, weight in statSet:
                longname, value = attributes.singleAttribute(shortname)
                setPlayer.setAttribute(longname, attributes.attributeMinMax(longname)[1]-5)
        self.getAvg("mutual maximum stats")

    def randomStats(self):
        success = 0
        total = 0
        for i in range(0, 5000):
            for shortname, weight in self.params.atkStats:
                self.atkPlayer.setAttribute(*attributes.singleAttribute(shortname))
            for shortname, weight in self.params.defStats:
                self.defPlayer.setAttribute(*attributes.singleAttribute(shortname))
            total += 1
            success += self.fakeGame.skillContest(self.atkPlayer, self.defPlayer, self.params)
        print(f"Testing random stats...")
        print(f"Success rate: {str(round(success/total*100,2))}%")
        print("-------")


    def allTests(self):
        self.lowStats()
        self.lowAtkHighDef()
        self.highAtkLowDef()
        self.highStats()
        self.randomStats()

    def getAvg(self, testName:str):
        success = 0
        total = 0
        for i in range(0, 5000):
            total += 1
            success += self.fakeGame.skillContest(self.atkPlayer, self.defPlayer, self.params)
        print(f"Testing {testName}...")
        print("Attacker stat values:")
        for attr, w in self.params.atkStats:
            print(self.atkPlayer.getAttribute(attr))
        print("Defender stat values:")
        for attr, w in self.params.defStats:
            print(self.defPlayer.getAttribute(attr))
        print(f"Success rate: {str(round(success/total*100,2))}%")
        print("-------")


class TestGame(object):

    def __init__(self):
        awayRoster = [
                player.Player("Laika", 93),
                player.Player("Vivi", 16),
                player.Player("Jorts", 75),
                player.Player("Yuki", 23),
                player.Player("Konecny", 96),
                player.Player("Laika", 93),
                player.Player("Vivi", 16),
                player.Player("Jorts", 75),
                player.Player("Yuki", 23),
                player.Player("Konecny", 11)
            ]
        homeRoster = [
                player.Player("Landeskog", 92),
                player.Player("Byram", 4),
                player.Player("MacKinnon", 29),
                player.Player("Makar", 8),
                player.Player("Rantanen", 96),
                player.Player("Landeskog", 92),
                player.Player("Byram", 4),
                player.Player("MacKinnon", 29),
                player.Player("Makar", 8),
                player.Player("Rantanen", 96)
            ]


        aTeam = team.Team(awayRoster, [player.Player('Artemis', 17)], "Vail Powder", "PDR")
        hTeam = team.Team(homeRoster, [player.Player('Kuemper', 35)], "Colorado Avalanche", "COL")
        self.Game = game.Game(aTeam, hTeam)

    def faceoffTest(self):
        for i in range(0,8):
            self.Game.playStopped = True
            foResult = self.Game.event() #this doesnt return anything but it's nice to know what it's for I guess
        lines = self.Game.eventLogOut()
        print(lines)