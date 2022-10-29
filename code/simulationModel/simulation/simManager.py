import os
from copy import deepcopy

from constants import *
import variables as var
from utils.pathClass import simulationPathsManager

from utils.auxiliaryFunctions import getFileOfSubdirsInDir, createDir, createDirRec, getStructInFile

import simulationModel.simulation.generateTimeline.main as tlGen
import simulationModel.simulation.simulateTimeline.main as tlSim

def fromHypNameToChRule(hypName):
    sPath = hypName.split("_")
    
    if sPath[1] == "-":
        a = 0
        alpha = 0
    else:
        a = float(sPath[1])
        if a.is_integer():
            a = int(a)
        alpha = 1

    return {
        A: a, \
        ALPHA: alpha, \
    }

def fromChRuleToHypName(params):
    if params[ALPHA] == 0:
        hypothesisName = "-"
    else:
        hypothesisName = params[A]
    return 'hypothesis_{}'.format(hypothesisName)

class SimManager:
    def __init__(self, codebase):
        self.cbaGetter: codeBaseAttributes = codeBaseAttributes(codebase)
        self.distsGetter: Distributions = Distributions()
        self.inputChecker: InputChecker = InputChecker()
        self.simulationsToRun = []

    def runSimulations(self):
        self.getSimulationInputs()

        while(self.simulationsToRun != []):
            cba, dists, spDist = self.getNextSimInput()
            self.simulate(cba, dists, spDist)

    def getSimulationInputs(self):
        self.cbaSet = self.cbaGetter.getCodebaseAttributes()
        self.distsSet = self.distsGetter.getDistributions()
        self.h_k_Set = self.getChangeRules()
        for cba in self.cbaSet:
            for dists in self.distsSet:
                for h_k in self.h_k_Set:
                    self.simulationsToRun += [{CA: cba, DISTS: dists, CH_R: h_k}]
    
    def simulate(self, cba, dists, chR):
        timeline = tlGen.generateTimeline(cba, dists)
        if timeline != -1:
            paths: simulationPathsManager = var.variablesDict[PATHS]
            paths.buildHypothesisPaths(fromChRuleToHypName(chR))
            tlSim.simulateTimeline(timeline, dists, chR, fromChRuleToHypName(chR))

            if not REAL_CODE_BASE in cba:
                f = open(paths.getTheoCodeBaseInfo(), "w", encoding="utf-8")
                for k, v in cba.items():
                    f.write('{}: {}\n'.format(k, v))
                f.close()

    def getNextSimInput(self):
        if len(self.simulationsToRun) == 0:
            return -1, -1
        nextSim = self.simulationsToRun.pop(0)
        nextSim[CA] = self.inputChecker.checkCBA(nextSim[CA])
        nextSim[DISTS] = self.inputChecker.checkDists(nextSim[DISTS])

        return nextSim[CA], nextSim[DISTS], nextSim[CH_R]

    def getChangeRules(self):
        changeRulesSet = [{A: 0, \
            ALPHA: 0}]

        initialAttractSet = var.INITIAL_ACTRACTIVENESS_SET
        alphaSet = var.ATTRACTIVENESS_ALPHA

        for initialAttract in initialAttractSet:
            for alpha in alphaSet:
                changeRulesSet += [{A: initialAttract, \
                    ALPHA: alpha}]
        
        return changeRulesSet

