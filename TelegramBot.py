import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import os

class TelegramBot:
    subscribers = []
    subscriberFile = "./TelegramBotSubscribers.txt"
    commands = []

    def getAllSubscribers(self):
        return list(self.subscribers)

    def registerCommand(self, cmd, callback,helpText):
        self.commands.append([cmd,callback,helpText])

    def displayHelp(self,chat_id):
        helpText = "Please use '/help command' to get more Information about a command "
        self.sendToChatID(chat_id,helpText)

    def getCommandTuple(self,cmd):
        for tuple in self.commands:
            if tuple[0] == cmd:
                return tuple
        return None

    def isRegisteredCommand(self,cmd):
        return self.getCommandTuple(cmd) != None

    def displayCommandHelpText(self,chat_id,cmd):
        helpText = self.getCommandTuple(cmd)[2]
        self.sendToChatID(chat_id,helpText)

    def saveSubscribers(self):
        with open(self.subscriberFile, 'w') as f:
            for subscriber in self.subscribers:
                if subscriber != None and subscriber != "\n" and subscriber != "":
                    f.write("%s\n" % subscriber)

    def loadSubscribers(self):
        exists = os.path.isfile(self.subscriberFile)
        if exists:
            with open(self.subscriberFile, 'r') as f:
                for subscriber in f:
                    if subscriber != None and subscriber != "\n" and subscriber != "":
                        self.subscribe(subscriber)

    def messageReceived(self,msg):
        chat_id = msg['chat']['id']
        command = msg['text']

        if command == "/help":
            self.displayHelp(chat_id)
        elif command == "/subscribe":
            self.subscribe(chat_id)
            self.sendToChatID(chat_id,"You receive now updates")
        elif command == "/unsubscribe":
            self.unsubscribe(chat_id)
            self.sendToChatID(chat_id,"You will no longer receive updates")
        elif command.startswith("/help "):
            helpWithCommand = command[5:]
            if helpWithCommand in self.commands:
                self.displayCommandHelpText(chat_id,helpWithCommand)

        splits = command.split(" ",1)
        onlyCommand = splits[0]
        parameters = None
        if len(splits)>1:
            parameters = splits[1]

        if self.isRegisteredCommand(onlyCommand):
            callback = self.getCommandTuple(onlyCommand)[1]
            callback(chat_id,parameters)

    def __init__(self,token):
        self.token = token
        self.loadSubscribers()

    def start(self):
        self.bot = telepot.Bot(self.token)
        MessageLoop(self.bot,{'chat':self.messageReceived}).run_as_thread()
        self.sendToAll("I'm online")

    def sendToAll(self,message):
        for subscriber in self.subscribers:
            print("Send Message to: ")
            print("<<<"+subscriber+">>>")
            self.sendToChatID(subscriber,message)

    def sendToChatID(self,chat_id,message):
        self.bot.sendMessage(chat_id,message)

    def isSubscriber(self,chat_id):
         return chat_id in self.subscribers

    def subscribe(self,chat_id):
         if not self.isSubscriber(chat_id):
            self.subscribers.append(chat_id)
            self.saveSubscribers()

    def unsubscribe(self,chat_id):
         self.subscribers.remove(chat_id)
         self.saveSubscribers()
