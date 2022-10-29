from math import floor

from constants import *
import variables as var

from utils.auxiliaryFunctions import getStructInFile
from utils.timelineClass import Timeline

class Component: 
    def __init__(self, dist, total, mean=None, len=None, notZeros=None, order=None) -> None:
        self.dist = dist
        self.mean = mean
        self.total = total
        self.notZeros = notZeros
        self.cLen = len
        self.order = order
        self.results = None

    def getDist(self):
        return self.dist
    
    def getMean(self):
        return self.mean
    
    def getTotal(self):
        return self.total

    def getNotZeros(self):
        return self.notZeros

    def getCLen(self):
        return self.cLen

    def getResults(self):
        return self.results

    def getResultForCommit(self, x):
        return self.results[x]

    def setResults(self, results):
        self.results = results
    
    def setResultForCommit(self, i, res):
        self.results[i] = res

    def setTotal(self, total):
        self.total = total

    def setCLen(self, len):
        self.cLen = len

    def switchCommitsResults(self, commit1, commit2):
        self.results[commit1], self.results[commit2] = self.results[commit2], self.results[commit1]

def getComponentsCharacteristics(cbAttr):
    
    # ---------------------------------------
    # -- Information on how to distribute: --
    # -- > the commits per developer   ------
    # -- > added files per all commits ------
    # -- > deleted files per all commits ----
    # -- > changed files per all commits ----
    # ---------------------------------------
    distributions = var.variablesDict[DISTS]
    return {
        COMMITS: Component(
            dist  = distributions[NOC_PER_DEV],
            mean  = cbAttr[NOC] / cbAttr[NOD],
            total = cbAttr[NOC],
            len   = cbAttr[NOD]),

        FILES_ADDED: Component(
            dist     = distributions[F_ADD_PER_C],
            mean     = cbAttr[F_ADD] / cbAttr[NOC],
            total    = cbAttr[F_ADD],
            len      = cbAttr[NOC],
            notZeros = floor(cbAttr[NOC] * cbAttr[P_C_ADD])),

        FILES_DELETED: Component(
            dist     = distributions[F_DEL_PER_C],
            mean     = cbAttr[F_DEL] / cbAttr[NOC],
            total    = cbAttr[F_DEL],
            len      = cbAttr[NOC],
            notZeros = floor(cbAttr[NOC] * cbAttr[P_C_DEL])),

        FILES_CHANGED: Component(
            dist     = distributions[F_CH_PER_C],
            mean     = cbAttr[F_CH] / cbAttr[NOC],
            total    = cbAttr[F_CH],
            len      = cbAttr[NOC],
            notZeros = floor(cbAttr[NOC] * cbAttr[P_C_CH])),

        DATES: Component(
            dist  = distributions[D_PER_C],
            total = cbAttr[CB_DUR]
        )
    }