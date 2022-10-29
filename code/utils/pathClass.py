from constants import *
import variables as var
from utils.auxiliaryFunctions import createDirRec, codebaseNetsPath, doesPathExist

class PathsManager:
    def __init__(self):
        self.pathDict = {}
        pass

class dataMiningPathsManager(PathsManager): # TODO strings to constants
    def __init__(self, codebase):
        super().__init__()
        self.pathDict["CODE_BASE_NAME"] = codebase.split("/")[1]

        self.pathDict["CODE_BASE_DIR"] = '{}/{}'.format(RESULTSDIR, self.pathDict["CODE_BASE_NAME"])

        self.pathDict["RAW_DATA_DIR"] = '{}/rawData'.format(self.pathDict["CODE_BASE_DIR"])
        self.pathDict["RAW_DATA_CODE"] = '{}/code.txt'.format(self.pathDict["RAW_DATA_DIR"])
        createDirRec(self.pathDict["RAW_DATA_DIR"])

        self.pathDict["RESULTS_INFO_DIR"] = '{}/informationOnAlgorithmsResults'.format(self.pathDict["CODE_BASE_DIR"])
        self.pathDict["RESULTS_INFO_CODE"] = '{}/infoAboutCodeGathering.txt'.format(self.pathDict["RESULTS_INFO_DIR"])
        createDirRec(self.pathDict["RESULTS_INFO_DIR"])

        self.pathDict["CODE_BASE_URL"] = 'https://github.com/{}'.format(codebase)
        pass

    def getPathToStoreCodeRawData(self):
        return self.pathDict["RAW_DATA_CODE"]
    
    def getPathToStoreMiningProcessResults(self):
        return self.pathDict["RESULTS_INFO_CODE"]
    
    def codebaseURL(self):
        return self.pathDict["CODE_BASE_URL"]

class netConstructionPathsManager(PathsManager):
    def __init__(self, codebase):
        super().__init__()
        self.pathDict["CODE_BASE_NAME"] = codebase.split("/")[1]
        self.pathDict["CODE_BASE_DIR"] = '{}/{}'.format(RESULTSDIR, self.pathDict["CODE_BASE_NAME"])

        self.pathDict["CODE_BASE_NET_TYPES"] = '{}/networksDir'.format(self.pathDict["CODE_BASE_DIR"])
        self.pathDict["CODE_BASE_NETS"] = '{}/{}'.format(self.pathDict["CODE_BASE_NET_TYPES"], codebaseNetsPath())
        createDirRec(self.pathDict["CODE_BASE_NETS"])

        self.pathDict["RAW_DATA_CODE"] = '{}/rawData/code.txt'.format(self.pathDict["CODE_BASE_DIR"])

        self.pathDict["EMPIRICAL_TIME_LINE"] = "{}/empiricalTimeline.pickle".format(self.pathDict["CODE_BASE_DIR"])

    def getCodebaseName(self):
        return self.pathDict["CODE_BASE_NAME"]

    def getCodebaseDir(self):
        return self.pathDict["CODE_BASE_DIR"]

    def getCodeBaseNetTypes(self):
        return self.pathDict["CODE_BASE_NET_TYPES"]

    def getCodeBaseNetsPath(self):
        return self.pathDict["CODE_BASE_NETS"]

    def getPathCodeRawData(self):
        return self.pathDict["RAW_DATA_CODE"]
    
    def getEmpiricalTL(self):
        return self.pathDict["EMPIRICAL_TIME_LINE"]

class netAnalysisPathsManager(PathsManager):
    def __init__(self, codebase):
        super().__init__()

        self.pathDict["CODE_BASE_NAME"] = codebase.split("/")[1]
        self.pathDict["CODE_BASE_DIR"] = '{}/{}'.format(RESULTSDIR, self.pathDict["CODE_BASE_NAME"])
        self.pathDict["CODE_BASE_GRAPHS"] = "{}/graphsDir/{}".format(self.pathDict["CODE_BASE_DIR"], codebaseNetsPath())

        self.pathDict["EMPIRICAL_TIME_LINE"] = "{}/empiricalTimeline.pickle".format(self.pathDict["CODE_BASE_DIR"])


    def getCodeBaseName(self):
        return self.pathDict["CODE_BASE_NAME"]

    def getCodeBaseDir(self):
        return self.pathDict["CODE_BASE_DIR"]

    def getCodeBaseGraphs(self):
        return self.pathDict["CODE_BASE_GRAPHS"]

    def getEmpiricalTL(self):
        return self.pathDict["EMPIRICAL_TIME_LINE"]

