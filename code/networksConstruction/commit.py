from constants import *
import variables as var
from networksConstruction.networksManager import NetworksManager

class Commit():
    def __init__(self, commitHash, commitAuthor, date):
        self.hash = commitHash
        self.date = date
        self.author = commitAuthor
        self.filesInCommit = []
        self.methodsInCommit = []
        
    def getLastAnalyzedFile(self):
        if len(self.filesInCommit) == 0: # happens in the case of removing a file that wasn't added as it was in a commit with >100 files
            return NON_EXISTENT_ITEM
        else:
            return self.filesInCommit[-1]
    
    def analyze(self):
        nm: NetworksManager = var.variablesDict[NET_MANAGER]
        if len(self.filesInCommit) > 0 and len(self.filesInCommit) < 100:
            self.author = nm.getOrCreateDeveloper(self.author)

            self.analyzeAux(FILE_TYPE, self.filesInCommit)
            if len(self.methodsInCommit) > 0 and len(self.methodsInCommit) < 100:
                self.analyzeAux(METHOD_TYPE, self.methodsInCommit)
            
            return True
        return False
    
    def analyzeAux(self, fileOrMethod, itemsInCommit):
        nm: NetworksManager = var.variablesDict[NET_MANAGER]
        nm.saveInfoInNets(fileOrMethod, self.author, self.date, itemsInCommit)
        nm.updateTimeline(fileOrMethod, self.author, self.date, itemsInCommit)
        nm.addItems(fileOrMethod, self.author, self.date, itemsInCommit)

    def addFileToCommit(self, file):
        self.filesInCommit += [file]

    def addMethodToCommit(self, method):
        self.methodsInCommit += [method]
        