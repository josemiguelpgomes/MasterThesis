from utils.networksClasses import Network
import numpy as np

def averageAcrossResults(listOfLists, putZeros=True):
    """
    different networks may have different number of nodes, so, 
    to do a mean, we need the same number of nodes
    """
    lenOfListWithMoreValues = len(max(listOfLists, key=len))
    if putZeros:
        for li in range(len(listOfLists)):
            l = listOfLists[li]
            if len(l) != lenOfListWithMoreValues:
                listOfLists[li] = [0] * (lenOfListWithMoreValues - len(l)) + l

    return np.mean(listOfLists, axis=0)

def organizeResults(listOfDict):
    listOfLists = [] 
    for d in range(len(listOfDict)):
        listOfListsPart = []
        for k, v in sorted(listOfDict[d].items(), key=lambda x: x[1]):
            listOfListsPart += [v]
        listOfLists += [listOfListsPart]
    
    return listOfLists
    
def getMetricsAndAverage(nets, metric):
    netMetricSet = []
    for n in nets: 
        netMetricSet += [getResultOfMetric(n, metric)]
    
    organizedNetMetricSet = organizeResults(netMetricSet)
    return averageAcrossResults(organizedNetMetricSet)

def getResultOfMetric(net: Network, metric):
    if metric == "wd":
        return net.getDegrees(weight="weight")
    elif metric == "wdD2D":
        return net.getDegrees(weight="oneMonth_numberOfCollabs")
    elif metric == "wdF":
        return net.getDegrees(nbunch=net.getFileNodes(), weight="weight")