import os, player, tweepy, twitHandler, time, skillContests, random, itertools
from attributes import normalDis
from hocTests import AttributeTest
from hocUtils import RinkGraph




if __name__ == "__main__":
    #for name in ["Vivi", "Artemis", "Laika", "Sharks", "Dragons", "Melua", "Sabriina", "Jorts (Buttered)", "Jorts (Unbuttered)"]:
    #    plyr = player.Player(name)
    #    print(f"{name}:")
    #    for atr in plyr.attributes:
    #        print(atr)
    #    print("----------")

    g = RinkGraph(edgeFilename="defaultedges.nx")
    g.getNodeDebug('25')


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

