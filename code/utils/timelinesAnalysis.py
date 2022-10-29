from math import ceil
import numpy as np

from constants import *
import variables as var

from utils.auxiliaryFunctions import cumulativeProbabilityDistribution, kolmogorovSmirnovCumDists, getStructInFile, saveStructInFile
from utils.graphsCreation import Chart, GraphInfo
from utils.timelineClass import Timeline

from simulationModel.analysis.complexEvalClass import ComplexEval

DEV_EXISTENCE = "intervalBetweenFirstAndLastCommitOfDev"

def divideAllMembersBy(l, value):
    return list(map(lambda x: x / value, l))

def getUniformityMetricDistribution(tl: Timeline, intervalForDeveloper):
    """
    interval for developer can have two different arguments
    ALL_TIME -> uniformity is measured since the first commit of the code base until the last commit of the code base
    DEV_EXISTENCE -> uniformity is measure since first commit of developer until the last commit of developer
    """

    TSperAuthor = {} # timesteps per author

    commitNumber = max(tl.getCommitIds()) 
    
    # ----------------------
    # GET TIME STEPS AND DATES PER AUTHOR
    for commitId in tl.getCommitIds():
        commitAuthor = tl.getAuthorOfCommitId(commitId)
        commitDate = tl.getDateOfCommitId(commitId)
        if commitAuthor in TSperAuthor.keys():
            TSperAuthor[commitAuthor]["timesteps"] += [commitId]
            TSperAuthor[commitAuthor]["dates"] += [commitDate]
        else:
            TSperAuthor[commitAuthor] = {}
            TSperAuthor[commitAuthor]["timesteps"] = [commitId]
            TSperAuthor[commitAuthor]["dates"] = [commitDate]
            TSperAuthor[commitAuthor]["uniformityValue"] = None
            TSperAuthor[commitAuthor]["worstValueForUniformity"] = None
    
    # ---------------------
    # CALCULATE UNIFORMITY PER DEVELOPER
    for dev in TSperAuthor.keys():
        infoPerDev = TSperAuthor[dev]
        nrCommitsDev = len(infoPerDev["dates"])
        
        # ---------------------------
        # GET SEQUENCES OF COMMITS ASSOCIATED TO THE MOST UNIFORM COMMITS AND LESS UNIFORM COMMITS ACROSS THE INTERVAL 
        if intervalForDeveloper == ALL_TIME:
            bestUniformInterval = commitNumber / (nrCommitsDev+1)
            developersCommit_th = 0 # 0 means that this is the first commit of the developer, index 0 of list
            
            # get less uniform case (followed commits in the beginning)
            lessUniformCommitValues = list(range(1, nrCommitsDev+1))
            bestUniformTimesteps = np.arange(bestUniformInterval, commitNumber, bestUniformInterval)
            if ceil(bestUniformTimesteps[-1]) == commitNumber:
                bestUniformTimesteps = bestUniformTimesteps[:-1]
        elif intervalForDeveloper == DEV_EXISTENCE:
            if nrCommitsDev <= 2: # is only calculated for devs with more than two commits
                infoPerDev["uniformityMetric"] = None
                continue

            developersCommit_th = 1 # 1 means that this is the second commit of the developer, index 1 of the list

            devFirstCommit = min(infoPerDev["timesteps"])
            devLastCommit = max(infoPerDev["timesteps"])
            lessUniformCommitValues = list(range(devFirstCommit + 1, devFirstCommit + nrCommitsDev - 1))
            
            bestUniformInterval = (devLastCommit - devFirstCommit) / (nrCommitsDev - 1)

            bestUniformTimesteps = np.arange(devFirstCommit + bestUniformInterval, devLastCommit, bestUniformInterval)
            if ceil(bestUniformTimesteps[-1]) >= devLastCommit:
                bestUniformTimesteps = bestUniformTimesteps[:-1]

        # ----------------------------------------
        # MEASURE THE DIFFERENCE BETWEEN INTERVALS
        # DIFFERENCE BETWEEN WORST CASE AND IDEAL SERVES AS A LIMIT OF UNIFORMITY, IN THIS CASE THE WORSE UNIFORMITY

        infoPerDev["uniformityValue"] = 0
        infoPerDev["worstValueForUniformity"] = 0

        for bestTime in bestUniformTimesteps:
            if intervalForDeveloper == ALL_TIME:
                differenceBetweenRealAndIdeal = abs(infoPerDev["timesteps"][developersCommit_th] - bestTime)
                differenceBetweenWorstCaseAndIdeal = abs(lessUniformCommitValues[developersCommit_th] - bestTime)
            elif intervalForDeveloper == DEV_EXISTENCE:
                differenceBetweenRealAndIdeal = abs(infoPerDev["timesteps"][developersCommit_th] - bestTime)
                differenceBetweenWorstCaseAndIdeal = abs(lessUniformCommitValues[developersCommit_th-1] - bestTime) + 1

            infoPerDev["uniformityValue"] += differenceBetweenRealAndIdeal
            infoPerDev["worstValueForUniformity"] += differenceBetweenWorstCaseAndIdeal + 1
                
            developersCommit_th += 1
        
        # ---------------------------------------------------------------------
        # NORMALIZE UNIFORMITY VALUE, USING THE WORST UNIFORMITY VALUE AS A CAP

        # first, get the mean uniformity per developer 
        infoPerDev["uniformityValue"] = infoPerDev["uniformityValue"] / nrCommitsDev
        infoPerDev["worstValueForUniformity"] = infoPerDev["worstValueForUniformity"] / nrCommitsDev

        if infoPerDev["worstValueForUniformity"] == 0 and infoPerDev["uniformityValue"] == 0:
            infoPerDev["uniformityMetric"] = 0
        else:
            infoPerDev["uniformityMetric"] = infoPerDev["uniformityValue"] / infoPerDev["worstValueForUniformity"]
    
    devUniformityValues = list(filter(lambda x: x != None, map(lambda x: x["uniformityMetric"], TSperAuthor.values())))
    return cumulativeProbabilityDistribution(sorted(devUniformityValues))

