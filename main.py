import TelegramBot
import urllib2
from bs4 import BeautifulSoup
import time
import TrackManiaRank
import emoji
import json
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from telepot.loop import MessageLoop
import os

bot = None

def loadToken():
    global bot
    tokenPath = "./token.txt"
    exists = os.path.isfile(tokenPath)
    if not exists:
        f = open(tokenPath,"w+")
        print "Please insert a TelegramBot Token in the File './token.txt'"
        return False
    with open(tokenPath,"r") as f:
            for line in f:
                    bot = TelegramBot.TelegramBot(str(line))   
                    return True


if not loadToken():
    print "Programm is now stopping"
    exit()



telegramDataPath = "./chatIDToURL.txt"
trackMania = TrackManiaRank.TrackManiaRank()

chatIDToUrl = telepot.helper.SafeDict()  # thread-safe dict

def loadChatIDToURL():
    exists = os.path.isfile(telegramDataPath)
    if not exists:
        f = open(telegramDataPath,"w+")
    with open(telegramDataPath) as f:
        try:
            data = json.load(f)
            return data
        except ValueError:
            return telepot.helper.SafeDict()
    return telepot.helper.SafeDict()

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

def isChatIDRegistered(chat_id):
    chat_id = str(chat_id)
    if chat_id in chatIDToUrl:
        return True
    return False

def saveChatIDAndURL(chat_id,url):
    chatIDToUrl[chat_id] = url
    with open(telegramDataPath,"w") as f:
        json.dump(chatIDToUrl,f)

def getURLFromChatID(chat_id):
    chat_id = str(chat_id)
    if isChatIDRegistered(chat_id):
        return chatIDToUrl[chat_id]
    return None

def register(chat_id,MyHelper,msg):
    if trackMania.isValidURL(msg):
        saveChatIDAndURL(str(chat_id),str(msg))
    else:
        bot.sendToChatID(chat_id,"That was not correct, see /start")

def unregister(chat_id,MyHelper,msg):
    if str(chat_id) in chatIDToUrl:
        del chatIDToUrl[str(chat_id)]
    bot.sendToChatID(chat_id,"Your are unregistered, retry with /start")

def sendRank(chat_id):
    url = getURLFromChatID(chat_id)
    if not trackMania.isValidURL(url):
        unregister(chat_id,None,"")
        bot.sendToChatID(chat_id,"That was not correct, see /start")
        return
    result = trackMania.getPlayerInformations(url)
    message = getMessageFromResult(result)
    bot.sendToChatID(chat_id,message)


def sendToAllSubscribersTheirRank():
    for subscriber in bot.getAllSubscribers():
        chat_id = subscriber.strip()
        if isChatIDRegistered(chat_id):
            #bot.sendToChatID(chat_id,"Bot started")
            sendRank(chat_id)
            sendKeyBoard(chat_id)


keyboardNotSubscribed = InlineKeyboardMarkup(inline_keyboard=[[
                   InlineKeyboardButton(text='Subscribe', callback_data='subscribe'),
                   InlineKeyboardButton(text='Rank', callback_data='rank'),
               ]])
keyboardSubscribed = InlineKeyboardMarkup(inline_keyboard=[[
                   InlineKeyboardButton(text='Unsubscribe', callback_data='unsubscribe'),
                   InlineKeyboardButton(text='Rank', callback_data='rank'),
               ]])


newConversationMessage = "Welcome to the TrackManiaBot!\n With this Bot you can get Informations about your online rank, daily or on request. \n\n"
newConversationMessage = newConversationMessage+ "1. Make your TrackMania Profile public.\n"
newConversationMessage = newConversationMessage+ "2. Send your profile URL\n"
linkForPS4 = "https://players.turbo.trackmania.com/ps4/profile"
ProfilePrivacyImage = "./ProfilePrivacy.png"

