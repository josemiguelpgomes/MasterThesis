import powerlaw
from scipy.optimize import curve_fit
from numpy import mean
from math import isnan

from constants import *

class distStatisticalAnalysis:
    def __init__(self, constructionType, nodesNumber=None, dataToCompare=None) -> None:
        self.R = None
        if constructionType == FROM_DATA_TO_COMPARE:
            self.analysisOfData(dataToCompare)
        elif constructionType == FROM_OTHER_ATTRIBUTES:
            self.nodesNumber = nodesNumber

    def analysisOfData(self, data) -> None:
        if len(set(data)) > 2: # more than 2 unique values
            
            self.min = round(min(data), 3)
            self.max = round(max(data), 3)
            self.mean = round(mean(data), 3)

            dataToVerifyPowerlaw = list(filter(lambda x: x != 0, data))
            if len(dataToVerifyPowerlaw) == 0:
                print("Only zeros for DSA.")
            results = powerlaw.Fit(dataToVerifyPowerlaw, verbose=False)
            R, p = results.distribution_compare('power_law', 'exponential')
            if not isnan(R):
                R = round(R)
            if not isnan(p):
                p = round(p, 2)

            self.R = R
            self.p = p
            
            self.plgamma = round(results.power_law.alpha, 2)
            self.plxmin = results.power_law.xmin
            if not isnan(self.plxmin):
                self.plxmin = round(self.plxmin)

    def getMin(self):
        return self.min
    
    def getMax(self):
        return self.max

    def getMean(self):
        return self.mean

    def getR(self):
        return self.R
    
    def getP(self):
        return self.p

    def getPLGamma(self):
        return self.plgamma

    def getXMin(self):
        return self.plxmin
    
    def getNodesNumber(self):
        return self.nodesNumber
    
    def didAnalyse(self):
        return self.R != None and not isnan(self.R)
    
def powerLawFitFunc(x, a, k):
    return a * (x ** k) 

def powerlawFitBetweenTwoDataSets(xdata, ydata):
    try:
        popt, pcov = curve_fit(powerLawFitFunc, xdata, ydata)
    except RuntimeError:
        return [-1], [-1], [-1]

    fitGraphPowerLaw = [list(xdata), powerLawFitFunc(xdata, *popt).tolist()]

    return list(popt), list(pcov), list(fitGraphPowerLaw)