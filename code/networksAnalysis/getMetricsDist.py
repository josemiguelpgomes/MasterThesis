from constants import *
import variables as var

from utils.auxiliaryFunctions import cumulativeProbabilityDistribution, createDirRec, getStructInFile, saveStructInFile
from utils.graphInfoClass import GraphInfo
from utils.pathClass import netAnalysisPathsManager

from networksAnalysis.getMetricsFromNets import getDataGivenMetric

def cumDistGivenParams(comparisonType, date=ALL_TIME, save=True, compBetweenCBs=False):
    graphInfo: GraphInfo = var.variablesDict[GRAPH_INFO]
    paths: netAnalysisPathsManager = var.variablesDict[PATHS]
    
    if compBetweenCBs:
        netKey = paths.getCodeBaseName()
    else:
        netKey = date

    dataToCompare = getDataGivenMetric(comparisonType, date, compBetweenCBs, False)
    if save:
        graphInfo.addData(cumulativeProbabilityDistribution(dataToCompare))
        dataLenWithZeros = len(dataToCompare)
        dataToCompare = list(filter(lambda x: x != 0, dataToCompare))
        dataLenWithoutZeros = len(dataToCompare)
        
        graphInfo.getDSAofNet(netKey).analysisOfData(dataToCompare)

        if date == ALL_TIME:
            allTimeDSA = graphInfo.getDSAofNet(ALL_TIME)
            codebaseDSA = '{} & {} & {} & {} & {} \\\\ \hline \n'.format(paths.getCodeBaseName(), allTimeDSA.getR(), allTimeDSA.getP(), allTimeDSA.getPLGamma(), allTimeDSA.getXMin())

            pathToKeepComparisonInfo = '{}/codebasesComparison'.format(RESULTSDIR)
            pathToKeepComparisonPickles = '{}/pickles'.format(pathToKeepComparisonInfo)
            createDirRec(pathToKeepComparisonPickles)

            pathWithSpecificPickle = '{}/{}.pickle'.format(pathToKeepComparisonPickles, comparisonType)
            infoOnAnalysisType = getStructInFile(pathWithSpecificPickle)
            if paths.getCodeBaseName() not in infoOnAnalysisType:
                infoOnAnalysisType[paths.getCodeBaseName()] = {}
            infoOnAnalysisType[paths.getCodeBaseName()]["DSA"] = codebaseDSA

            newInfoToTxt = 'Codebase & $R$ & $p$ & $\gamma$ & $xmin$ \\\\ \hline \n'
            for net in infoOnAnalysisType.keys():
                if "DSA" in infoOnAnalysisType[net]:
                    newInfoToTxt += infoOnAnalysisType[net]["DSA"]
            
            newInfoToTxt += '\nCodebase & Files & Changes & Functionality \\\\ \hline \n'
            for net in infoOnAnalysisType.keys():
                for i in range(4):
                    itemInfo = infoOnAnalysisType[net]["top6"][i]
                    sfileName = itemInfo[0].split("/")
                    if len(sfileName) > 1:
                        fileName = "/".join(sfileName[-2:])
                    else:
                        fileName = sfileName[0]
        
                    res = fileName.find("ELIMINATED_")
                    if res != -1:
                        fileName = fileName[res+13:]

                    if "\\" in fileName:
                        fileName = fileName.replace("\\", "$\\backslash$")

                    if "_" in fileName:
                        fileName = fileName.replace("_", "\\_")

                    if i == 3:
                        endLine = "\hline"
                    else:
                        endLine = "\cline{2-4}"

                    if i == 0:
                        newInfoToTxt += '\multirow{4}{*}{' + net + '}' + ' & {} & {} & - \\\\ {} \n'.format(fileName, itemInfo[1], endLine)
                    else: 
                        newInfoToTxt += '& {} & {} & - \\\\ {} \n'.format(fileName, itemInfo[1], endLine)
            
            saveStructInFile(infoOnAnalysisType, pathWithSpecificPickle)
            graphInfo.setInfoToTxt(newInfoToTxt)
        
        #"{}:\n Len of data with zeros: {}\nLen of data without zeros: {}\n".format("TODO", dataLenWithZeros, dataLenWithoutZeros))
        
        return True
    else:
        graphInfo.getDSAofNet(netKey).analysisOfData(dataToCompare)
        return cumulativeProbabilityDistribution(dataToCompare), dataToCompare