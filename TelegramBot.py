import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import os
from telepot.delegate import (
    per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)

propose_records = telepot.helper.SafeDict()  # thread-safe dict
botClass = None

class MyHelper(telepot.helper.ChatHandler):

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                   InlineKeyboardButton(text='Yes', callback_data='yes'),
                   InlineKeyboardButton(text='um ...', callback_data='no'),
               ]])

    def __init__(self, *args, **kwargs):
        super(MyHelper, self).__init__(*args, **kwargs)

        # Retrieve from database
        global propose_records
        if self.id in propose_records:
            self._count, self._edit_msg_ident = propose_records[self.id]
            self._editor = telepot.helper.Editor(self.bot, self._edit_msg_ident) if self._edit_msg_ident else None
        else:
            self._count = 0
            self._edit_msg_ident = None
            self._editor = None

    def _propose(self):
        self._count += 1
        sent = self.sender.sendMessage('%d. Would you marry me?' % self._count, reply_markup=self.keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_msg_ident = telepot.message_identifier(sent)

    def _cancel_last(self):
        if self._editor:
            self._editor.editMessageReplyMarkup(reply_markup=None)
            self._editor = None
            self._edit_msg_ident = None

    def on_chat_message(self, msg):
        global botClass
        botClass.messageReceived(msg,self)

    def on_callback_query(self, msg):
        global botClass
        callback = botClass.getCallbackQueryFunction()
        callback(msg,self)

    def on__idle(self, event):
        #self.sender.sendMessage('I know you may need a little time. I will always be here for you.')
        #self.close()
        pass

    def on_close(self, ex):
        # Save to database
        global propose_records
        propose_records[self.id] = (self._count, self._edit_msg_ident)







class TelegramBot:
    subscribers = []
    subscriberFile = "./TelegramBotSubscribers.txt"
    commands = []
    callback_query_function = None
    callback_remaining_message_function = None
    bot = None

    def dummyOtherFunction(self,msg,MyHelper):
        pass

    def setCallbackRemainingMessageFunction(self,function):
        self.callback_remaining_message_function = function

    def getCallbackRemainingMessageFunction(self):
        if self.callback_remaining_message_function != None:
            return self.callback_remaining_message_function
        return dummyFunction

    def setCallbackQueryFunction(self,function):
        self.callback_query_function = function

    def getCallbackQueryFunction(self):
        if self.callback_query_function != None:
            return self.callback_query_function
        return dummyOtherFunction

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
                    subscriber = str(subscriber).strip()
                    if subscriber != None and subscriber != "\n" and subscriber != "":
                        self.subscribe(subscriber)

    def messageReceived(self,msg,MyHelper):
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
            callback(chat_id,MyHelper,parameters)
        else:
            callback = self.getCallbackRemainingMessageFunction()
            callback(chat_id,MyHelper,msg['text'])

    def __init__(self,token):
        self.token = token
        self.loadSubscribers()
        self.bot = "Moin"

    def getBot(self):
        return self.bot

    def start(self):
        self.bot = telepot.DelegatorBot(self.token, [include_callback_query_chat_id(pave_event_space())(per_chat_id(types=['private']), create_open, MyHelper, timeout=10),])
        global botClass
        botClass = self
        MessageLoop(self.bot).run_as_thread()
        #self.sendToAll("I'm online")

    def sendToAll(self,message):
        for subscriber in self.subscribers:
            self.sendToChatID(subscriber,message)

    def sendToChatID(self,chat_id,message):
        return self.bot.sendMessage(chat_id,message)

    def sendFileToChatID(self,chat_id,pathToFile):
        return self.bot.sendPhoto(chat_id, open(pathToFile, 'rb'))

    def isSubscriber(self,chat_id):
        return str(chat_id) in self.subscribers

    def subscribe(self,chat_id):
        if not self.isSubscriber(str(chat_id)):
            self.subscribers.append(str(chat_id).strip())
            self.saveSubscribers()

    def unsubscribe(self,chat_id):
        self.subscribers.remove(str(chat_id).strip())
        self.saveSubscribers()
