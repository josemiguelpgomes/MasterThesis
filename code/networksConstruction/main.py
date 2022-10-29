import sys

from constants import *
import variables as var
from utils.pathClass import netConstructionPathsManager

from networksConstruction.commit import Commit
from networksConstruction.networksManager import NetworksManager
from networksConstruction.itemInteraction import interactionWithItem
from networksConstruction.auxNetConstruction import lineRelatedWithMethod, prefixMethodNamesWithFileName, getCommitAndFileInfo, developerShouldBeIgnored

def createNetworks():
    var.initVariablesDict()

    codebase = sys.argv[1]
    paths = var.variablesDict[PATHS] = netConstructionPathsManager(codebase)

    netManager: NetworksManager = NetworksManager()
    var.variablesDict[NET_MANAGER] = netManager

    initialDate = None
    commit: Commit = None
    codeRawDataFile = open(paths.getPathCodeRawData(), "r", encoding="utf-8")
    for line in codeRawDataFile:
        if lineRelatedWithMethod(line):
            if developerShouldBeIgnored(authorName, codebase):
                continue

            file = commit.getLastAnalyzedFile()
            if file == NON_EXISTENT_ITEM: # If the correspondent file is deleted then the deletion of the methods took place when the file was deleted
                continue

            methodBefore, methodAfter = prefixMethodNamesWithFileName(line, file)
            interactionWithItem(METHOD_TYPE, methodBefore, methodAfter, commit)

        else: # File analysis
            commitHash, commitAuthor, oldFilePath, newFilePath, date, nloc, cyclicComplexity = getCommitAndFileInfo(line)
            
            if initialDate == None:
                initialDate = date
                netManager.decideIfCreateTLNets(initialDate)

            if commit != None and commitHash != commit.hash: # new commit
                wasAnalyzed = commit.analyze()
                netManager.verifyIfNewTimePeriod(date)
                
                commit = None
                if wasAnalyzed:
                    netManager.increaseCommitId()

            authorName = commitAuthor.split(";")[0]
            if developerShouldBeIgnored(authorName, codebase):
                continue

            if commit == None:
                commit: Commit = Commit(commitHash, commitAuthor, date)

            interactionWithItem(FILE_TYPE, oldFilePath, newFilePath, commit, nloc, cyclicComplexity)

    codeRawDataFile.close()

    commit.analyze() # Analyze last commit

    netManager.saveAttribsInNets(initialDate, date)  
    netManager.saveTimelineInfo()

    netManager.saveNets(FILE_TYPE, ALL_TIME)
    netManager.saveNets(METHOD_TYPE, ALL_TIME)

createNetworks()
