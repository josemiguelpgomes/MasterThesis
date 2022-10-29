from constants import *
from utils.distStatisticalAnalysis import distStatisticalAnalysis

class GraphInfo:
    def __init__(self):
        self.info = {DATA: [], LEGEND_LABELS: [], DSA_PER_NET: {}}

    # ----
    # ADDS

    def addData(self, data):
        self.info[DATA] += [data]

    def addLegend(self, legend):
        self.info[LEGEND_LABELS] += [legend]

    def setDSAofNet(self, netKey, dsa): # dsa is distributition statiscal analysis
        self.info[DSA_PER_NET][netKey] = dsa

    def getDSAofNet(self, netKey) -> distStatisticalAnalysis:
        return self.info[DSA_PER_NET][netKey]
    
    def addInfoToTxt(self, info):
        if self.getInfoToTxt() == "":
            self.setInfoToTxt(info)
        else:
            self.info[INFO_TO_TXT] += info

    # ----
    # SETS

    def setData(self, data):
        self.info[DATA] = data

    def setXLabel(self, xlabel):
        self.info[XLABEL] = xlabel

    def setYLabel(self, ylabel):
        self.info[YLABEL] = ylabel

    def setPath(self, path):
        self.info[PATH_TO_FIG] = path

    def setLoglog(self, loglog):
        self.info[LOGLOG] = loglog

    def setIgnorePoints(self, ignorePointsWithYSmallerThan):
        self.info[IGNORE_POINTS_Y_SMALLER_THAN] = ignorePointsWithYSmallerThan

    def setRotateXTickLabels(self, rotateXTick):
        self.info[ROTATE_X_LABELS] = rotateXTick

    def setInfoToTxt(self, infoToTxt):
        self.info[INFO_TO_TXT] = infoToTxt

    def setLegends(self, legends):
        self.info[LEGEND_LABELS] = legends

    # ----
    # GETS

    def getData(self):
        return self.info[DATA]

    def getXLabel(self):
        return self.info[XLABEL] if XLABEL in self.info.keys() else ""
    
    def getYLabel(self):
        return self.info[YLABEL] if YLABEL in self.info.keys() else ""
    
    def getPath(self):
        return self.info[PATH_TO_FIG]

    def getLegendLabels(self):
        return self.info[LEGEND_LABELS] if LEGEND_LABELS in self.info.keys() else None

    def getRotateXTickLabels(self):
        return self.info[ROTATE_X_LABELS] if ROTATE_X_LABELS in self.info.keys() else False
    
    def getLoglog(self):
        return self.info[LOGLOG] if LOGLOG in self.info.keys() else False

    def getIgnorePoints(self):
        return self.info[IGNORE_POINTS_Y_SMALLER_THAN] if IGNORE_POINTS_Y_SMALLER_THAN in self.info.keys() else False 

    def getDsaPerNet(self):
        return self.info[DSA_PER_NET]

    def getGammaOfNet(self, netKey):
        return self.info[DSA_PER_NET][netKey].getPLGamma()

    def getInfoToTxt(self):
        return self.info[INFO_TO_TXT] if INFO_TO_TXT in self.info.keys() else ""

    # ----------------
    # VERIFY EXISTENCE

    def hasLegends(self):
        return LEGEND_LABELS in self.info.keys()

    def hasDifferentNets(self):
        return DSA_PER_NET in self.info.keys()
    