# ----------

def timelineComparison(whichTimelinesToGet, draw=True):
    paths = var.variablesDict[PATHS]

    if whichTimelinesToGet == EMP:
        empData, empTLClass = getStructInFile(paths.getEmpiricalTL()).getCAForSimulation()
        timelines = [EMP]
    elif whichTimelinesToGet == THEO:
        theoData, theoTLClass = getStructInFile(paths.getGenTimeLine()).getCAForSimulation()
        timelines = [THEO]
    elif whichTimelinesToGet == BOTH_TL:
        theoData, theoTLClass = getStructInFile(paths.getGenTimeLine()).getCAForSimulation()
        empData, empTLClass = getStructInFile(paths.getEmpiricalTL()).getCAForSimulation()
        timelines = [EMP, THEO]

    aspectRes = {}

    for aspect in CODEBASE_ASPECTS:
        for tl in timelines:
            if aspect in [FILES_ADDED_UNTIL_T, FILES_DELETED_UNTIL_T, FILES_CHANGED_UNTIL_T]:
                tlClass = theoData[aspect] if tl == THEO else empData[aspect]
                if aspect not in aspectRes:
                    aspectRes[aspect] = {}
                aspectRes[aspect][tl] = tlClass
            
            elif aspect == DATE_DIFF_PER_T:
                if aspect not in aspectRes:
                    aspectRes[aspect] = {}
                aspectRes[aspect][tl] = []
                tlClass = theoData[DATE_DIFF_PER_T] if tl == THEO else empData[DATE_DIFF_PER_T]

                for di in range(len(tlClass) - 1):
                    aspectRes[aspect][tl] += [(tlClass[di + 1] - tlClass[di]).total_seconds()]
            
            elif aspect == COMMITS_PER_DEV:
                if aspect not in aspectRes:
                    aspectRes[aspect] = {}
                tlClass = theoData[COMMITS_PER_DEV] if tl == THEO else empData[COMMITS_PER_DEV]
                aspectRes[aspect][tl] = cumulativeProbabilityDistribution(tlClass.values())

            elif aspect == NEW_DEVS_UNTIL_T:
                if aspect not in aspectRes:
                    aspectRes[aspect] = {}
                tlClass = theoTLClass if tl == THEO else empTLClass
                aspectRes[aspect][tl], authorsUntilT, numberDevsInT = [], {}, 0
                for commitId in tlClass.getCommitIds():
                    author = tlClass.getAuthorOfCommitId(commitId)
                    if author not in authorsUntilT.keys():
                        numberDevsInT += 1
                        authorsUntilT[author] = 1
                    aspectRes[aspect][tl] += [numberDevsInT]
                
                tlData = theoData if tl == THEO else empData
                aspectRes[aspect][tl] = divideAllMembersBy(aspectRes[aspect][tl], len(tlData[COMMITS_PER_DEV].keys()))
                    
            elif aspect in [U_GLOBAL, U_LOCAL]:
                if aspect not in aspectRes:
                    aspectRes[aspect] = {}
                intervalToConsider = ALL_TIME if aspect == U_GLOBAL \
                    else DEV_EXISTENCE
                
                tlClass = theoTLClass if tl == THEO else empTLClass
                aspectRes[aspect][tl] = getUniformityMetricDistribution(tlClass, intervalToConsider)
            
        if aspect in [FILES_ADDED_UNTIL_T, FILES_DELETED_UNTIL_T, FILES_CHANGED_UNTIL_T, DATE_DIFF_PER_T]:
            for tl in timelines:
                aspectRes[aspect][tl] = np.cumsum(aspectRes[aspect][tl])

            if whichTimelinesToGet == BOTH_TL or whichTimelinesToGet == EMP:
                valueToNormalizeBy = aspectRes[aspect][EMP][-1]

                for tl in timelines:
                    aspectRes[aspect][tl] = divideAllMembersBy(aspectRes[aspect][tl], valueToNormalizeBy)

    if draw:
        for aspect in CODEBASE_ASPECTS:
            if aspect in [U_GLOBAL, U_LOCAL, COMMITS_PER_DEV]:
                cumDistOrCumSum = CUM_DIST
            else:
                cumDistOrCumSum = CUM_SUM
            createGraphForAspect(aspect, aspectRes[aspect], cumDistOrCumSum, whichTimelinesToGet)
    else:
        return aspectRes

