import statistics
import numpy as np
from dateutil.relativedelta import relativedelta

from constants import *
import variables as var
from utils.pathClass import netAnalysisPathsManager

from utils.networksClasses import Network
from utils.auxiliaryFunctions import getGraphData
from utils.developerClass import DeveloperEmpirical
from utils.distStatisticalAnalysis import distStatisticalAnalysis, powerlawFitBetweenTwoDataSets
from utils.graphsCreation import Chart, getGraphActors
from utils.graphInfoClass import GraphInfo

from networksAnalysis.nets import readNet
from networksAnalysis.getMetricsDist import cumDistGivenParams
from networksAnalysis.getMetricsFromNets import getDataGivenMetric

def getDates():
    d2f: Network = readNet(FILE_TYPE, D2I)
    return d2f.getNetAttrib(NET_INITIAL_DATE), d2f.getNetAttrib(NET_FINAL_DATE)

def comparisonAcrossCodebases(comparisonType, save=True):
    paths: netAnalysisPathsManager = var.variablesDict[PATHS]
    if not save:
        graphInfo = var.variablesDict[GRAPH_INFO] = GraphInfo()
        dist, allData = cumDistGivenParams(comparisonType, save=save, compBetweenCBs=True)
        return dist, graphInfo.getGammaOfNet(paths.getCodeBaseName()), allData
    
    graphInfo: GraphInfo = getGraphData('{}/{}/{}.png'.format(DIR_TO_COMPARE_CODEBASES, INFO_ABOUT_METRIC[comparisonType]["type"], comparisonType))
    if graphInfo == {}:
        graphInfo = GraphInfo()
    var.variablesDict[GRAPH_INFO] = graphInfo

    if paths.getCodeBaseName() not in graphInfo.getLegendLabels():
        existsCumDist = cumDistGivenParams(comparisonType)
        if existsCumDist:
            graphInfo.addLegend('{}'.format(paths.getCodeBaseName()))

        getGraphActors(COMPARISON_ACROSS_CODEBASES, comparisonType)
        Chart(graphInfo).draw()

    cbDSAoverTime(comparisonType)

def cbDSAoverTime(comparisonType):
    graphInfo = var.variablesDict[GRAPH_INFO] = GraphInfo()
    initialDate, finalDate = getDates()
    date = initialDate
    timeDifferenceBetweenIntervals = relativedelta(days=var.DAYS_BETWEEN_NETS)
    while (date < finalDate - relativedelta(days=var.HOW_MANY_DAYS_IN_A_NET)):
        cumDistGivenParams(comparisonType, date=date)
        date += timeDifferenceBetweenIntervals
    
    infoPerDate = graphInfo.getDsaPerNet()
    
    if len(infoPerDate) > 1:
        Rset, pSet = [], []
        nodesNumber = []
        nrPGreaterThan0_05 = 0
        nrRGreaterThan0, nrRLessThan0 = 0, 0
        totalIntervals, intervalsNotAnalyzed = 0, 0
        
        analysedDates = []
        valuesClass = []
        for netStartingDate in infoPerDate.keys():
            dsa: distStatisticalAnalysis = infoPerDate[netStartingDate] # dsa of net starting in netStartingDate

            if dsa.didAnalyse():
                analysedDates += [netStartingDate]
                Rset        += [dsa.getR()]
                pSet        += [dsa.getP()]
                nodesNumber += [dsa.getNodesNumber()]
                
                beforeLen = len(valuesClass)
                if dsa.getP() > 0.05:
                    nrPGreaterThan0_05 += 1
                    valuesClass += ['$p > 0.05$']
                elif dsa.getR() >= 0:
                    nrRGreaterThan0 += 1
                    valuesClass += ['$p \leq 0.05$\n$R \geq 0$']
                elif dsa.getR() < 0:
                    nrRLessThan0 += 1
                    valuesClass += ['$p \leq 0.05$;\n$R < 0$']
                assert(len(valuesClass) == beforeLen + 1)
            else:
                intervalsNotAnalyzed += 1
            totalIntervals += 1

        graphInfo: GraphInfo = GraphInfo()
        var.variablesDict[GRAPH_INFO] = graphInfo
        graphInfo.setData([[nodesNumber, valuesClass]])
        getGraphActors(DSA_OVER_TIME_CORRELATION, [comparisonType, 'nodesNumber'])

        graphInfo.addLegend("Real data")
        graphInfo.setInfoToTxt(
            "Total intervals: {}\nPercentage of intervals with: \n  - p > 0.05: {}\n  - p $\leq$ 0.05; R $\geq$ 0: {}\n  - p $\leq$ 0.05; R < 0: {}"\
                .format(totalIntervals, round(nrPGreaterThan0_05 / totalIntervals, 2), \
                    round(nrRGreaterThan0 / totalIntervals, 2), round(nrRLessThan0 / totalIntervals, 2))
        )
        Chart(graphInfo).draw()

def analyzeComparison(metric1, metric2, compAttribs):
    val1 = getDataGivenMetric(metric1, ALL_TIME, False, True)
    val2 = getDataGivenMetric(metric2, ALL_TIME, False, True)

    xdata, ydata, possibleComparisons, actualComparisons = [], [], 0, 0
    for n in val1.keys():
        if n in val2.keys():
            possibleComparisons += 1
            if val1[n] != 0 and val2[n] != 0:
                xdata += [val1[n]]
                ydata += [val2[n]]
                actualComparisons += 1
    
    if len(xdata) == 0:
        print("No sufficient values to compare for:", metric1, metric2)
        return

    if compAttribs[PL_FIT]:
        popt, pcov, fitGraphPLWithoutZeros = powerlawFitBetweenTwoDataSets(xdata, ydata)
        if popt == [-1]:
            print("Couldn't create a power law fit for", metric1, metric2)
            return

        alpha = np.around(popt[1], 3)
        standardDeviationAlpha = np.around(np.sqrt(np.diag(pcov)), 3)[1]

    graphInfo = GraphInfo()
    var.variablesDict[GRAPH_INFO] = graphInfo
    graphInfo.addData([xdata, ydata])
    graphInfo.setLoglog(compAttribs[LOGLOG])
    graphInfo.setInfoToTxt("Possible comparisons: {}\nActual comparisons:{}".format(possibleComparisons, actualComparisons))
    getGraphActors(COMPARISON_BETWEEN_METRICS, [metric1, metric2])

    if compAttribs[PL_FIT]:
        graphInfo.addData(fitGraphPLWithoutZeros)
        graphInfo.addLegend("Empirical data")
        graphInfo.addLegend("Powerlaw Fit\n($\\gamma$ = {}, $\\sigma$ = {})".format(alpha, standardDeviationAlpha))
        graphInfo.setIgnorePoints(min(ydata))
        graphInfo.setPath('{}_plfit.png'.format(graphInfo.getPath()))
    else:
        graphInfo.setPath('{}.png'.format(graphInfo.getPath()))

    Chart(graphInfo).draw()