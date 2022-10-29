from constants import *
import variables as var
from utils.pathClass import simulationPathsManager

from utils.auxiliaryFunctions import cumulativeProbabilityDistribution
from utils.graphsCreation import Chart, GraphInfo

from networksAnalysis.coreAnalysis import comparisonAcrossCodebases

from simulationModel.analysis.hypothesisComparison import hypothesisResults

from constants import EMP, THEO

concreteGraphLabels = {
    D2D: "FD2D WD, $wd$\n(number of times that developer $d$ have\ncollaborated with other developers, in files)",
    D2F: "File D2F WD, $wd$ \n(number of changes in a file)",
    F2F: "F2F WD, $wd$\n(sum of number of files in commits where\na certain file is present)"
}

def createGraphHypResForAnalysisType(results, netType, hypothesis):
    paths: simulationPathsManager = var.variablesDict[PATHS]
    netTypeToComparisonType = {D2F: D2F_F_WD, D2D: D2D_WD, F2F: F2F_F_WD}

    hypRes: hypothesisResults = var.variablesDict[HYP_RESULTS]

    resultsDict = {
        THEO: list(cumulativeProbabilityDistribution(results)), \
    }
    if paths.simulationRelatedWithRealCodeBase():
        resultsDict[EMP], empiricalGamma, allData = comparisonAcrossCodebases(netTypeToComparisonType[netType], save = False)
        hypRes.setCumDistOfHypForAnalysisType(EMP, netType, resultsDict[EMP])
        hypRes.setGammaOfHypForAnalysisType(EMP, netType, empiricalGamma)
        hypRes.setAllDataOfHypForNet(EMP, netType, allData)

        graphData = [resultsDict[THEO], resultsDict[EMP]]
        legendLabels = ["Theoretical data\n(Null model)", "Empirical data"]
    else:
        graphData = [resultsDict[THEO]]
        legendLabels = []

    hypRes.setCumDistOfHypForAnalysisType(hypothesis, netType, resultsDict[THEO])
    hypRes.setAllDataOfHypForNet(hypothesis, netType, results)

    graphInfo = GraphInfo()
    graphInfo.setData(graphData)
    graphInfo.setXLabel(concreteGraphLabels[netType])
    graphInfo.setYLabel('Relative frequency')
    graphInfo.setPath('{}/{}.png'.format(paths.getHypothesisGraphsDir(), netType))
    graphInfo.setLegends(legendLabels)
    graphInfo.setLoglog(True)
    Chart(graphInfo).draw()