def createGraphForAspect(aspect, res, cumDistOrCumSum, whichTimelinesToGet):
    paths = var.variablesDict[PATHS]

    loglog = True if aspect == COMMITS_PER_DEV else False

    if whichTimelinesToGet == EMP:
        if cumDistOrCumSum == CUM_DIST:
            res[aspect] = [res[EMP]]
        elif cumDistOrCumSum == CUM_SUM:
            eCumDist = [range(len(res[EMP])), res[EMP]]
            res[aspect] = [eCumDist]

        legendLabels = None
    elif whichTimelinesToGet == THEO:
        if cumDistOrCumSum == CUM_DIST:
            res[aspect] = [res[THEO]]
        elif cumDistOrCumSum == CUM_SUM:
            tCumDist = [range(len(res[THEO])), res[THEO]]
            res[aspect] = [tCumDist]
        legendLabels = None
        infoToTxt = ""
    else:
        distsId = var.variablesDict[DISTS]["paramsId"]
        if cumDistOrCumSum == CUM_DIST:
            res[aspect] = [res[THEO], res[EMP]]
            aspectKS = kolmogorovSmirnovCumDists(res[THEO], res[EMP])
            infoToTxt = "KS against empirical: {}".format(aspectKS)
        elif cumDistOrCumSum == CUM_SUM:
            eCumDist = [range(len(res[EMP])), res[EMP]]
            tCumDist = [range(len(res[THEO])), res[THEO]]
            res[aspect] = [tCumDist, eCumDist]
            aspectKS = kolmogorovSmirnovCumDists(tCumDist, eCumDist, inverseCumDists=False)
            infoToTxt = "KS against empirical: {}".format(aspectKS)

        ceval = getStructInFile(paths.getComplexEvalPath())
        if ceval == {}:
            ceval = ComplexEval()
        ceval: ComplexEval
        ceval.addAspectForCEval(distsId, aspect, round(aspectKS, 2))
        ceval.selfSave()

        legendLabels = [THEO, EMP]
    
    graphInfo = GraphInfo()
    graphInfo.setData(res[aspect])
    graphInfo.setXLabel(CONCRETE_GRAPH_INFO_CB_ASPECTS[aspect][XLABEL])
    graphInfo.setYLabel(CONCRETE_GRAPH_INFO_CB_ASPECTS[aspect][YLABEL])
    graphInfo.setPath('{}/{}.png'.format(paths.getComparisonsDir(), aspect))
    graphInfo.setLegends(legendLabels)
    graphInfo.setLoglog(loglog)
    graphInfo.addInfoToTxt(infoToTxt)
    Chart(graphInfo).draw()

