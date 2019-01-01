import TelegramBot
import urllib2
from bs4 import BeautifulSoup
import time
import TrackManiaRank
import emoji
import json
import os

token = "608105554:AAFeglfX6Ac-T8Ry4-mWENsBvaxVbjhOokI"
bot = TelegramBot.TelegramBot(token)

telegramDataPath = "./chatIDToURL.txt"
url = "https://players.turbo.trackmania.com/ps4/profile/dypygafo-ps45ad85262982be"
trackMania = TrackManiaRank.TrackManiaRank()


folder = "./test/hallo/leben.txt"
if not os.path.exists(folder):
    os.makedirs(folder)


chatIDToUrl = {}

def loadChatIDToURL():
    exists = os.path.isfile(telegramDataPath)
    if not exists:
        f = open(telegramDataPath,"w+")
        print "Create new File"
    with open(telegramDataPath) as f:
        try:
            data = json.load(f)
            return data
        except ValueError:
            return {}
    return {}

def getDifferenceForMessageWithEmoji(value):
    em = ""
    if value < 0:
        value = "-"+str(value)
        em = emoji.emojize('red_circle:', use_aliases=True)
    elif value >0:
        value = "+"+str(value)
        em = emoji.emojize(':thumbsup:', use_aliases=True)

    return " ("+str(value)+" "+em+")\n"

def getMessageFromResult(result):
    message = str(result["player"])+" is on Rank:\n"

    message = message+str("World: "+str(result["world"]))
    message = message+getDifferenceForMessageWithEmoji(result["worldDiff"])

    message = message+str(str(result["land"])+": "+str(result["landRank"]))
    message = message+getDifferenceForMessageWithEmoji(result["landRankDiff"])

    message = message+str(str(result["zip"])+": "+str(result["zipRank"]))
    message = message+getDifferenceForMessageWithEmoji(result["zipRankDiff"])

    return message

def saveChatIDAndURL(chat_id,url):
    chatIDToUrl[chat_id] = url
    with open(telegramDataPath,"w") as f:
        json.dump(chatIDToUrl,f)

def getURLFromChatID(chat_id):
    chat_id = str(chat_id)
    if chat_id in chatIDToUrl:
        return chatIDToUrl[chat_id]
    return None

def register(chat_id,msg):
    if(msg!=None):
        saveChatIDAndURL(chat_id,msg)
    else:
        bot.sendToChatID(chat_id,"Please enter your profile url")

def getRank(chat_id,msg):
    print msg
    url = getURLFromChatID(chat_id)
    if url == None:
        bot.sendToChatID(chat_id,"Please use /register")
        return
    result = trackMania.getPlayerInformations(url)
    message = getMessageFromResult(result)
    bot.sendToChatID(chat_id,message)


def sendToAllSubscribersTheirRank():
    for subscriber in bot.getAllSubscribers():
        chat_id = subscriber.strip()
        print chatIDToUrl[chat_id]
        if chat_id in chatIDToUrl:
            bot.sendToChatID(chat_id,emoji.emojize('Python is /play secret/', use_aliases=True))
            url = chatIDToUrl[chat_id]
            result = trackMania.getPlayerInformations(url)
            message = getMessageFromResult(result)
            bot.sendToChatID(chat_id,message)


chatIDToUrl = loadChatIDToURL()
print chatIDToUrl
botName = "trackmaniabot"
bot.registerCommand("/rank",getRank,"Shows your Rank")
bot.registerCommand("/register",register,"Enter your URL")
bot.start()

#                       December 30, 2018 at 6:20:02 AM GMT
#Letzte Aktualisierung: 31. Dezember 2018 um 06:20:01 GMT

print "Starting TelegramBot: "+botName
while True:
    sendToAllSubscribersTheirRank()
    '''Get Updates and send them to the Players'''
    time.sleep(60*60*23) #wait 23h
    time.sleep(60*50)    #and 50 Minutes

    while not bot.newUpdateOnline():# while no new updates
        time.sleep(60*1) #wait a minute and check again
