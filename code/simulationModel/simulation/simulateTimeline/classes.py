from operator import le
from random import random
from math import floor
from numpy import random as nprandom

from constants import *
import variables as var

from utils.auxiliaryFunctions import normalize, listsSetDifference
from utils.timelineClass import Timeline
from utils.networksClasses import Network

class Context:
    def __init__(self, timelineClass, chDist):
        self.getChDistInfo(chDist)
        self.initSimActors(timelineClass)

    def getChDistInfo(self, chDist):
        self.A = chDist[A]
        self.alpha = chDist[ALPHA]

    def initSimActors(self, tl: Timeline):

        self.tl = tl

        self.dates = tl.getAllDates()

        # actors
        self.devs = []
        self.files, self.notRemovedFiles = [], []
        
        # ---------------------
        # developers creation

        allDevsCommitsInfo = {}
        for commitId in tl.getCommitIds():
            author = tl.getAuthorOfCommitId(commitId)
            commitAttr = {
                "numberOfFilesChanged": tl.getChangesOfCommitId(commitId),
                "date": tl.getDateOfCommitId(commitId),\
                "numberOfFilesAdded": tl.getAddsOfCommitId(commitId), 
                "numberOfFilesRemoved": tl.getDeletesOfCommitId(commitId)
            }
            if author in allDevsCommitsInfo.keys():
                allDevsCommitsInfo[author] += [commitAttr]
            else:
                allDevsCommitsInfo[author] = [commitAttr]
        
        for dev, devCommitsInfo in allDevsCommitsInfo.items():
            dj = Developer(dev, len(devCommitsInfo), devCommitsInfo, self)
            self.devs += [dj]
        
        self.totalActors = len(self.devs)

    # -------------
    # ACTOR GETTERS

    def getDeveloperNumbered(self, name):
        for d in self.devs:
            if d.number == name:
                return d
        return -1

    def getFiles(self):
        return self.files

    def getNotRemovedFiles(self):
        return self.notRemovedFiles

    # -------------
    # ACTORS UPDATES

    def addNewFile(self):
        self.totalActors += 1
        fj = File(self.totalActors, self)
        self.files += [fj]
        self.notRemovedFiles += [fj]
        return fj

    def removeFromNonRemovedFiles(self, file):
        self.notRemovedFiles.remove(file)

class Item():
    def __init__(self, number, type):
        self.number = number # developer or file are identified by an incremental id.
        self.type = type

class Developer(Item):
    def __init__(self, number, commitsToDo, commitInfo, context):
        super().__init__(number, DEV_TYPE)
        self.numberOfCommitsToDo = commitsToDo
        self.commitInfo = commitInfo

        self.context: Context = context

    def commitToFiles(self, net: Network, A, alpha):
        filesInCommit: list[File] = []

        commitAttrs = self.getNextCommitAttrs()

        commitDate = commitAttrs["date"]
        fnrInCommit = commitAttrs["numberOfFilesChanged"]
        numberOfAddedFiles = int(commitAttrs["numberOfFilesAdded"])
        numberOfRemovedFiles = commitAttrs["numberOfFilesRemoved"]

        for j in range(numberOfRemovedFiles):
            possibleFilesToDelete = list(filter(lambda x: x.removed == False, self.context.getFiles()))
            fToDelete: File = nprandom.choice(possibleFilesToDelete)
            filesInCommit += [fToDelete]

            fToDelete.remove()

        for j in range(numberOfAddedFiles):
            fToCommit: File = self.addNewFile()
            filesInCommit += [fToCommit]

        numberOfChangesInFilesThatExist = fnrInCommit
        
        for j in range(numberOfChangesInFilesThatExist):
            if len(self.context.getNotRemovedFiles()) > 20:
                fToCommit: File = self.pickFileAccordingPrefAttach(self.context.getNotRemovedFiles(), A, alpha)
                while fToCommit in filesInCommit:
                    fToCommit: File = self.pickFileAccordingPrefAttach(self.context.getNotRemovedFiles(), A, alpha)
            else:
                possibleFilesToCommit = listsSetDifference(self.context.getNotRemovedFiles(), filesInCommit)
                fToCommit: File = self.pickFileAccordingPrefAttach(possibleFilesToCommit, A, alpha)
            
            filesInCommit += [fToCommit]

        if len(filesInCommit) < 100:
            for j in filesInCommit:
                net.addEdgeOrWeightToNetwork(self, j, types=[DEV_TYPE, FILE_TYPE], date=commitDate)

        for f in filesInCommit:
            f.increaseRealCommits()
            
        return filesInCommit

    def getNextCommitAttrs(self):
        return self.commitInfo.pop(0)

    def addNewFile(self):
        return self.context.addNewFile()
    
    def pickFileAccordingPrefAttach(self, fileStruct, A, alpha):
        if alpha == 0:
            return fileStruct[floor(random() * len(fileStruct))]
        
        filePopularity = normalize(list(map(lambda x: A + (x.getRealCommits() ** alpha), fileStruct)))
        return nprandom.choice(fileStruct, p=filePopularity)

class File(Item):
    def __init__(self, number, context):
        super().__init__(number, FILE_TYPE)
        self.removed = False
        self.realCommits = 0 # number of commits where the file is, and there is less than 100 files
        self.context: Context = context
    
    def remove(self):
        self.removed = True
        self.context.removeFromNonRemovedFiles(self)

    def increaseRealCommits(self):
        self.realCommits += 1

    def getRealCommits(self):
        return self.realCommits