def newConversation(chat_id,MyHelper,msg):
    if isChatIDRegistered(chat_id):
        bot.sendToChatID(chat_id,"Welcome back")
        sendKeyBoard(chat_id)
    else:
        bot.sendToChatID(chat_id,newConversationMessage)
        bot.sendToChatID(chat_id,linkForPS4)
        bot.sendFileToChatID(chat_id,ProfilePrivacyImage)

def getKeyBoard(chat_id):
    if isChatIDRegistered(chat_id):
        if bot.isSubscriber(chat_id):
            return keyboardSubscribed
        else:
            return keyboardNotSubscribed
    else:
        return None

def sendKeyBoard(chat_id):
    message = "Select:"
    if isChatIDRegistered(chat_id):
            bot.getBot().sendMessage(chat_id,message, reply_markup=getKeyBoard(chat_id))
    else:
        bot.sendToChatID(chat_id,"Register Yourself please")

def on_callback_query(msg,MyHelper):
    chat_id = msg['from']['id']
    query_data = msg['data']

    MyHelper._count += 1

    if query_data == "subscribe":
        MyHelper._cancel_last()
        bot.subscribe(chat_id)
        sent = MyHelper.sender.sendMessage("Subscribed! You receive now every day a new update", reply_markup=getKeyBoard(chat_id))
        MyHelper._editor = telepot.helper.Editor(MyHelper.bot, sent)
        MyHelper._edit_msg_ident = telepot.message_identifier(sent)
        return
    elif query_data == "unsubscribe":
        MyHelper._cancel_last()
        bot.unsubscribe(chat_id)
        sent = MyHelper.sender.sendMessage("Unfortunately Unsubscribed :-( Hope you enjoyed!", reply_markup=getKeyBoard(chat_id))
        MyHelper._editor = telepot.helper.Editor(MyHelper.bot, sent)
        MyHelper._edit_msg_ident = telepot.message_identifier(sent)
        return
    elif query_data == "rank":
        if isChatIDRegistered(chat_id):
            url = getURLFromChatID(chat_id)
            if trackMania.isValidURL(url):
                result = trackMania.getPlayerInformations(url)
                message = getMessageFromResult(result)
                MyHelper._cancel_last()
                sent = MyHelper.sender.sendMessage(message, reply_markup=getKeyBoard(chat_id))
                MyHelper._editor = telepot.helper.Editor(MyHelper.bot, sent)
                MyHelper._edit_msg_ident = telepot.message_identifier(sent)
            return
        return

def remainingMessageCallback(chat_id,MyHelper,msg):
    state = trackMania.getURLState(msg)
    if state == "wrong":
        bot.sendToChatID(chat_id,"This was not the correct Website.\n Please give me your Profile URL: ")
        bot.sendToChatID(chat_id,linkForPS4)
    if state == "privat":
        bot.sendToChatID(chat_id,"Woaah, you forgot to set your Profive Public")
        bot.sendFileToChatID(chat_id,ProfilePrivacyImage)
    if state == "valid":
        MyHelper._cancel_last()
        register(chat_id,MyHelper,msg)
        sent = MyHelper.sender.sendMessage("That's a valid URL", reply_markup=getKeyBoard(chat_id))
        MyHelper._editor = telepot.helper.Editor(MyHelper.bot, sent)
        MyHelper._edit_msg_ident = telepot.message_identifier(sent)


bot.setCallbackQueryFunction(on_callback_query)
#bot.registerCommand("/rank",getRank,"Displays your Rank")
bot.registerCommand("/register",register,"Registers yourself")
bot.registerCommand("/unregister",unregister,"Unregister yourself")
bot.registerCommand("/start",newConversation,"Show Start Informations")
bot.setCallbackRemainingMessageFunction(remainingMessageCallback)
bot.start()

chatIDToUrl = loadChatIDToURL()
botName = "trackmaniabot"
minutesSleep = 60

print "Starting TelegramBot: "+botName
while True:
    sendToAllSubscribersTheirRank()
    while not trackMania.newUpdateOnline():# while no new updates
        print "No New Update, check again in "+str(minutesSleep)+" minutes"
        time.sleep(minutesSleep*10) #wait a minute and check again
        
    print "New Update found"