class simulationPathsManager(PathsManager):
    def __init__(self):
        super().__init__()
    
    def simulationRelatedWithRealCodeBase(self):
        return "CODE_BASE_NAME" in self.pathDict.keys()

    def codebaseAttributesPaths(self, realCB, theoCodeBaseNr, fromAnalysis=False):
        if realCB == None:
            self.pathDict["CODE_BASE_DIR"] = RESULTSDIR + "/" + THEOCODEBASES
            createDirRec(self.pathDict["CODE_BASE_DIR"])

            self.pathDict["THEO_CODE_BASE_PATH"] = '{}/theoCodeBase_{}'.format(self.pathDict["CODE_BASE_DIR"], theoCodeBaseNr)
            self.pathDict["THEO_CODE_BASE_INFO"] = '{}/cbAttrsInfo.txt'.format(self.pathDict["THEO_CODE_BASE_PATH"])
            self.pathDict["GEN_MODEL_DIR"] = '{}/simulations;MC_{}'.format(self.pathDict["THEO_CODE_BASE_PATH"], var.MAX_MONTHS_COLLAB)
        else:
            self.pathDict["CODE_BASE_NAME"] = realCB.split("/")[1]
            self.pathDict["CODE_BASE_DIR"] = '{}/{}'.format(RESULTSDIR, self.pathDict["CODE_BASE_NAME"])
            self.pathDict["EMPIRICAL_TL"] = '{}/empiricalTimeline.pickle'.format(self.pathDict["CODE_BASE_DIR"])
            self.pathDict["COMPLEX_EVAL_PICKLE"] = '{}/comparisonAcrossSDists.pickle'.format(self.pathDict["CODE_BASE_DIR"])
            self.pathDict["COMPLEX_EVAL_TXT"] = '{}/comparisonAcrossSDists.txt'.format(self.pathDict["CODE_BASE_DIR"])
            self.pathDict["GEN_MODEL_DIR"] = '{}/simulations;MC_{}'.format(self.pathDict["CODE_BASE_DIR"], var.MAX_MONTHS_COLLAB)
        
        if not fromAnalysis:
            createDirRec(self.pathDict["GEN_MODEL_DIR"])

    def buildDistsPaths(self, distsId, fromAnalysis=False):
        self.pathDict["GEN_MODEL"] = '{}/dists_{}/'.format(self.pathDict["GEN_MODEL_DIR"], distsId)

        self.pathDict["GEN_INFO_PKL"] = '{}/dists_{}/info.pickle'.format(self.pathDict["GEN_MODEL_DIR"], distsId)
        self.pathDict["GEN_DISTS_INFO"] = '{}/dists_{}/distsInfo.txt'.format(self.pathDict["GEN_MODEL_DIR"], distsId)
        self.pathDict["GEN_NETWORKS_DIR"] = '{}/dists_{}/networks'.format(self.pathDict["GEN_MODEL_DIR"], distsId)
        self.pathDict["GEN_GRAPHS_DIR"] = '{}/dists_{}/graphs'.format(self.pathDict["GEN_MODEL_DIR"], distsId)

        self.pathDict["GEN_TIMELINE"] = '{}/theoreticalTimeline.pickle'.format(self.pathDict["GEN_NETWORKS_DIR"])
        self.pathDict["COMPARISONS_DIR"] = '{}/timelineComparisons'.format(self.pathDict["GEN_NETWORKS_DIR"])
        self.pathDict["HYPOTHESIS_COMPARISON_DIR"] = '{}/hypothesisComparison'.format(self.pathDict["GEN_GRAPHS_DIR"])

        if fromAnalysis:
            if doesPathExist(self.pathDict["GEN_NETWORKS_DIR"]):
                createDirRec(self.pathDict["GEN_GRAPHS_DIR"])
                createDirRec(self.pathDict["HYPOTHESIS_COMPARISON_DIR"])
        else:
            createDirRec(self.pathDict["GEN_NETWORKS_DIR"])
            createDirRec(self.pathDict["COMPARISONS_DIR"])

        #var.pathDict["dataToRedoComparisons"] = '{}/dataToRedoGraphs'.format(var.pathDict["HYPOTHESIS_COMPARISON_DIR"])
        #var.pathDict["infoToRedoGraphs"] = '{}/data.pickle'.format(var.pathDict["dataToRedoComparisons"])
        #createDirRec(var.pathDict["dataToRedoComparisons"])

    def buildHypothesisPaths(self, hypothesisDir):
        self.pathDict["HYPOTHESIS_NETS_DIR"] = "{}/{}".format(self.pathDict["GEN_NETWORKS_DIR"], hypothesisDir)
        self.pathDict["HYPOTHESIS_GRAPHS_DIR"] = "{}/{}".format(self.pathDict["GEN_GRAPHS_DIR"], hypothesisDir)
        
        if doesPathExist(self.pathDict["HYPOTHESIS_NETS_DIR"]):
            createDirRec(self.pathDict["HYPOTHESIS_GRAPHS_DIR"])
        createDirRec(self.pathDict["HYPOTHESIS_NETS_DIR"])

    def getCodeBaseDir(self):
        return self.pathDict["CODE_BASE_DIR"]

    def getComplexEvalPath(self):
        return self.pathDict["COMPLEX_EVAL_PICKLE"]

    def getComplexEvalTxt(self):
        return self.pathDict["COMPLEX_EVAL_TXT"]

    def getEmpiricalTL(self):
        return self.pathDict["EMPIRICAL_TL"]

    def getTheoCodeBasePath(self):
        return self.pathDict["THEO_CODE_BASE_PATH"]

    def getTheoCodeBaseInfo(self):
        return self.pathDict["THEO_CODE_BASE_INFO"]

    def getGenModelDir(self):
        return self.pathDict["GEN_MODEL_DIR"]

    def getCodeBaseName(self):
        return self.pathDict["CODE_BASE_NAME"]

    def getGenNetworksDir(self):
        return self.pathDict["GEN_NETWORKS_DIR"]

    def getGenGraphsDir(self):
        return self.pathDict["GEN_GRAPHS_DIR"]

    def getGenTimeLine(self):
        return self.pathDict["GEN_TIMELINE"]
    
    def getHypothesisNetsDir(self):
        return self.pathDict["HYPOTHESIS_NETS_DIR"]

    def getHypothesisGraphsDir(self):
        return self.pathDict["HYPOTHESIS_GRAPHS_DIR"]

    def getHypothesisComparisonDir(self):
        return self.pathDict["HYPOTHESIS_COMPARISON_DIR"]

    def getGenDistsInfo(self):
        return self.pathDict["GEN_DISTS_INFO"]

    def getGenInfoPickle(self):
        return self.pathDict["GEN_INFO_PKL"]

    def getComparisonsDir(self):
        return self.pathDict["COMPARISONS_DIR"]