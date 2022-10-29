import datetime as dt
from dateutil.relativedelta import relativedelta
import networkx as nx

from constants import *
import variables as var
from utils.pathClass import netConstructionPathsManager
from utils.networksClasses import Network, devToDevNetworks

from utils.auxiliaryFunctions import datetimeIntoStr
from utils.timelineClass import Timeline

from networksConstruction.auxNetConstruction import isItemDeleted

class NetworksManager():
    def __init__(self):
        self.createNetworks()

        self.initialDate = None

        # INFO FOR TIME LIMITED NETS
        self.timeLimitedFinalDates = []
        self.lastTimeLimitedInitialDate = None

        # INFO FOR TIMELINE
        self.commitId = 1
        self.timeline = Timeline()

        # INFO ABOUT DATES AND FILES PER DATE
        self.initialDate = None
        self.filesPerDate = {}
    
    # ----------------
    # CREATE NETS

    def createNet(self, sm, netType):
        paths: netConstructionPathsManager = var.variablesDict[PATHS]
        return Network(\
            nx.Graph(\
                netPath="{}/{}_{}.pickle".format(paths.getCodeBaseNetsPath(), sm, netType)))

    def createNetworks(self):
        self.netsDict = {
            FILE_TYPE: {
                ALL_TIME: {
                    D2I: None, I2I: None, D2D: None,
                }
            }, \
            METHOD_TYPE: {
                ALL_TIME: {
                    D2I: None, I2I: None, D2D: None,
                }
            }
        }
        for softMod in self.netsDict: # software module (file or method)
            for netType in self.netsDict[softMod][ALL_TIME].keys():
                self.netsDict[softMod][ALL_TIME][netType] = self.createNet(softMod, netType)

    def decideIfCreateTLNets(self, initialDate):
        if initialDate < dt.datetime.now() - relativedelta(days=var.HOW_MANY_DAYS_IN_A_NET):
            self.createTimeLimitedNetworks(initialDate)
            self.lastTimeLimitedInitialDate = initialDate

    def createTimeLimitedNetworks(self, date):
        paths: netConstructionPathsManager = var.variablesDict[PATHS]
    
        for softMod in self.netsDict.keys():
            self.netsDict[softMod][date] = {}
            for netType in [D2I, D2D, I2I]:
                upperTimeLimit = date + relativedelta(days=var.HOW_MANY_DAYS_IN_A_NET)
                lowerTimeLimit, upperTimeLimit = datetimeIntoStr(date), datetimeIntoStr(upperTimeLimit)
                self.netsDict[softMod][date][netType] = Network(\
                    nx.Graph( 
                        netPath="{}/{}_{}_{}_{}.pickle"\
                            .format(paths.getCodeBaseNetsPath(), softMod, netType, lowerTimeLimit, upperTimeLimit)))
    
    # ------------
    # GET NETWORKS

    def getNet(self, fileOrMethod, netType, timeLimitedInfo=ALL_TIME) -> Network:
        return self.netsDict[fileOrMethod][timeLimitedInfo][netType]

    def getTimeLimitedNetworks(self, fileOrMethod, netType) -> list[Network]:
        tlNets = []
        for tlInfo in self.netsDict[fileOrMethod].keys():
            if tlInfo != ALL_TIME:
                tlNets += [self.netsDict[fileOrMethod][tlInfo][netType]]
        
        return tlNets

    def getAllNetworksOfType(self, fileOrMethod, netType) -> list[Network]:
        return [self.getNet(fileOrMethod, netType, ALL_TIME)] + self.getTimeLimitedNetworks(fileOrMethod, netType)

    # ----------------
    # NETWORKS UPDATES
    
    def saveInfoInNets(self, fileOrMethod, author, date, itemsInCommit):
        i2inets = self.getAllNetworksOfType(fileOrMethod, I2I)
        self.establishPossibleRelationsBetweenFiles(i2inets, itemsInCommit)

        for n in self.getAllNetworksOfType(fileOrMethod, D2I):
            commitDatesForDevs = n.getNodeAttributes(ITEM_DATES)
            if author in commitDatesForDevs:
                commitDatesForDev = commitDatesForDevs[author]
            else:
                commitDatesForDev = []
            n.setNodeAttributes({author: {ITEM_DATES: commitDatesForDev + [date]}})

    def addItems(self, fileOrMethod, author, date, itemsInCommit):
        netsToChange = self.getAllNetworksOfType(fileOrMethod, D2I)
        self.addItemsInNets(itemsInCommit, netsToChange, author, date)

    def getOrCreateDeveloper(self, author):
        for n in self.getTimeLimitedNetworks(FILE_TYPE, D2I):
            n.getOrCreateDeveloper(author)
        return self.getNet(FILE_TYPE, D2I, ALL_TIME).getOrCreateDeveloper(author)
    
    def addItemsInNets(self, itemsInCommit, netsToChange: list[Network], author, date):
        for item in itemsInCommit:
            for n in netsToChange:
                n.addEdgeOrWeightToNetwork(author, item, types=[DEV_TYPE, FILE_TYPE], date=date)

    def establishPossibleRelationsBetweenFiles(self, netsToChange: list[Network], itemsInCommit):
        if itemsInCommit != []:
            for x in range(len(itemsInCommit)):
                for y in range(x + 1, len(itemsInCommit)):
                    for n in netsToChange: # i2i; i2i_tr
                        n.addEdgeOrWeightToNetwork(itemsInCommit[x], itemsInCommit[y])

    def removeNodesWithoutChanges(self, fileOrMethod, timeLimitedInfo):
        d2i: Network = self.getNet(fileOrMethod, D2I, timeLimitedInfo)

        iNodes = d2i.getFileNodes() if fileOrMethod == FILE_TYPE else d2i.getMethodNodes()
        for n in iNodes:
            if fileOrMethod == FILE_TYPE:
                if d2i.getDegree(n) == 0:
                    d2i.removeNode(n)
            elif fileOrMethod == METHOD_TYPE:
                if d2i.getDegree(n) == 0:
                    d2i.removeNode(n)

    def removeEliminatedFiles(self, fileOrMethod, timeLimitedInfo):
        d2i: Network = self.getNet(fileOrMethod, D2I, timeLimitedInfo)
        i2i: Network = self.getNet(fileOrMethod, I2I, timeLimitedInfo)

        if fileOrMethod == FILE_TYPE:
            nodesToAnalyzeToRemove = d2i.getFileNodes()
        elif fileOrMethod == METHOD_TYPE:
            nodesToAnalyzeToRemove = d2i.getMethodNodes()
        
        nodesToRemove = list(filter(lambda x: isItemDeleted(x, fileOrMethod), nodesToAnalyzeToRemove))
        for n in nodesToRemove:
            d2i.removeNode(n)
            
            if n in i2i.getNodes():
                i2i.removeNode(n)

    # ----------------
    # TIME LIMITED NETWORKS

    def getTimeLimitedKeys(self, fileOrMethod): 
        tlKeys = []
        for tlInfo in self.netsDict[fileOrMethod].keys():
            if tlInfo != ALL_TIME:
                tlKeys += [tlInfo]
        
        return tlKeys

    def timePeriodHavePassed(self, d2, d1, period):
        secondsInADay = (60 * 60 * 24)
        return (d2 - d1).total_seconds() > secondsInADay * period

    def verifyIfNewTimePeriod(self, actualDate):
        lastTlNetAnalyzedDate = None

        for tlNetInitialDate in self.getTimeLimitedKeys(FILE_TYPE):
            if self.timePeriodHavePassed(actualDate, tlNetInitialDate, var.HOW_MANY_DAYS_IN_A_NET):
                self.saveNets(FILE_TYPE, timeLimitedInfo=tlNetInitialDate)
                self.saveNets(METHOD_TYPE, timeLimitedInfo=tlNetInitialDate)

                lastTlNetAnalyzedDate = tlNetInitialDate

                del self.netsDict[FILE_TYPE][tlNetInitialDate]
                del self.netsDict[METHOD_TYPE][tlNetInitialDate]

        nextBeginningDate = None

        maxTLNets = var.HOW_MANY_DAYS_IN_A_NET / var.DAYS_BETWEEN_NETS
        if lastTlNetAnalyzedDate != None and len(self.timeLimitedFinalDates) >= maxTLNets:
            nextBeginningDate = lastTlNetAnalyzedDate + relativedelta(days=var.HOW_MANY_DAYS_IN_A_NET)
        elif self.lastTimeLimitedInitialDate != None and len(self.timeLimitedFinalDates) < maxTLNets:
            if self.timePeriodHavePassed(actualDate, self.lastTimeLimitedInitialDate, var.DAYS_BETWEEN_NETS):
                self.lastTimeLimitedInitialDate += relativedelta(days=var.DAYS_BETWEEN_NETS)
                nextBeginningDate = self.lastTimeLimitedInitialDate
        
        if nextBeginningDate != None:
            if actualDate > nextBeginningDate + relativedelta(days=var.HOW_MANY_DAYS_IN_A_NET): 
                # happens when there was a gap greater than relativedelta(days=var.HOW_MANY_DAYS_IN_A_NET) between commits...
                while(nextBeginningDate + relativedelta(days=var.HOW_MANY_DAYS_IN_A_NET) < actualDate):
                    self.createTimeLimitedNetworks(nextBeginningDate)
                    self.saveNets(FILE_TYPE, nextBeginningDate)
                    self.saveNets(METHOD_TYPE, nextBeginningDate)
                    nextBeginningDate += relativedelta(days=var.HOW_MANY_DAYS_IN_A_NET)
            else:
                self.createTimeLimitedNetworks(nextBeginningDate)

    # -------------------
    # COLLABORATION NETWORKS

    def createD2DNets(self, fileOrMethod, timeLimitedInfo):
        d2i: Network = self.getNet(fileOrMethod, D2I, timeLimitedInfo)
        d2d: Network = self.getNet(fileOrMethod, D2D, timeLimitedInfo)


        totalItemChanges = 0
        if fileOrMethod == FILE_TYPE:
            itemNodes = d2i.getFileNodes()
            allDevs = d2i.getDeveloperNodes()
        elif fileOrMethod == METHOD_TYPE:
            itemNodes = d2i.getMethodNodes()
            d2f: Network = self.getNet(FILE_TYPE, D2I, timeLimitedInfo)
            allDevs = d2f.getDeveloperNodes()

        for dev in allDevs:
            d2d.addNode(dev)

        for iNo in itemNodes:
            changesInINo = d2i.degreeOfNode(iNo, weight=ST_WEIGHT)
            totalItemChanges += changesInINo

        devToDevNetworks(fileOrMethod, d2d, d2i)

    # -------------------
    # SAVING INFO IN NETS

    def saveAttribsInNets(self, initialDate, finalDate):
        d2f: Network = self.getNet(FILE_TYPE, D2I, ALL_TIME)
        d2f.setNetAttrib(NET_INITIAL_DATE, initialDate)
        d2f.setNetAttrib(NET_FINAL_DATE, finalDate)

    # ------------
    # SAVING NETS

    def saveNets(self, fileOrMethod, timeLimitedInfo):
        #self.removeNodesWithoutChanges(fileOrMethod, timeLimitedInfo)

        #self.removeEliminatedFiles(fileOrMethod, timeLimitedInfo)

        self.createD2DNets(fileOrMethod, timeLimitedInfo)
        
        d2i = self.getNet(fileOrMethod, D2I, timeLimitedInfo)
        i2i = self.getNet(fileOrMethod, I2I, timeLimitedInfo)
        if fileOrMethod == FILE_TYPE:
            items = d2i.getFileNodes()
        else:
            items = d2i.getMethodNodes()
        for i in items:
            i2i.addNode(i)

        d2i.saveNet()
        i2i.saveNet()

    # --------------
    # TIME LINE

    def increaseCommitId(self):
        self.commitId += 1

    def updateTimeline(self, fileOrMethod, author, date, itemsInCommit):
        d2i: Network = self.getNet(fileOrMethod, D2I, ALL_TIME)

        addedItems, removedItems = 0, 0
        for item in itemsInCommit:
            if d2i.degreeOfNode(item) == 0 or item not in d2i.getNodes():
                addedItems += 1
            elif isItemDeleted(item, fileOrMethod):
                removedItems += 1
        
        self.timeline.setCommitInfo(fileOrMethod=fileOrMethod,
            commitId=self.commitId,
            author=author,
            date=date,
            changes=len(itemsInCommit) - addedItems - removedItems,
            adds=addedItems,
            removes=removedItems)
        
    def saveTimelineInfo(self):
        self.timeline.save(
            nrFiles=len(self.getNet(FILE_TYPE, D2I, ALL_TIME).getFileNodes()),
            nrDevs=len(self.getNet(FILE_TYPE, D2I, ALL_TIME).getDeveloperNodes()),
            nrMethods=len(self.getNet(METHOD_TYPE, D2I, ALL_TIME).getMethodNodes())
        )