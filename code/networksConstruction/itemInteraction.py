from constants import *
import variables as var

from utils.networksClasses import Network

from networksConstruction.commit import Commit
from networksConstruction.networksManager import NetworksManager
from networksConstruction.auxNetConstruction import isMethodFromFile, createTotalMethodName, getItemNameIfEliminated, \
    getPartsOfTotalMethodName

def interactionWithItem(fileOrMethod, itemOldPath, itemNewPath: str, commit: Commit, nloc=None, cyclicComplexity=None):
    if itemNewPath.endswith(NON_EXISTENT_ITEM):
        itemNewPath = deleteItem(fileOrMethod, itemOldPath, commit)
        if itemNewPath == -1:
            return -1

        if fileOrMethod == FILE_TYPE:
            deleteMethodsFromFile(itemNewPath, commit)
    elif itemOldPath.endswith(NON_EXISTENT_ITEM):
        createItem(fileOrMethod, itemNewPath, nloc, cyclicComplexity)
    elif itemNewPath != itemOldPath:
        changeItem(fileOrMethod, itemOldPath, itemNewPath, commit)
    
    if fileOrMethod == FILE_TYPE:
        commit.addFileToCommit(itemNewPath)
    elif fileOrMethod == METHOD_TYPE:
        commit.addMethodToCommit(itemNewPath)

def createItem(fileOrMethod, itemPath, nloc=None, comp=None):
    nm: NetworksManager = var.variablesDict[NET_MANAGER]
    n: Network
    if fileOrMethod == FILE_TYPE:
        for n in nm.getAllNetworksOfType(fileOrMethod, D2I):
            n.addNode(itemPath, type=fileOrMethod, otherAttribs={ITEM_DATES: [], ITEM_NLOC: nloc, ITEM_CC: comp})
    elif fileOrMethod == METHOD_TYPE:
        for n in nm.getAllNetworksOfType(fileOrMethod, D2I):
            n.addNode(itemPath, type=fileOrMethod, otherAttribs={ITEM_DATES: []})

def changeItem(fileOrMethod, itemOldPath, itemNewPath, commit):
    nm: NetworksManager = var.variablesDict[NET_MANAGER]
    d2inets: list[Network] = nm.getAllNetworksOfType(fileOrMethod, D2I)
    i2inets: list[Network] = nm.getAllNetworksOfType(fileOrMethod, I2I)

    if itemNewPath in d2inets[0].getNodes():
        deleteItem(fileOrMethod, itemNewPath, commit)

    for net in d2inets + i2inets:
        net: Network
        net.relabelNodes({itemOldPath: itemNewPath}, copy=False)

    if fileOrMethod == FILE_TYPE: # Change the file name in the methods that made a reference to it
        d2mnet: Network = nm.getNet(METHOD_TYPE, D2I)
        methods = d2mnet.getMethodNodes()
        methodsFromFile = list(filter(lambda m: isMethodFromFile(m, itemOldPath), methods))
        for mff in methodsFromFile:
            newName = createTotalMethodName(itemNewPath, getPartsOfTotalMethodName(mff)[1])
            interactionWithItem(METHOD_TYPE, mff, newName, commit)

def deleteItem(fileOrMethod, itemOldPath, commit):
    nm: NetworksManager = var.variablesDict[NET_MANAGER]
    d2inets: list[Network] = nm.getAllNetworksOfType(fileOrMethod, D2I)
    i2inets: list[Network] = nm.getAllNetworksOfType(fileOrMethod, I2I)

    if itemOldPath not in d2inets[0].getNodes():
        return -1
    else:
        if d2inets[0].degreeOfNode(itemOldPath) == 0:
            for n in d2inets + i2inets:
                n.removeNode(itemOldPath)

    for i in range(1, 10000):
        if fileOrMethod == FILE_TYPE:
            itemNewPath = getItemNameIfEliminated(itemOldPath, i, fileOrMethod)
        elif fileOrMethod == METHOD_TYPE:
            fileName, methodName = getPartsOfTotalMethodName(itemOldPath)
            itemNewPath = getItemNameIfEliminated(methodName, i, fileOrMethod, fileName)
            
        if itemNewPath not in d2inets[0].getNodes():
            for n in d2inets + i2inets:
                n.relabelNodes({itemOldPath: itemNewPath}, copy=False)

            if fileOrMethod == FILE_TYPE: # Change the file name in the methods that made a reference to it
                d2mnet: Network = nm.getNet(METHOD_TYPE, D2I)
                methodsNetNodes = d2mnet.getMethodNodes()
                methodsFromFile = list(filter(lambda m: isMethodFromFile(m, itemOldPath), methodsNetNodes))
                for oldMethodName in methodsFromFile:
                    newMethodName = createTotalMethodName(itemNewPath, getPartsOfTotalMethodName(oldMethodName)[1])
                    interactionWithItem(METHOD_TYPE, oldMethodName, newMethodName, commit)

            newItemPath = itemNewPath
            break
            
    if i == 10000:
        print("ERROR... AN ITEM WITH THE SAME NAME WAS ELIMINATED 10000 TIMES...")
        exit(-1)

    return newItemPath

def deleteMethodsFromFile(filePath, commit: Commit):
    nm: NetworksManager = var.variablesDict[NET_MANAGER]
    f2fnets = nm.getAllNetworksOfType(METHOD_TYPE, I2I)
    for n in f2fnets:
        n: Network
        methodsNetNodes = n.getNodes()
        methodsFromFile = list(filter(lambda m: isMethodFromFile(m, filePath), methodsNetNodes))
        for mff in methodsFromFile:
            newMethodPath = deleteItem(METHOD_TYPE, mff, commit)
            if newMethodPath == -1:
                continue
            
            commit.addMethodToCommit(newMethodPath)