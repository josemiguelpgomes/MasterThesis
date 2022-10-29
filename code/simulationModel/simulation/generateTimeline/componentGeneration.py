import numpy as np
from datetime import datetime, timedelta

from constants import *
import variables as var

from utils.auxiliaryFunctions import normalize

from simulationModel.simulation.generateTimeline.sequenceGeneration \
    import constroyUniformSequence, constroyPowerOrExponentialSequence
from simulationModel.simulation.generateTimeline.componentCharacteristics import Component

def createEachComponentOverTime(timelineComponents):
    for component, cInfo in timelineComponents.items():
        cInfo: Component
        if component == DATES:
            continue

        if cInfo.getDist() == UNIF_DIST:
            timelineComponents = getUniformSequence(timelineComponents, component)
        elif cInfo.getDist() in [EXP_DIST, PL_DIST]:
            timelineComponents = getPowerOrExponentialSequence(timelineComponents, component, cInfo.getDist())
        else:
            timelineComponents = getSpecificSequences(timelineComponents, component, cInfo.getDist())
        
        # first commit should have files added
        if component == FILES_ADDED: 
            if cInfo.getResultForCommit(0) == 0:
                for i in range(1, len(cInfo.getResults())):
                    if cInfo.getResultForCommit(i) != 0:
                        cInfo.switchCommitsResults(0, i)

        # each commit has atleast 1 add or 1 change
        if component == FILES_CHANGED:
            fChangesResults = cInfo.getResults()
            fAddResults = timelineComponents[FILES_ADDED].getResults()
            for i in range(len(fChangesResults)):
                if fChangesResults[i] == 0:
                    if fAddResults[i] == 0:
                        possibleIndex = False
                        while not possibleIndex:
                            indexToRemoveFrom = np.random.choice(range(len(fChangesResults)), p=normalize(fChangesResults))
                            if fChangesResults[indexToRemoveFrom] <= 1:
                                continue
                            possibleIndex = True
                    
                        fChangesResults[i] += 1
                        fChangesResults[indexToRemoveFrom] -= 1
        
        # update info according to constructed approximated sequence
        if component == COMMITS and cInfo.getDist() != UNIF_DIST:
            numberOfCommits = sum(cInfo.getResults())

            cInfo.setTotal(numberOfCommits)

            timelineComponents[FILES_ADDED].setCLen(numberOfCommits)
            timelineComponents[FILES_CHANGED].setCLen(numberOfCommits)
            timelineComponents[FILES_DELETED].setCLen(numberOfCommits)

    verifyRestrictions(timelineComponents)

    timelineComponents = createDateSequence(timelineComponents)

    return timelineComponents

def getUniformSequence(timelineComponents: dict[str, Component], component):
    limitPerTimestep = getLimitPerTimestep(timelineComponents, component)

    # DISTRIBUTE UNIFORMILY ACROSS ALL ENTITIES (DEVELOPERS OR COMMITS)
    cInfo: Component = timelineComponents[component]
    
    sequence = []
    perc = var.variablesDict[DISTS][P_ADDS_FIRST_COMMIT] 
    if component == FILES_ADDED and perc != "-":
        seq_0 = round(cInfo.getTotal() * float(perc))
        sequence = [round(cInfo.getTotal() * float(perc))]

        seqSum = cInfo.getTotal() - seq_0
        seqMean = seqSum / (cInfo.getCLen() - 1)
        seqLen = cInfo.getCLen() - 1
    else:
        seqMean = cInfo.getMean()
        seqLen=cInfo.getCLen()
        seqSum=cInfo.getTotal()

    timelineComponents[component].setResults(sequence + constroyUniformSequence(
            seqMean=seqMean, 
            seqLength=seqLen, 
            seqSum=seqSum, 
            limitPerI=limitPerTimestep, 
            attrib=component,
        ))

    return timelineComponents

def getPowerOrExponentialSequence(timelineComponents, component, knownDist):
    cInfo: Component = timelineComponents[component]
    numberOfCommits = timelineComponents[COMMITS].getTotal()

    if component == COMMITS: 
        # ALL DEVELOPERS MUST HAVE ATLEAST ONE COMMIT
        nonZeroValuesPerCommit = cInfo.getCLen()
        numberOfZerosInValues = 0
    else: # NOT ALL COMMITS NEED TO HAVE ADDED FILES OR DELETED FILES OR CHANGED FILES
        nonZeroValuesPerCommit = len(cInfo.getNotZeros())
        numberOfZerosInValues = numberOfCommits - nonZeroValuesPerCommit

    if numberOfZerosInValues == 0:
        sumOfNotZeros = cInfo.getTotal()
    else:
        sumOfNotZeros = sum(cInfo.getNotZeros())

    sequence = list(constroyPowerOrExponentialSequence(
        objectiveDist=knownDist, 
        seqSum=sumOfNotZeros, 
        seqSize=nonZeroValuesPerCommit, 
        saveInCache=True, 
        nearValue=True
    ))

    if component == COMMITS:
        timelineComponents[component].setResults(sequence)
    else:
        # MAKES SURE THAT RESTRICTIONS ARE FOLLOWED AND DISTRIBUTE VALUES BY TIME.
        limitPerTimestep = getLimitPerTimestep(timelineComponents, component)
        # TODO
        pass
        
    return timelineComponents

