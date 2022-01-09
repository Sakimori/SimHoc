import os, player, tweepy, twitHandler, time, skillContests, random
from attributes import normalDis

if __name__ == "__main__":
    #for name in ["Vivi", "Artemis", "Laika", "Sharks", "Dragons", "Melua", "Sabriina", "Jorts (Buttered)", "Jorts (Unbuttered)"]:
    #    plyr = player.Player(name)
    #    print(f"{name}:")
    #    for atr in plyr.attributes:
    #        print(atr)
    #    print("----------")

    atkPlayer = player.Player("Vivi")
    defPlayer = player.Player("Artemis")
    for plyr in [atkPlayer, defPlayer]:
        print(f"{plyr.name}:")
        for atr in plyr.attributes:
            print(atr)
        print("----------")


    def skillContest(atkPlayer:player.Player, defPlayer:player.Player, params:skillContests.SkillContestParams):
        """Contests the two players with the given stats and stat weights. Returns True on offensive success."""
        if params.override is not None:
            print(params.override)
        else:
            atkValue = 0
            defValue = 0
            for attr, weight in params.atkStats:
                atkValue += 95 * weight/100
            for attr, weight in params.defStats:
                defValue += 35 * weight/100

            print(f"Attack: {atkValue}")
            print(f"Defense:{defValue}")

            success = 0
            total = 5000

            for i in range(0,5000):
                atkRoll = normalDis(atkValue, atkValue/2, 0)
                defRoll = normalDis(defValue, defValue/2, 0)
                success += (atkRoll-defRoll) > 0
            print(f"Success {round(success/total*100,3)}% of the time.")

    defAction = player.DefAction.Poke
    for atkAction in [player.AtkAction.SkateF]:
        params = skillContests.SkillContestParams(atkAction, defAction, skillContests.Situations.EvenStrength)
        skillContest(atkPlayer, defPlayer, params)

    #twitter = twitHandler.TwitHandler()
    #if os.path.exists(os.path.join("Data", "lastID.twt")):
    #    with open(os.path.join("Data", "lastID.twt")) as idFile:
    #        lastID = idFile.readline().strip()
    #else:
    #    lastID = 0

    #while True:
    #    twitter.scanForMention(lastID)
    #    time.sleep(30)
    #    with open(os.path.join("Data", "lastID.twt")) as idFile:
    #        lastID = idFile.readline().strip()


    #twitter.sendTextTweet(player.Player("Amogus").twitterString())

