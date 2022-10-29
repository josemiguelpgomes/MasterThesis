import sys
import networkx as nx

from constants import *
import variables as var
from utils.pathClass import simulationPathsManager

from coreAnalysis import analyzeSimDist
from utils.auxiliaryFunctions import doesPathExist, getItemsInDir

from utils.networksClasses import Network

from simulationModel.analysis.hypothesisComparison import hypothesisResults

THEO_CODE_BASE = "theoCBs"
REAL_CODE_BASE = "realCBs"

def analyzeHyp(hypothesisDir):

    paths: simulationPathsManager = var.variablesDict[PATHS]
    paths.buildHypothesisPaths(hypothesisDir)
    
    # GET D2FNETS
    d2fnets = []
    for i in range(var.NUMBER_OF_NETWORKS):
        d2fnets += [Network(nx.read_gpickle('{}/d2f_{}.pickle'.format(paths.getHypothesisNetsDir(), i)))]

    # ANALYSIS ACROSS DIFFERENT NETS
    for netToAnalyse in [D2F, D2D, F2F]:
        analyzeSimDist(netToAnalyse, d2fnets, hypothesisDir)

if __name__ == "__main__":
    var.initVariablesDict()
    paths = var.variablesDict[PATHS] = simulationPathsManager()

    modelId = 1 

    realCBindex = 0
    realCBToAnalyze = sys.argv[1] if len(sys.argv) == 2 else var.REPOSITORIES_SET[0]

    theoCodeBaseId = 1
    mayHaveNextTheoCodeBase = False

    for cbType in [THEO_CODE_BASE, REAL_CODE_BASE]:
        while(True):
            var.variablesDict["compareHypothesis"] = False
            if cbType == REAL_CODE_BASE:
                paths.codebaseAttributesPaths(realCB=realCBToAnalyze, theoCodeBaseNr=None, fromAnalysis=True)
                paths.buildDistsPaths(modelId, fromAnalysis=True)
                
                hypRes = var.variablesDict[HYP_RESULTS] = hypothesisResults(startEmpRes=True)
            else:
                paths.codebaseAttributesPaths(realCB=None, theoCodeBaseNr=theoCodeBaseId, fromAnalysis=True)
                paths.buildDistsPaths(modelId, fromAnalysis=True)

                hypRes = var.variablesDict[HYP_RESULTS] = hypothesisResults(startEmpRes=False)

            if not doesPathExist(paths.getGenNetworksDir()):
                # gets next code base to analyze
                if mayHaveNextTheoCodeBase:
                    theoCodeBaseId += 1
                    modelId = 1
                    mayHaveNextTheoCodeBase = False
                    continue
                break

            if cbType == THEO_CODE_BASE:
                mayHaveNextTheoCodeBase = True

            FILES_TO_NOT_CONSIDER = [
                "theoreticalTimeline.pickle", "timelineComparisons"
            ]
            for hypothesisDir in getItemsInDir(paths.getGenNetworksDir()):
                if hypothesisDir in FILES_TO_NOT_CONSIDER:
                    continue
                analyzeHyp(hypothesisDir)
            
            if var.variablesDict["compareHypothesis"]:
                hypRes.comparison(modelId)

            modelId += 1
        
        modelId = 1