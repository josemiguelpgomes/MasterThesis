from constants import *
import variables as var
from utils.pathClass import simulationPathsManager

from utils.auxiliaryFunctions import doesPathExist, getStructInFile, createDirRec, saveStructInFile

from simulationModel.simulation.generateTimeline.componentCharacteristics import getComponentsCharacteristics
from simulationModel.simulation.generateTimeline.componentGeneration import createEachComponentOverTime
from simulationModel.simulation.generateTimeline.createTimeline import createTimelineOfCommits
from utils.timelinesAnalysis import timelineComparison

def generateTimeline(cba, dists):
    # verify if timeline is already created, else creates, analyzes and saves it
    paths: simulationPathsManager = var.variablesDict[PATHS]
    var.variablesDict[DISTS] = dists

    if doesPathExist(paths.getGenTimeLine()):
        if REAL_CODE_BASE in cba: # TODO delete
            timelineComparison(BOTH_TL)
        else:
            timelineComparison(THEO)
        return getStructInFile(paths.getGenTimeLine())
    else:
        timeline = detailTimeline(cba)
        
        createDirRec(paths.getGenNetworksDir())
        saveStructInFile(timeline, paths.getGenTimeLine())

        # comparisons between the generated timeline and empirical timeline
        if REAL_CODE_BASE in cba:
            whichTimelinesToGet = BOTH_TL
        else:
            whichTimelinesToGet = THEO
        timelineComparison(whichTimelinesToGet)

        return timeline

def detailTimeline(cba):
    timelineComponents = getComponentsCharacteristics(cba)
    if timelineComponents == -1:
        return
    timelineParts = createEachComponentOverTime(timelineComponents)
    return createTimelineOfCommits(timelineParts)