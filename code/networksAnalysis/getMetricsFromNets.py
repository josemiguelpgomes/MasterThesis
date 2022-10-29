from operator import itemgetter

from constants import *
import variables as var

from utils.graphInfoClass import GraphInfo
from utils.distStatisticalAnalysis import distStatisticalAnalysis
from utils.networksClasses import Network
from utils.pathClass import netAnalysisPathsManager
from utils.developerClass import DeveloperEmpirical

from networksAnalysis.nets import readNet

from utils.auxiliaryFunctions import createDirRec, getStructInFile, saveStructInFile

FILES = "files"
METHODS = "methods"
DEVS = "developers"
ALL = "all"

# METRIC TYPES
D = "d"
WD = "wd"
C_WD = "wdC"
D_COM = "dcom"
D_FREQ = "dcomfreq"
CB_FREQ = "cbcomfreq"

# EXTRA ANALYSIS
TOP_6 = "top6"
TOP_6_NAME = "top6_name"

def getDataGivenMetric(comparison, date, compBetweenCBs: bool, compBetweenMetrics: bool):
    graphInfo: GraphInfo = var.variablesDict[GRAPH_INFO]

    # Net reading
    type = comparison.split("_")[0]
    if type == D2D:
        net = readNet(FILE_TYPE, D2D, date=date)
    elif type == F2F:
        net = readNet(FILE_TYPE, I2I, date=date)
    elif type == D2DM:
        net = readNet(METHOD_TYPE, D2D, date=date)
    elif type == D2M:
        net = readNet(METHOD_TYPE, D2I, date=date)
    elif type == M2M:
        net = readNet(METHOD_TYPE, I2I, date=date)
    else: 
        net = readNet(FILE_TYPE, D2I, date=date)

    infoDict = \
    {                 # nodes          | # type                 | # infoToTxt            |  # description
        D2F_F_WD    : {"nodes": FILES  , "metricType": WD       , "infoToTxt": TOP_6     }, # File changes
        D2M_M_WD    : {"nodes": METHODS, "metricType": WD       , "infoToTxt": TOP_6     }, # Method changes
 
        D2F_D_WD    : {"nodes": DEVS   , "metricType": WD       , "infoToTxt": TOP_6_NAME}, # Developer changes in files
        D2M_D_WD    : {"nodes": DEVS   , "metricType": WD       , "infoToTxt": TOP_6_NAME}, # Developer changes in methods

        F2F_F_WD    : {"nodes": ALL    , "metricType": WD       , "infoToTxt": TOP_6     }, # Files coupling
        M2M_WD      : {"nodes": ALL    , "metricType": WD       , "infoToTxt": TOP_6     }, # Methods coupling

        D2D_D_D     : {"nodes": ALL    , "metricType": D        , "infoToTxt": TOP_6_NAME}, # Developers collaboration degree in files
        D2D_WD      : {"nodes": ALL    , "metricType": C_WD     , "infoToTxt": TOP_6_NAME}, # Developers collaboration in files
        D2DM_WD     : {"nodes": ALL    , "metricType": C_WD     , "infoToTxt": TOP_6_NAME}, # Developers collaboration in methods
        
        D2F_D_COMMS : {"nodes": DEVS   , "metricType": D_COM    , "infoToTxt": TOP_6_NAME}, # Developer commits
        ITEM_NLOC   : {"nodes": FILES  , "metricType": ITEM_NLOC, "infoToTxt": TOP_6     }, 
        ITEM_CC     : {"nodes": FILES  , "metricType": ITEM_CC  , "infoToTxt": TOP_6     }
    }

    compInfo = infoDict[comparison]
    
    nodesType        , metricType           , infoToTxt = \
    compInfo["nodes"], compInfo["metricType"], compInfo["infoToTxt"]

    # Gather specific nodes
    if nodesType == FILES:
        nodes = net.getFileNodes()
    elif nodesType == METHODS:
        nodes = net.getMethodNodes()
    elif nodesType == DEVS:
        nodes = net.getDeveloperNodes()
    else:
        nodes = net.getNodes()
    
    if compBetweenMetrics:
        dataToCompare, _ = getDataToCompareGivenMetric(net, metricType, nodes, toComparison=True)
    else:
        # Gather according to certain metric
        dataToCompare, wholeData = getDataToCompareGivenMetric(net, metricType, nodes)
        # Get extra info
        if infoToTxt != None:
            if infoToTxt == TOP_6:
                topElems = list(sorted(wholeData.items(), key=itemgetter(1), reverse=True)[:6])
            elif infoToTxt == TOP_6_NAME:
                topElems = list(map(lambda x: (x[0].getName(), x[1]), sorted(wholeData.items(), key=itemgetter(1), reverse=True)[:6]))

            # ---
            if date == ALL_TIME:
                paths: netAnalysisPathsManager = var.variablesDict[PATHS]
                pathToKeepComparisonInfo = '{}/codebasesComparison'.format(RESULTSDIR)
                pathToKeepComparisonPickles = '{}/pickles'.format(pathToKeepComparisonInfo)
                createDirRec(pathToKeepComparisonPickles)

                pathWithSpecificPickle = '{}/{}.pickle'.format(pathToKeepComparisonPickles, comparison)
                infoOnAnalysisType = getStructInFile(pathWithSpecificPickle)

                if paths.getCodeBaseName() not in infoOnAnalysisType:
                    infoOnAnalysisType[paths.getCodeBaseName()] = {}
                infoOnAnalysisType[paths.getCodeBaseName()]["top6"] = topElems

                saveStructInFile(infoOnAnalysisType, pathWithSpecificPickle)

        if compBetweenCBs:
            paths: netAnalysisPathsManager = var.variablesDict[PATHS]
            netKey = paths.getCodeBaseName()
        else:
            netKey = date
        graphInfo.setDSAofNet(netKey, distStatisticalAnalysis(FROM_OTHER_ATTRIBUTES, len(nodes)))

    return dataToCompare


