from constants import *
import variables as var
from utils.pathClass import simulationPathsManager

from utils.distStatisticalAnalysis import distStatisticalAnalysis
from utils.auxiliaryFunctions import kolmogorovSmirnovCumDists, createDirRec, getStructInFile
from utils.graphsCreation import Chart, GraphInfo

from simulationModel.simulation.simManager import fromHypNameToChRule
from simulationModel.analysis.complexEvalClass import ComplexEval

ITALIC = "\\textit{"
MTR_BEGIN = "\multirow{4}*{"
C_LINE = "\cline{2-6}"
P_END = "}"

CONCRETE_GRAPH_INFO = {
    COLLAB_PER_FILE: {
        XLABEL: "Quantity of collaboration in file, $c$",
        YLABEL: "Cumulative distribution, $P_{c}^{Cum}$",
        LOGLOG: True
    },
    D2F: {
        XLABEL: "File D2F WD, $wd$ \n(number of changes in a file)",
        YLABEL: "Cumulative distribution, $P_{wd}^{Cum}$",
        LOGLOG: True
    },
    D2D: {
        XLABEL: "FD2D WD, $wd$\n(number of times that developer $d$ have\ncollaborated with other developers, in files)",
        YLABEL: "Cumulative distribution, $P_{wd}^{Cum}$",
        LOGLOG: True
    },
    F2F: {
        XLABEL: "F2F WD, $wd$\n(sum of number of files in commits where\na certain file is present)",
        YLABEL: "Cumulative distribution, $P_{wd}^{Cum}$",
        LOGLOG: True
    }
}

MODEL_ID_INFO = {
    3: {
        "newDevR": "RANDOM",
        "knownDevR": "RANDOM"
    },
    4: {
        "newDevR": "RANDOM",
        "knownDevR": "PROP\_TODO"
    },
    5: {
        "newDevR": "RANDOM",
        "knownDevR": "PROP\_DONE"
    },
    6: {
        "newDevR": "PROP\_TODO",
        "knownDevR": "RANDOM"
    },
    7: {
        "newDevR": "PROP\_TODO",
        "knownDevR": "PROP\_TODO"
    },
    8: {
        "newDevR": "PROP\_TODO",
        "knownDevR": "PROP\_DONE"
    }
}

