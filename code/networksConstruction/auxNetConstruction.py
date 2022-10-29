import datetime as dt

from constants import *
import variables as var

def developerShouldBeIgnored(author, codebase):
    return codebase in var.DEVELOPERS_TO_IGNORE and author in var.DEVELOPERS_TO_IGNORE[codebase]

# ----------------
# READING RAW DATA

def getCommitAndFileInfo(line: str):
    sLine = line[:-1].rsplit(',')
    return sLine[0], sLine[1], sLine[2], sLine[3], dt.datetime.strptime(sLine[4], "%c"), sLine[5], sLine[6]

def lineRelatedWithMethod(line: str):
    return line.startswith("#")

# ----
# ITEM

def isItemDeleted(itemName: str, fileOrMethod):
    if fileOrMethod == FILE_TYPE:
        return itemName.startswith("{}_".format(DELETED_ITEM))
    elif fileOrMethod == METHOD_TYPE:
        return itemName.split("...")[1].startswith("{}_".format(DELETED_ITEM))

def getItemNameIfEliminated(previousName, numberOfEliminations, fileOrMethod, fileName = None):
    if fileOrMethod == FILE_TYPE:
        return '{}_{}_{}'.format(DELETED_ITEM, numberOfEliminations, previousName)
    elif fileOrMethod == METHOD_TYPE:
        return '{}...{}_{}_{}'.format(fileName, DELETED_ITEM, numberOfEliminations, previousName)

# -------
# METHODS

def createTotalMethodName(fileName, methodName):
    return '{}...{}'.format(fileName, methodName)

def getPartsOfTotalMethodName(totalMethod):
    sMethod = totalMethod.split("...")
    return sMethod[0], sMethod[1]

def isMethodFromFile(methodName, fileName):
    return getPartsOfTotalMethodName(methodName)[0] == fileName

def getMethodName(totalMethodName):
    return getPartsOfTotalMethodName(totalMethodName)[1]

def prefixMethodNamesWithFileName(line, file):
    methodBefore, methodAfter = line[2:-1].split(';;;') # The ;;; divides the update of the method
    return createTotalMethodName(file, methodBefore), createTotalMethodName(file, methodAfter) # Methods are named considering their file