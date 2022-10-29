import sys

from constants import *
import variables as var
from utils.pathClass import netAnalysisPathsManager

from networksAnalysis.coreAnalysis import comparisonAcrossCodebases, analyzeComparison

def getDataAndDrawGraph(attrib1, attrib2=None):
    if attrib2 == None: # cumulative distribution or cumulative value
        comparisonAcrossCodebases(attrib1)
    else: # comparison
        compInfo = COMPARISONS_INFO[attrib1][attrib2]
        if compInfo[PL_FIT] == True:
            for boolean in [True, False]:
                analyzeComparison(attrib1, attrib2, {LOGLOG: compInfo[LOGLOG], PL_FIT: boolean})
        else:
            analyzeComparison(attrib1, attrib2, compInfo)

if __name__ == "__main__":
    var.initVariablesDict()
    paths = var.variablesDict[PATHS] = netAnalysisPathsManager(sys.argv[1])

    # cumulative distributions
    for m in METRICS:
        getDataAndDrawGraph(m)

    # comparisons
    for a1 in COMPARISONS_INFO.keys():
        for a2 in COMPARISONS_INFO[a1].keys():
            getDataAndDrawGraph(a1, a2)