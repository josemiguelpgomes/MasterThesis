import variables as var
from utils.pathClass import netConstructionPathsManager
from constants import *

from utils.auxiliaryFunctions import saveStructInFile

class Timeline:
    def __init__(self) -> None:
        self.info = {}
        self.timeline = {FILE_TYPE: {}, METHOD_TYPE: {}}

    def setGlobalInfo(self, filesNumber, devsNumber, methodsNumber):
        self.info["filesNumber"] = filesNumber
        self.info["devsNumber"] = devsNumber
        self.info["methodsNumber"] = methodsNumber
    
    def setDevsNumber(self, devsNumber):
        self.info["devsNumber"] = devsNumber

    def setCommitInfo(self, fileOrMethod, commitId, author, date, changes, adds, removes):
        self.timeline[fileOrMethod][commitId] = {
                "author": author, "date": date, \
                "numberOfFilesChanged": changes, 
                "numberOfFilesAdded": adds, "numberOfFilesRemoved": removes
            }
        
    def setDistsForGenTimeline(self, params): # if is a theoretical timeline
        self.timeline["distributions"] = params

    def getCommitIds(self):
        return list(self.timeline[FILE_TYPE].keys())
    
    def getDateOfCommitId(self, commitId):
        return self.timeline[FILE_TYPE][commitId]["date"]

    def getAddsOfCommitId(self, commitId):
        return self.timeline[FILE_TYPE][commitId]["numberOfFilesAdded"]
    
    def getDeletesOfCommitId(self, commitId):
        return self.timeline[FILE_TYPE][commitId]["numberOfFilesRemoved"]
    
    def getChangesOfCommitId(self, commitId):
        return self.timeline[FILE_TYPE][commitId]["numberOfFilesChanged"]
    
    def getAuthorOfCommitId(self, commitId):
        return self.timeline[FILE_TYPE][commitId]["author"]
    
    def getDevsNumber(self):
        return self.info["devsNumber"]

    def getAllDates(self):
        dates = []
        for commitId in self.getCommitIds():
            dates += [self.getDateOfCommitId(commitId)]
        return dates

    def save(self, nrFiles, nrDevs, nrMethods):
        paths: netConstructionPathsManager = var.variablesDict[PATHS]
        self.setGlobalInfo(nrFiles, nrDevs, nrMethods)
        saveStructInFile(self, paths.getEmpiricalTL())

    def getCAForSimulation(self):
        commitsPerDevEmpirical = {}
        filesAddedPerTimestep, filesChangedPerTimestep, filesDeletedPerTimestep, datesOfCommits = [], [], [], []

        commitsWithFilesAdded, commitsWithFilesChanged, commitsWithFilesDeleted = 0, 0, 0

        for commitId in self.getCommitIds():
            author = self.getAuthorOfCommitId(commitId)
            filesChanged = self.getChangesOfCommitId(commitId)
            filesAdded = self.getAddsOfCommitId(commitId)
            filesDeleted = self.getDeletesOfCommitId(commitId)
            date = self.getDateOfCommitId(commitId)

            if author in commitsPerDevEmpirical:
                commitsPerDevEmpirical[author] += 1
            else:
                commitsPerDevEmpirical[author] = 1

            if filesAdded > 0:
                commitsWithFilesAdded += 1

            if filesChanged > 0:
                commitsWithFilesChanged += 1

            if filesDeleted > 0:
                commitsWithFilesDeleted += 1

            filesAddedPerTimestep += [filesAdded]
            filesChangedPerTimestep += [filesChanged]
            filesDeletedPerTimestep += [filesDeleted]
            datesOfCommits += [date]

        pCommitsWithFilesAdded = commitsWithFilesAdded / len(datesOfCommits)
        pCommitsWithFilesChanged = commitsWithFilesChanged / len(datesOfCommits)
        pCommitsWithFilesDeleted = commitsWithFilesDeleted / len(datesOfCommits)

        numberOfCommits = len(datesOfCommits)

        return {
            NOC: numberOfCommits, COMMITS_PER_DEV: commitsPerDevEmpirical, \
            FILES_ADDED_UNTIL_T: filesAddedPerTimestep,  P_C_ADD: pCommitsWithFilesAdded,
            FILES_DELETED_UNTIL_T: filesDeletedPerTimestep,  P_C_DEL: pCommitsWithFilesDeleted, 
            FILES_CHANGED_UNTIL_T: filesChangedPerTimestep, P_C_CH: pCommitsWithFilesChanged,
            DATE_DIFF_PER_T: datesOfCommits, 
        }, self
