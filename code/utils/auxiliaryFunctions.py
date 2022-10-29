from operator import itemgetter
import os
import functools
import numpy as np
import pickle
import shutil

from constants import *
import variables as var

def listsSetDifference(list1, list2):
    return list(set(list1) - set(list2))

####################################################################################
# PROGRAM SPECIFICS

def codebaseNetsPath():
    return "DPN_{};DBN_{};MC_{}"\
        .format(var.HOW_MANY_DAYS_IN_A_NET, var.DAYS_BETWEEN_NETS, var.MAX_MONTHS_COLLAB)

def datetimeIntoStr(date, present=False):
    if date == ALL_TIME:
        return ALL_TIME
    
    if present:
        if var.DAYS_BETWEEN_NETS % 365 == 0 and var.HOW_MANY_DAYS_IN_A_NET % 365 == 0:
            return str(date.year)
        else:
            if date.month < 10:
                month = '0' + str(date.month)
            else:
                month = str(date.month)
            return '{}/{}'.format(month, date.year)
    else:
        return '{},{}'.format(date.month, date.year)

####################################################################################
# FILE SYSTEM INTERACTIONS

def createDirRec(path):
    for i in range(len(path.split("/"))):
        createDir("/".join(path.split("/")[:i]))
    createDir(path)

def createDir(path):
    currentPath = os.getcwd()
    currentPath = currentPath + "/" + path
    try:
        os.mkdir(currentPath)
    except OSError: # path is already created
        return -1

def removeDir(relativePath):
    currentPath = os.getcwd()
    currentPath = currentPath + "/" + relativePath
    if os.path.exists(currentPath):
        try:
            shutil.rmtree(currentPath)
        except OSError as e:
            print ("Error: %s - %s." % (e.filename, e.strerror))

def getStructInFile(fileName):
    try:
        with open(fileName, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError as e: 
        return {}

def saveStructInFile(d, fileName):
    with open(fileName, 'wb') as f:
        pickle.dump(d, f)

def doesPathExist(path):
    return os.path.exists(path)

def getItemsInDir(path):
    return os.listdir(path)

def getGraphData(graphPath):
    sPath = graphPath.split("/")
    figName = sPath[-1].split(".")[0]
    path = '{}/{}/{}.pickle'.format("/".join(sPath[:-1]), 'pickledData', figName)
    return getStructInFile(path)

def getFileOfSubdirsInDir(pathToDir, fileInfoName):
    dirComponents = sorted(os.listdir(pathToDir))

    fileDictList = []
    for d in dirComponents:
        createDirRec(pathToDir)
        f = open('{}/{}/{}'.format(pathToDir, d, fileInfoName), encoding="utf-8")

        # txt to dict
        fileDict = {}
        for line in f:
            sLine = line.split(":")
            sLine[1] = sLine[1][1:-1]
            try:
                if sLine[0] == PARAMS_ID:
                    fileDict[sLine[0]] = int(sLine[1])
                else:
                    fileDict[sLine[0]] = float(sLine[1])
            except ValueError:
                fileDict[sLine[0]] = sLine[1]
        
        fileDictList += [fileDict]
    
    return fileDictList

#################################################################################### 
# MATHS

def normalize(struct, xDist = "uni", alpha=None, normalizeDictValues=False):
    if normalizeDictValues: # dict
        l = struct.values()
    else: # list
        l = struct

    if list(filter(lambda x: x != 0, l)) == []:
        return [1 / len(l)] * len(l)
    
    if xDist == "uni":
        total = functools.reduce(lambda x, y: x + y, filter(lambda x: x != 0, l))
        if normalizeDictValues:
            return {k: v / total for k, v in struct.items()}
        else:
            return list(map(lambda x: x / total, l))

def histogram(values):
    hDict = {}
    for v in values:
        if v in hDict:
            hDict[v] += 1
        else:
            hDict[v] = 1
    return hDict

def cumulativeProbabilityDistribution(values, relativeProbability=True):
    hDict = histogram(values)
    x, y = [], []
    for kS in sorted(hDict.keys()):
        x += [kS]
        y += [hDict[kS]]
    y = np.cumsum(y[::-1])[::-1]
    if relativeProbability:
        y = list(map(lambda x: x / len(values), y))
    return x, y

def kolmogorovSmirnovCumDists(cumDist1, cumDist2, inverseCumDists=True, topKS=False):
    x1, y1 = cumDist1
    x2, y2 = cumDist2

    cd1Values, cd2Values = [], []
    infoAboutVal = {}
    for iX in range(len(x1)):
        x = x1[iX]
        if x in x2: 
            xIndexInX2 = x2.index(x)
            cd1Values += [y1[iX]]
            cd2Values += [y2[xIndexInX2]]
            infoAboutVal[x] = ("BOTH", len(cd1Values) - 1)
        else:
            x2Iterator = 0
            while (x2Iterator < len(x2) and x > x2[x2Iterator]):
                if x < x2[x2Iterator]:
                    break
                x2Iterator += 1
            
            if x2Iterator == len(x2):
                cd1Values += [y1[iX]]
                if inverseCumDists:
                    cd2Values += [0]
                else:
                    cd2Values += [1]
            else: 
                cd1Values += [y1[iX]]
                cd2Values += [y2[x2Iterator]]
            infoAboutVal[x] = ("ONLY_1", len(cd1Values) - 1)
    
    for iX in range(len(x2)):
        x = x2[iX]
        if x not in x1:
            x1Iterator = 0
            while (x1Iterator < len(x1) and x > x1[x1Iterator]):

                if x < x1[x1Iterator]:
                    break
                x1Iterator += 1
            
            if x1Iterator == len(x1):
                if inverseCumDists:
                    cd1Values += [0]
                else:
                    cd1Values += [1]
                cd2Values += [y2[iX]]
            else: 
                cd1Values += [y1[x1Iterator]]
                cd2Values += [y2[iX]]
            infoAboutVal[x] = ("ONLY_2", len(cd1Values) - 1)

    maxDiff = 0
    if topKS:
        numberOfValues1, numberOfValues2 = 0, 0
        for val, info in sorted(infoAboutVal.items(), key=itemgetter(0), reverse=True):
            if numberOfValues1 >= 10 and numberOfValues2 >= 10:
                indexToStartFrom = info[1]
                break
            if info[0] == "BOTH":
                numberOfValues1 += 1
                numberOfValues2 += 1
            elif info[0] == "ONLY_1":
                numberOfValues1 += 1
            elif info[0] == "ONLY_2":
                numberOfValues2 += 1

        indexesToEvaluate = range(indexToStartFrom, len(cd1Values))
    else:
        indexesToEvaluate = range(len(cd1Values))

    for i in indexesToEvaluate:
        valDiff = abs(cd1Values[i] - cd2Values[i])
        if valDiff > maxDiff:
            maxDiff = valDiff

    return maxDiff