class codeBaseAttributes:
    def __init__(self, codebase=None):
        self.realReposCBAttrCache = {}
        self.codebase = codebase
        pass

    def getCodebaseAttributes(self):
        if self.codebase != None:
            return self.getRealCodebaseAttributes()
        else:
            return self.formulateCBAttrsToAnalyze()
    
    def getRealCodebaseAttributes(self):
        cb = self.codebase
        if cb in self.realReposCBAttrCache.keys():
            return [deepcopy(self.realReposCBAttrCache[cb])]

        cbPath = '{}/{}/empiricalTimeline.pickle'.format(RESULTSDIR, cb.split("/")[1])
        empData, _ = getStructInFile(cbPath).getCAForSimulation()

        cbAttrs = {
            NOD    : len(empData[COMMITS_PER_DEV].keys()),   # number of developers
            NOC    : sum(empData[COMMITS_PER_DEV].values()), # number of commits
            F_ADD  : sum(empData[FILES_ADDED_UNTIL_T]),   # total files added
            F_CH   : sum(empData[FILES_CHANGED_UNTIL_T]), # total files changed
            F_DEL  : sum(empData[FILES_DELETED_UNTIL_T]), # total files deleted
            CB_DUR : (empData[DATE_DIFF_PER_T][-1] - empData[DATE_DIFF_PER_T][0]).total_seconds(), # codebase duration
            P_C_ADD: empData[P_C_ADD], # percentage of commits with more than zero files added
            P_C_CH : empData[P_C_CH],  # percentage of commits with more than zero files changed
            P_C_DEL: empData[P_C_DEL], # percentage of commits with more than zero files deleted
            REAL_CODE_BASE: cb
        }
        self.realReposCBAttrCache[cb] = cbAttrs
        return [deepcopy(cbAttrs)]

    def formulateCBAttrsToAnalyze(self):
        codeBaseAttributesSet = []
        codeBaseAttributesSet += [var.DEFAULT_CODEBASE_ATTRIBUTES]

        validCBAttrs = []
        for cbA in codeBaseAttributesSet:
            if REAL_CODE_BASE in cbA and cbA != self.getRealCodebaseAttributes(cbA[REAL_CODE_BASE]):
                del cbA[REAL_CODE_BASE]
            if self.cbAttrCompliesWithRestrictions(cbA):
                validCBAttrs += [cbA]
        
        return validCBAttrs
    
    def cbAttrCompliesWithRestrictions(self, cbAttr):
        if cbAttr[F_ADD] < cbAttr[F_DEL]:
            print("Can't simulate code base: fAdd < fDel")
            return False
        elif cbAttr[NOD] < 5:
            print("Can't simulate code base: Small number of developers (nod < 5)")
            return False
        elif cbAttr[NOC] < 5:
            print("Can't simulate code base: Small number of commits (noc < 5)")
            return False
        elif cbAttr[NOC] > cbAttr[F_ADD] + cbAttr[F_DEL] + cbAttr[F_CH]:
            print("Can't simulate code base: Not enough operations for all commits (noc > fAdd + fDel + fCh)")
            return False
        return True

class Distributions:
    def __init__(self):
        pass

    def getDistributions(self):
        if var.COPY:
            return self.copyDistsFromOtherCodebase()
        else:
            distributionsSet = []
            distributionsSet += [var.DISTRIBUTIONS]

            # HERE CAN BE MODIFIED TO ANALYSE MORE DISTRIBUTIONS 

            return distributionsSet

    def copyDistsFromOtherCodebase(self):
        cbToCopyDistFrom = var.REPO_TO_COPY_FROM
        pathToCopyFrom = '{}/{}/simulations;MC_{}/'.format(RESULTSDIR, cbToCopyDistFrom.split("/")[1], var.MAX_MONTHS_COLLAB)
        createDirRec(pathToCopyFrom)
        return getFileOfSubdirsInDir(pathToCopyFrom, DISTS_INFO_FILE)

class InputChecker():
    def __init__(self):
        pass

    def checkCBA(self, cba):
        paths: simulationPathsManager = var.variablesDict[PATHS]
        if REAL_CODE_BASE in cba:
            paths.codebaseAttributesPaths(cba[REAL_CODE_BASE], None)
        else:
            theoCodeBasesPath = RESULTSDIR + "/" + THEOCODEBASES
            createDirRec(theoCodeBasesPath)
            
            cba = self.verifyIfSetOfParamsExist(cba, len(os.listdir(theoCodeBasesPath)) + 1, theoCodeBasesPath, fileName=CBATTRS_INFO_FILE)
            paths.codebaseAttributesPaths(None, cba[PARAMS_ID])

        return cba

    def verifyIfSetOfParamsExist(self, params, parametersId, pathForGenNullModels, fileName):
        existentParamsSet = getFileOfSubdirsInDir(pathForGenNullModels, fileName)

        for exParams in existentParamsSet:
            paramsNumber = exParams[PARAMS_ID]
            del exParams[PARAMS_ID]
            if params == exParams:
                params[PARAMS_ID] = paramsNumber
                break
        
        if PARAMS_ID not in params:
            params[PARAMS_ID] = parametersId

        return params

    def checkDists(self, dists):
        paths: simulationPathsManager = var.variablesDict[PATHS]

        id = self.getIdForNextSimulation()
        dists = self.verifyIfSetOfParamsExist(dists, id, paths.getGenModelDir(), fileName=DISTS_INFO_FILE)

        paths.buildDistsPaths(dists[PARAMS_ID])
        
        return dists
    
    def getIdForNextSimulation(self):
        paths: simulationPathsManager = var.variablesDict[PATHS]
        parametersId = 1

        while(True):
            networksPathForRepo = "{}/dists_{}/networks".format(paths.getGenModelDir(), parametersId)
            if not os.path.exists(networksPathForRepo):
                break
            
            parametersId += 1

        return parametersId