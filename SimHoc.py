import os, player, time, skillContests, random, itertools, json
from cohost.models.user import User
from cohost.models.block import AttachmentBlock, MarkdownBlock
from attributes import normalDis
from hocTests import AttributeTest, TestGame
from hocUtils import RinkGraph
from player import Player

def auzh():
    """
    returns login cookie
    """
    with open("./Data/auth.txt", "r") as file:
        return file.readline().strip()


if __name__ == "__main__":
    #for name in ["Vivi", "Artemis", "Laika", "Sharks", "Dragons", "Melua", "Sabriina", "Jorts (Buttered)", "Jorts (Unbuttered)"]:
    #    plyr = player.Player(name)
    #    print(f"{name}:")
    #    for atr in plyr.attributes:
    #        print(atr)
    #    print("----------")

    #g = TestGame()
    #g.faceoffTest()


    cookie = auzh()
    user = User.loginWithCookie(cookie)
    project = user.getProject('ashl')
    #zhisPlayer = Player("Abyss",16)
    
    #blocks = [MarkdownBlock("Testing new version of API shares")]
    #newPost = project.post('', blocks, tags=['dont make fun of me', 'zis is hard'], shareOfPostId=7294245)
    
    #blocks = [
        #AttachmentBlock('pybug.png'), # References image file pybug.png
        #MarkdownBlock(zhisPlayer.statsString()) # Example of markdown / text block
        #MarkdownBlock("did i break not-shares?")
    #]
    #newPost = project.post('', blocks, tags=['nope good job'])