def getDataToCompareGivenMetric(net: Network, compMetricType, nodes, toComparison=False):
    wholeData = None
    if compMetricType == WD:
        wholeData = dict(net.getDegrees(nbunch=nodes, weight=ST_WEIGHT))
    elif compMetricType == D:
        wholeData = dict(net.getDegrees())
    elif compMetricType == C_WD:
        wholeData = dict(net.getDegrees(weight=D2D_WEIGHT))
    elif compMetricType == D_COM:
        wholeData = {k: len(v) for k, v in dict(net.getNodeAttributes(ITEM_COMMITS_DATES)).items() if k in nodes}
    elif compMetricType == ITEM_NLOC or compMetricType == ITEM_CC:
        wholeData = dict(net.getNodeAttributes(compMetricType))
        wholeData = {k: int(v) for k,v in wholeData.items()}
    elif compMetricType == D_FREQ:
        timeBetweenCommitsPerDev = []
        for v in net.getNodeAttributes(ITEM_COMMITS_DATES).values(): # dev, [date1, date2, date3]
            v = sorted(v)
            for i in range(len(v) - 1):
                timeBetweenCommitsPerDev += [(v[i + 1] - v[i]).total_seconds()] 
        
        dataToCompare = timeBetweenCommitsPerDev
    elif compMetricType == CB_FREQ:
        allDates = []
        timeBetweenCommitsCodebase = []
        for v in net.getNodeAttributes(ITEM_COMMITS_DATES).values():
            for d in v: 
                allDates += [d]

        allDates = sorted(allDates)
        for i in range(len(allDates) - 1):
            timeBetweenCommitsCodebase += [(allDates[i + 1] - allDates[i]).total_seconds()]
 
        dataToCompare = timeBetweenCommitsCodebase
    
    if compMetricType in [WD, D, C_WD, D_COM, ITEM_NLOC, ITEM_CC]:
        if toComparison:
            if type(list(nodes)[0]) == DeveloperEmpirical:
                dataToCompare = {k.name: v for k, v in wholeData.items()}
            else:
                dataToCompare = {k: v for k, v in wholeData.items()}
        else:
            dataToCompare = list(wholeData.values())

    if wholeData != None:
        return dataToCompare, wholeData
    else:
        return dataToCompare, -1