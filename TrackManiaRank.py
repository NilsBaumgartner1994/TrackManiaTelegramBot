import urllib2
import os
from bs4 import BeautifulSoup
import json

class TrackManiaRank:
    lastUpdate = None
    dataPath = "./trackmaniaData/"
    defaultUrl = "https://players.turbo.trackmania.com/"

    def getPathToPlayerInformation(self,url):
        url = url[len(self.defaultUrl):]
        splits = url.split("/")
        return self.dataPath+splits[0]+"/"+splits[2]+".txt"

    def savePlayerInformationToFile(self,url,recentInformations):
        path = self.getPathToPlayerInformation(url)
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path))

        with open(path,"a") as f:
            json.dump(recentInformations,f)

    def loadLastPlayerInformationFromFileByPath(self,path):
        with open(path,"r") as f:
            for line in f:
                pass
            last = line
            return json.loads(last)

    def getLastPlayerInformationFromFileByUrl(self,url):
        path = self.getPathToPlayerInformation(url)
        if not os.path.exists(path):
            return None
        return self.loadLastPlayerInformationFromFileByPath(path)

#    def loadPlayerInformationAll(self):
 #       for folder in os.listdir(self.dataPath):
  #          for file in os.listdir(self.dataPath+folder):
   #             playerInformation = self.loadLastPlayerInformationFromFile(self.dataPath+folder+"/"+file)
    #            url = self.defaultUrl+folder+"/profile/"+file
     #           self.playerInformations[url] = playerInformation


    def newUpdateOnline(self):
        updateTimeOnHTML = self.getLastUpdate()
        if lastUpdate != updateTimeOnHTML:
            lastUpdate = updateTimeOnHTML
            return True
        return False

    def getLastUpdate(self):
        url = "https://players.turbo.trackmania.com/ps4/rankings"
        response = urllib2.urlopen(url)
        html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        smallTag = soup.findAll("small")
        return smallTag[0].getText()

    def __init__(self):
        pass

    def helperTextToDigit(self,text):
        return int(''.join(i for i in text if i.isdigit()))

    def getDifferenceFromOldToNewFromPlayer(self,newInformations,oldInformations):
        if oldInformations==None or newInformations==None:
            return {"worldDiff":0,"landRankDiff":0,"zipRankDiff":0}

        worldDiff = self.helperTextToDigit(oldInformations["world"])-self.helperTextToDigit(newInformations["world"])
        landDiff = self.helperTextToDigit(oldInformations["landRank"])-self.helperTextToDigit(newInformations["landRank"])
        zipDiff = self.helperTextToDigit(oldInformations["zipRank"])-self.helperTextToDigit(newInformations["zipRank"])
        return {"worldDiff":worldDiff,"landRankDiff":landDiff,"zipRankDiff":zipDiff}

    def getPlayerInformationFromWebsite(self,url):
        response = urllib2.urlopen(url)
        html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        
        playerTag = soup.findAll("div", {"class": "jumbotron header-jumbotron"})
        playerName = playerTag[0].div.h1.getText()

        rankTag = soup.findAll("div", {"class": "col-xs-9 text-right"})
        worldRank = rankTag[0].div.strong.getText()

        land = None
        landRank = None
        
        zip = None
        zipRank = None
        element = 1
        for child in rankTag[0]:
            if(element==3):
                land = child.strip()
            elif(element==4):
                landRank = child.getText()
            elif(element==6):
                zip = child.strip()
            elif(element==7):
                zipRank = child.getText()
            element = element+1

        recentInformations = {"player":playerName,"world":worldRank,"land":land,"landRank":landRank,"zip":zip,"zipRank":zipRank}
        recentInformations["time"] = self.getLastUpdate()
        return recentInformations   

    def checkForNewUpdatesForPlayerAndSaveThem(self,url):
        if(url==None):
            return
        oldInformations = self.getLastPlayerInformationFromFileByUrl(url)
        newInformations = self.getPlayerInformationFromWebsite(url)
        diffs = self.getDifferenceFromOldToNewFromPlayer(newInformations,oldInformations)
        newInformations.update(diffs)
        self.savePlayerInformationToFile(url,newInformations)
        return newInformations

    def getPlayerInformations(self,url):
        if(url==None):
            return None

        lastWebPageUpdate = self.getLastUpdate()
        lastInformations = self.getLastPlayerInformationFromFileByUrl(url)
        if lastInformations == None:
            lastInformations = self.checkForNewUpdatesForPlayerAndSaveThem(url)
        elif lastInformations["time"] != lastWebPageUpdate:
            lastInformations = self.checkForNewUpdatesForPlayerAndSaveThem(url)
 
        return lastInformations

    def getAllPlayersFromPage(self,url):
        response = urllib2.urlopen(url)
        html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        table = soup.findAll("table", {"class": "table table-striped"})
        element = 1
        rankDict = {}
        playerDict = {}

        for row in table[0].find_all("tr"):
            if(element != 1):
                rank = row.td.getText()
                player = row.a.getText().strip()
                rankDict[rank] = player
                playerDict[player] = rank
            element = element +1
        return {"rank":rankDict,"player":playerDict}