class hypothesisResults:
    def __init__(self, startEmpRes):
        """
        self.hypRes has the following structure:
        {
            hypothesis/empirical: {
                {
                    comparisonType: cumDist
                    comparisonType_gamma: cumDistGamma
                    comparisonType_allData: allDataThatLeadsToCumDist
                }
            }
        }

        Example: 
        {
            "hypothesis_0": {
                {
                    D2F: REPRESENTATION OF D2F CUMULATIVE DISTRIBUTION, IN PARTICULAR D2F FILES WD
                    D2F_GAMMA: GAMMA OF D2F CUMULATIVE DISTRIBUTION
                    D2F_ALLDATA: ALL DATA OF D2F FILES WD
                }
            }
        }
        """
        
        if startEmpRes:
            self.hypRes = {EMP: {}}
        else:
            self.hypRes = {}

    def setCumDistOfHypForAnalysisType(self, hyp, analysis, cumDist):
        if hyp not in self.hypRes.keys():
            self.hypRes[hyp] = {}
        self.hypRes[hyp]['{}_cumDist'.format(analysis)] = cumDist

    def setGammaOfHypForAnalysisType(self, hyp, analysis, gamma):
        if hyp not in self.hypRes.keys():
            self.hypRes[hyp] = {}
        self.hypRes[hyp]['{}_gamma'.format(analysis)] = gamma

    def setAllDataOfHypForNet(self, hyp, analysis, gamma):
        if hyp not in self.hypRes.keys():
            self.hypRes[hyp] = {}
        self.hypRes[hyp]['{}_allData'.format(analysis)] = gamma

    def getCumDistOfHypForNet(self, hyp, analysis):
        return self.hypRes[hyp]['{}_cumDist'.format(analysis)]

    def getCumDistGammaOfHypForCompType(self, hyp, analysis):
        return self.hypRes[hyp]['{}_gamma'.format(analysis)]

    def getAllDataOfHypForAnalysisType(self, hyp, analysis):
        return self.hypRes[hyp]['{}_allData'.format(analysis)]

    def getHypothesis(self):
        hypSet = []
        for k in self.hypRes.keys():
            if not k.endswith("_allData") and not k.endswith("_gamma"):
                hypSet += [k]
        return hypSet

    def comparison(self, modelId):
        paths: simulationPathsManager = var.variablesDict[PATHS]

        compsToAnalyze = [D2F, D2D, F2F, COLLAB_PER_FILE]
        for analysisType in compsToAnalyze:

            resultsSet = []
            legends = []

            for hyp in self.getHypothesis():
                if hyp == EMP and not paths.simulationRelatedWithRealCodeBase():
                    continue
                
                resultsSet += [self.getCumDistOfHypForNet(hyp, analysisType)]

                if hyp == EMP:
                    legends += [EMP]
                else:
                    sParams = hyp.split("_")

                    if sParams[1] == "-":
                        legends += ["k = -"]
                    else:
                        legends += ["k = {}".format(float(sParams[1]))]

            createDirRec(paths.getHypothesisComparisonDir())
            path = '{}/{}.png'.format(paths.getHypothesisComparisonDir(), analysisType)
            if paths.simulationRelatedWithRealCodeBase():
                infoToTxt = self.statisticalAnalysisIntoLatex(analysisType, modelId)
            else:
                infoToTxt = ""

            graphInfo = GraphInfo()
            graphInfo.setData(resultsSet)
            graphInfo.setXLabel(CONCRETE_GRAPH_INFO[analysisType][XLABEL])
            graphInfo.setYLabel(CONCRETE_GRAPH_INFO[analysisType][YLABEL])
            graphInfo.setPath(path)
            graphInfo.setLegends(legends)
            graphInfo.setLoglog(CONCRETE_GRAPH_INFO[analysisType][LOGLOG])
            graphInfo.addInfoToTxt(infoToTxt)
            Chart(graphInfo).draw()
    
    def statisticalAnalysisIntoLatex(self, analysisType, modelId):
        paths: simulationPathsManager = var.variablesDict[PATHS]

        infoToTxt = ''
        if analysisType in [D2F, D2D, F2F]:
            infoToTxt += '__ k & $R_{t}$ & $p_{t}$ & KS & $\gamma_{t}$ & $\gamma_{e}$ \\\\ \hline \n'
            firstLineAfterTableTitle = True
            wroteHowManyTimes = 0

            if paths.simulationRelatedWithRealCodeBase():
                empiricalGamma = self.getCumDistGammaOfHypForCompType(EMP, analysisType)
            else:
                empiricalGamma = "-"
        
        ceval = getStructInFile(paths.getComplexEvalPath())
        if ceval == {}:
            ceval = ComplexEval()
        ceval: ComplexEval
        for hyp in self.getHypothesis():
            ksValue = "-"

            if hyp != EMP and analysisType in [D2F, D2D, F2F]:
                if paths.simulationRelatedWithRealCodeBase():
                    ksValue = round(\
                        kolmogorovSmirnovCumDists(\
                            self.getCumDistOfHypForNet(EMP, analysisType), \
                            self.getCumDistOfHypForNet(hyp, analysisType), 
                            2
                        ), 2)
                
                paramsDict = fromHypNameToChRule(hyp)
                if paramsDict[ALPHA] == 0:
                    initialAttract = "-"
                else:
                    initialAttract = paramsDict[A]

                dsa = distStatisticalAnalysis(constructionType=FROM_DATA_TO_COMPARE, \
                    dataToCompare=self.getAllDataOfHypForAnalysisType(hyp, analysisType))

                # SAVE INFO FOR COMPLEX EVAL
                gammaDiff = abs(dsa.getPLGamma() - empiricalGamma)
                empMax = max(self.getAllDataOfHypForAnalysisType(EMP, analysisType))
                maxPercentage = round((dsa.getMax() / empMax) * 100)
                ceval.addKSforCEval(modelId, analysisType, hyp, ksValue)
                ceval.addGammaDiffForCEval(modelId, analysisType, hyp, gammaDiff)
                ceval.addMaxPercForCEval(modelId, analysisType, hyp, maxPercentage)

                # DSA INTO TXT
                if firstLineAfterTableTitle:
                    empiricalGammaStr = '\multirow{4}{*}' + '{' + str(round(empiricalGamma, 2)) + '}' 
                    lineInfo = '\cline{1-5}'
                    infoToTxt += "{} & {} & {} & {} & {} & {} \\\\ {}\n" \
                    .format(initialAttract, dsa.getR(), dsa.getP(), ksValue, dsa.getPLGamma(), empiricalGammaStr, lineInfo) 
                    firstLineAfterTableTitle = False
                else:
                    if wroteHowManyTimes == 3: # tables with 4 lines
                        lineInfo = '\hline'
                    else:
                        lineInfo = '\cline{1-5}'
                    infoToTxt += "{} & {} & {} & {} & {} & \\\\ {} \n" \
                        .format(initialAttract, dsa.getR(), dsa.getP(), ksValue, dsa.getPLGamma(), lineInfo)
                wroteHowManyTimes += 1

        if analysisType == "F2F" and modelId == 9: # last analysis
            ceval.selfToTxt()
        
        ceval.selfSave()
                    
        return infoToTxt