def getSpecificSequences(timelineComponents, component, knownDist):
    cInfo: Component = timelineComponents[component]
    
    if knownDist == ALL_IN_FIRST:
        assert(component == FILES_ADDED) # tested only for filesAdded
        cInfo.setResults([0] * cInfo.getCLen())
        cInfo.setResultForCommit(0, cInfo.getTotal())
    
    return timelineComponents

def getLimitPerTimestep(timelineComponents, component):
    limitPerTimestep = None
    if component == FILES_DELETED: 
        # RESTRICTS THE NUMBER OF FILES DELETED TO BE LESS THAN THE NUMBER OF FILES ADDED (IN EACH TIMESTEP)
        limitPerTimestep = list(np.cumsum(timelineComponents[FILES_ADDED].getResults()))
    elif component == FILES_CHANGED: 
        # RESTRICTS THE NUMBER OF FILES CHANGED TO BE LESS THAN THE NUMBER OF FILES ADDED LESS
        # THE NUMBER OF FILES DELETED (IN EACH TIMESTEP)
        limitPerTimestep = []
        addedCumsum = np.cumsum(timelineComponents[FILES_ADDED].getResults())
        deletedCumsum = np.cumsum(timelineComponents[FILES_DELETED].getResults())
        deletedPerTimestep = timelineComponents[FILES_DELETED].getResults()
        for i in range(len(timelineComponents[FILES_ADDED].getResults()) - 1):
            limitPerTimestep += [addedCumsum[i] - deletedCumsum[i] - deletedPerTimestep[i+1]]

    return limitPerTimestep

def createDateSequence(timelineComponents):
    
    numberOfCommits = timelineComponents[COMMITS].getTotal()
    dateDiffsDist = timelineComponents[DATES].getDist()
    repoTime = timelineComponents[DATES].getTotal()
    firstDate = datetime.now()
    
    if dateDiffsDist == UNIF_DIST:
        meanDateDiff = repoTime / numberOfCommits

        generatedDates = [firstDate]
        while(len(generatedDates) < numberOfCommits):
            generatedDates += [generatedDates[-1] + timedelta(seconds=meanDateDiff)]

    elif dateDiffsDist == EXP_DIST or dateDiffsDist == PL_DIST:
        sequence = list(constroyPowerOrExponentialSequence(
            objectiveDist=dateDiffsDist, 
            seqSum=int(sum(repoTime) / 60), 
            seqSize=numberOfCommits, 
            saveInCache=True, 
            nearValue=True)
        )
        
        generatedDates = [firstDate]
        while(len(generatedDates) < numberOfCommits):
            nextDiff = int(sequence.pop(0) * 60) 
            generatedDates += [generatedDates[-1] + timedelta(seconds=nextDiff)]

    else:
        print("Wrong data for dateTimeDist: {}".format(dateDiffsDist))
        return -1
    
    timelineComponents[DATES].setResults(generatedDates)

    return timelineComponents

def verifyRestrictions(timelineComponents: dict[str, Component]):
    numberOfCommits = timelineComponents[COMMITS].getTotal()

    # verify if every commit made some change
    interactionsPerCommit = []
    for i in range(numberOfCommits):
        interactionsPerCommit += [
            timelineComponents[FILES_ADDED].getResultForCommit(i) + \
            timelineComponents[FILES_DELETED].getResultForCommit(i) + \
            timelineComponents[FILES_CHANGED].getResultForCommit(i)]
    for e in interactionsPerCommit:
       assert(e > 0)

    filesPerCommit = np.cumsum(timelineComponents[FILES_ADDED].getResults()) - np.cumsum(timelineComponents[FILES_DELETED].getResults())
    deletesPerCommit = timelineComponents[FILES_DELETED].getResults()
    changesPerCommit = timelineComponents[FILES_CHANGED].getResults()
    for i in range(len(filesPerCommit) - 1):
        assert(filesPerCommit[i] > 0)
        assert(filesPerCommit[i] - changesPerCommit[i+1] >= 0)
        assert(filesPerCommit[i] - deletesPerCommit[i+1] > 0)
        assert(filesPerCommit[i] - deletesPerCommit[i+1] - changesPerCommit[i+1] >= 0)