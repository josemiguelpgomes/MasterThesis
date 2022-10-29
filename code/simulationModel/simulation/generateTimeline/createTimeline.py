import numpy.random as nprandom
from random import random

import variables as var
from constants import *

from utils.auxiliaryFunctions import normalize
from utils.timelineClass import Timeline
import variables as var
from simulationModel.simulation.generateTimeline.componentGeneration import Component

COMMITS_TO_DO = "commitsToDo"
COMMITS_DONE = "numberOfCommitsDone"

def createTimelineOfCommits(timelineComponents):
    generatedTimeline = Timeline()

    distributions = var.variablesDict[DISTS]
    selectAuthorRule = distributions[SEL_C_AUTHOR]
    
    # get generated sequences
    commitsComp: Component = timelineComponents[COMMITS]
    numberOfCommits = commitsComp.getTotal()
    numberOfDevs = commitsComp.getCLen()
    generatedCommitsPerDev = commitsComp.getResults()

    datesComp: Component = timelineComponents[DATES]
    generatedDates = datesComp.getResults()

    generatedFilesAdded = timelineComponents[FILES_ADDED].getResults()
    generatedFilesDeleted = timelineComponents[FILES_DELETED].getResults()
    generatedFilesChanged = timelineComponents[FILES_CHANGED].getResults()
    
    # create timeline
    commitsPerDev = {} # key: dev; val: number of commits
    for i in range(1, len(generatedCommitsPerDev) + 1):
        commitsPerDev[i] = {COMMITS_TO_DO: generatedCommitsPerDev[i-1], COMMITS_DONE: 0}
        
    developersThatCommittedUntilTimeT = {}

    commitId = 1
    totalCommitsToDo = sum(list(map(lambda d: d[COMMITS_TO_DO], commitsPerDev.values())))
    while(totalCommitsToDo != 0):

        if selectAuthorRule == RANDOM:
            dev = nprandom.choice(list(commitsPerDev.keys()))
        
        elif selectAuthorRule == COMPLEX_RULE: # does not require knowledge of the future
            dev, commitsPerDev, developersThatCommittedUntilTimeT = selCAuthor_thirdIteration(
                numberOfDevs=numberOfDevs,
                numberOfCommits=numberOfCommits,
                devsThatHaveCommittedUntilT=developersThatCommittedUntilTimeT,
                commitsPerDev=commitsPerDev
            )

        if commitsPerDev[dev][COMMITS_TO_DO] == 1:
            del commitsPerDev[dev]
        else:
            commitsPerDev[dev][COMMITS_TO_DO] -= 1
        
        multiplierFilesAdded = var.variablesDict[DISTS][MULTIPLIER_FILES_ADDED] 
        generatedTimeline.setCommitInfo(
            fileOrMethod = FILE_TYPE,
            commitId = commitId,
            author   = dev, 
            date     = generatedDates[0],
            changes  = generatedFilesChanged[0],
            adds     = generatedFilesAdded[0] * multiplierFilesAdded,
            removes  = generatedFilesDeleted[0]
        )
        del generatedDates[0], generatedFilesChanged[0], generatedFilesAdded[0], generatedFilesDeleted[0]

        commitId += 1
        totalCommitsToDo -= 1
    
    generatedTimeline.setDevsNumber(numberOfDevs)
    generatedTimeline.setDistsForGenTimeline(distributions)
    assert(len(generatedDates) == 0 and len(generatedFilesChanged) == 0 and len(generatedFilesAdded) == 0 and \
        len(generatedFilesDeleted) == 0)
        
    return generatedTimeline

def selCAuthor_thirdIteration(numberOfDevs, numberOfCommits, \
    devsThatHaveCommittedUntilT, commitsPerDev): # FOR MORE INFORMATION, READ THE PAPER

    developerToBeChosenToStartToCommit = var.variablesDict[DISTS][RULE_CHOOSE_DEV_TO_START_TO_COMMIT]

    if len(devsThatHaveCommittedUntilT.keys()) == 0:
        if developerToBeChosenToStartToCommit == RANDOM:
            developersWithoutCommits = list(set(commitsPerDev.keys()) - set(devsThatHaveCommittedUntilT.keys()))
            dev = nprandom.choice(developersWithoutCommits)

        elif developerToBeChosenToStartToCommit == PROPORTIONAL_COMMITS_TO_DO:
            dev = nprandom.choice(list(commitsPerDev.keys()), \
                p = normalize(
                    list(map(lambda x: x[COMMITS_TO_DO], 
                        list(commitsPerDev.values()))))
            )
        devsThatHaveCommittedUntilT[dev] = 1
    
    allDevelopersCommitedAtleastOnce = False 
    if len(devsThatHaveCommittedUntilT.keys()) == numberOfDevs:
        allDevelopersCommitedAtleastOnce = True

    # decides if a new developer should commit 
    addNewDeveloper = False
    if not allDevelopersCommitedAtleastOnce:
        nrDevsThatHaveCommittedAndHaveCommitsToDo = \
            len(list(filter(lambda x: x in commitsPerDev.keys(), devsThatHaveCommittedUntilT.keys())))
        
        if nrDevsThatHaveCommittedAndHaveCommitsToDo == 0 or \
            random() < (numberOfDevs / numberOfCommits):
            addNewDeveloper = True

    if not allDevelopersCommitedAtleastOnce and addNewDeveloper:
        if developerToBeChosenToStartToCommit == RANDOM:
            devsThatHaventCommittedYet = list(set(list(commitsPerDev.keys())) - set(devsThatHaveCommittedUntilT.keys()))
            dev = nprandom.choice(devsThatHaventCommittedYet)
            
        elif developerToBeChosenToStartToCommit == PROPORTIONAL_COMMITS_TO_DO:
            commitsPerDevWithoutCommits = {k: v[COMMITS_TO_DO] for k, v in commitsPerDev.items() if k not in devsThatHaveCommittedUntilT.keys()}
            normalizedCommits = normalize(commitsPerDevWithoutCommits.values()) 
            dev = nprandom.choice(list(commitsPerDevWithoutCommits.keys()), p=normalizedCommits)

        devsThatHaveCommittedUntilT[dev] = 1
    else:
        devsWithCommitsToDo = list(filter(lambda x: x in commitsPerDev.keys(), devsThatHaveCommittedUntilT.keys()))

        developerToBeChosenToCommit = var.variablesDict[DISTS][RULE_CHOOSE_DEV_TO_COMMIT]
        if developerToBeChosenToCommit == RANDOM:
            commitsDoneUntilT = {k: commitsPerDev[k][COMMITS_TO_DO] for k in devsWithCommitsToDo} 
            dev = nprandom.choice(list(commitsDoneUntilT.keys()))

        elif developerToBeChosenToCommit == PROPORTIONAL_COMMITS_DONE:
            commitsDoneUntilT = {k: commitsPerDev[k][COMMITS_DONE] for k in devsWithCommitsToDo} 
            dev = nprandom.choice(list(commitsDoneUntilT.keys()), p=normalize(commitsDoneUntilT.values()))
        
        elif developerToBeChosenToCommit == PROPORTIONAL_COMMITS_TO_DO:
            commitsDoneUntilT = {k: commitsPerDev[k][COMMITS_TO_DO] for k in devsWithCommitsToDo}
            dev = nprandom.choice(list(commitsDoneUntilT.keys()), p=normalize(commitsDoneUntilT.values()))

    commitsPerDev[dev][COMMITS_DONE] += 1

    return dev, commitsPerDev, devsThatHaveCommittedUntilT