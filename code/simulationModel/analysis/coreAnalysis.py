import multiprocessing as mp
import networkx as nx
from math import ceil

from constants import *
import variables as var
from utils.pathClass import simulationPathsManager

from utils.networksClasses import Network, devToDevNetworks
from utils.auxiliaryFunctions import doesPathExist, cumulativeProbabilityDistribution, codebaseNetsPath

from simulationModel.simulation.simulateTimeline.classes import Developer, File, Context
from simulationModel.analysis.hypothesisComparison import hypothesisResults

from simulationModel.analysis.getMetrics import getMetricsAndAverage, averageAcrossResults
from graphsCreation import createGraphHypResForAnalysisType

class devToDevThread:
    def __init__(self, queue, lock, d2fNet: Network, d2dNetPath):
        D2Dnet = Network(nx.Graph(timeRestricted=True, netPath=d2dNetPath))

        D2DnetsClass = devToDevNetworks(FILE_TYPE, D2Dnet, d2fNet, save=False)

        for dev in d2fNet.getDeveloperNodes():
            D2DnetsClass.net.addNode(dev)
        D2DnetsClass.net.saveNet()
        lock.acquire()
        queue.put(D2DnetsClass.net)
        lock.release()

def comparisonCollaborationPerFile(d2dnets, hyp):
    hypResults: hypothesisResults = var.variablesDict[HYP_RESULTS]
    paths: simulationPathsManager = var.variablesDict[PATHS]

    if paths.simulationRelatedWithRealCodeBase():
        netPath = '{}/networksDir/{}/{}_D2D.pickle' \
            .format(paths.getCodeBaseDir(), codebaseNetsPath(), FILE_TYPE)
        net = Network(nx.read_gpickle(netPath))

        hypResults.setCumDistOfHypForAnalysisType(EMP, COLLAB_PER_FILE, \
            cumulativeProbabilityDistribution(list(net.getNetAttrib(COLLAB_PER_FILE).values())))

    collaborationPerFileInDifferentNets = []
    for i in range(0, len(d2dnets)):
        collaborationPerFileInDifferentNets += [list(d2dnets[0].getNetAttrib(COLLAB_PER_FILE).values())]
    
    hypResults.setCumDistOfHypForAnalysisType(hyp, COLLAB_PER_FILE, \
        cumulativeProbabilityDistribution(averageAcrossResults(collaborationPerFileInDifferentNets, putZeros=False)))

def analyzeSimDist(netToAnalyse, d2fnets, hypothesisDir):
    paths: simulationPathsManager = var.variablesDict[PATHS]

    if not doesPathExist('{}/{}.png'.format(paths.getHypothesisGraphsDir(), netToAnalyse)):
        var.variablesDict["compareHypothesis"] = True

        d2dNets = []
        f2fnets = []

        if netToAnalyse == D2D:
            if doesPathExist('{}/d2d_{}.pickle'.format(paths.getHypothesisNetsDir(), 0)):
                for i in range(var.NUMBER_OF_NETWORKS):
                    d2dNets += [Network(nx.read_gpickle('{}/d2d_{}.pickle'.format(paths.getHypothesisNetsDir(), i)))]
            else:
                for t in range(0, ceil(var.NUMBER_OF_NETWORKS/var.THREADS)):
                    processes = []
                    queue = mp.Queue()
                    lock = mp.Lock()

                    for i in range(var.THREADS):
                        d2dNetPath = '{}/d2d_{}.pickle'.format(paths.getHypothesisNetsDir(), i)
                        p = mp.Process(target=devToDevThread, args=(queue, lock, d2fnets[i], d2dNetPath))
                        processes += [p]
                        p.start()

                    for p in processes:
                        d2f_tr = queue.get()
                        d2dNets += [d2f_tr]

                    for p in processes:
                        p.join()
            
            comparisonCollaborationPerFile(d2dNets, hypothesisDir)

        elif netToAnalyse == F2F:
            for i in range(var.NUMBER_OF_NETWORKS):
                f2fnets += [Network(nx.read_gpickle('{}/f2f_{}.pickle'.format(paths.getHypothesisNetsDir(), i)))]

        paramsInfo = {
            D2F: {"netsToAnalyze": d2fnets    , "metricToAnalyze": "wdF"  },
            D2D: {"netsToAnalyze": d2dNets    , "metricToAnalyze": "wdD2D"},
            F2F: {"netsToAnalyze": f2fnets    , "metricToAnalyze": "wd"   }
        }

        netsToAnalyze   = paramsInfo[netToAnalyse]["netsToAnalyze"]
        metricToAnalyze = paramsInfo[netToAnalyse]["metricToAnalyze"]

        averagedData = getMetricsAndAverage(netsToAnalyze, metricToAnalyze)
        createGraphHypResForAnalysisType(averagedData, netToAnalyse, hypothesisDir)