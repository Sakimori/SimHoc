import tweepy, os, json, player

dataDir = "Data"

class TwitHandler(object):
    """Twitter connection handler class"""
    api = tweepy.Client()

    def __init__(self):
        path = os.path.join(dataDir, "Twitter.keys")
        if os.path.exists(path):
            with open(path) as keysFile:
                bearerToken, consumerKey, consumerSecret, accessKey, accessSecret = [line.strip() for line in keysFile.readlines()]
        else:
            raise FileNotFoundError
        self.api = tweepy.Client(bearerToken, consumerKey, consumerSecret, accessKey, accessSecret)

    def scanForMention(self, lastRepliedID):
        mentions = self.api.get_users_mentions(1479541275862908928, since_id=lastRepliedID, max_results=20)
        if mentions.data is None or len(mentions.data) == 0:
            return

        for mention in reversed(mentions.data): #do oldest first
            lastID = mention.id

            if "rate " in mention.text.lower():
                try:
                    name = mention.text.split("rate ",1)[1]
                    self.sendTextReply(player.Player(name).twitterString(), mention)
                except:
                    print("Tweet already replied to.")

        with open(os.path.join(dataDir, "lastID.twt"), 'w') as file:
            file.write(str(lastID+1))



    def sendTextTweet(self, text:str):
        self.api.create_tweet(text=text)

    def sendTextReply(self, text:str, prevTweet):
        self.api.create_tweet(in_reply_to_tweet_id=prevTweet.id, text=text)

    def changeBio(self, newText):
        pass #awaiting API v1 permission