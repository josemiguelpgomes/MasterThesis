import pytz
utc = pytz.UTC

import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta

from pydriller import Repository

from constants import *
import variables as var
from utils.pathClass import dataMiningPathsManager

def fileDataToTxt(commitHash, commitAuthorName, commitAuthorEmail, oldFilePath, newFilePath, commitDate, fileLines, fileComplexity):
    return '{},{};{},{},{},{},{},{}\n'.format(
        commitHash, commitAuthorName.replace(",", ""), commitAuthorEmail.replace(",", ""), \
        oldFilePath.replace(",", ""), newFilePath.replace(",", ""), commitDate, fileLines, fileComplexity
    )

def functionDataToTxt(oldFuncName, newFuncName):
    return '# {};;;{}\n'.format(oldFuncName, newFuncName)

def sortFileElemsByDate(repoFile):
    f = open(repoFile, "r", encoding='utf-8')
    lines = f.readlines()

    data = {}

    fileChange = {}
    date = None
    for line in lines: 
        if line.startswith("#"):
            fileChange["methodsInfo"] += '{}'.format(line)
        else:
            if date != None:
                if date in data.keys():
                    data[date] += [fileChange]
                else:
                    data = data | {date: [fileChange]}

            sLine = line.rsplit(',')
            date = datetime.strptime(sLine[4], "%c") # datePos is 4
            fileChange = {"fileInfo": '{}'.format(line), "methodsInfo": ""}
            
    if date in data.keys():
        data[date] += [fileChange]
    else:
        data = data | {date: [fileChange]}
    f.close()

    data = {k: v for k, v in sorted(list(data.items()))}

    f = open(repoFile, "w", encoding="utf-8")
    for fileChangesPerDate in data.values():
        for fileChange in fileChangesPerDate:
            f.write(fileChange["fileInfo"])
            f.write(fileChange["methodsInfo"])
    f.close()

def methodAnalysis(fileToWriteResults, methodsBefore, methodsAfter, methodsChanged):
    methodsNamesAfter = list(map(lambda x: x.name, methodsAfter)) if len(methodsAfter) > 0 else []
    methodsNamesBefore = list(map(lambda x: x.name, methodsBefore)) if len(methodsBefore) > 0 else []
    changedNamesMethods = list(map(lambda x: x.name, methodsChanged)) if len(methodsChanged) > 0 else []

    for chM in changedNamesMethods:
        if chM in methodsNamesBefore and chM in methodsNamesAfter:
            fileToWriteResults.write(functionDataToTxt(chM, chM))
        elif chM in methodsNamesBefore:
            fileToWriteResults.write(functionDataToTxt(chM, None))
        elif chM in methodsNamesAfter:
            fileToWriteResults.write(functionDataToTxt(None, chM))

if __name__ == "__main__":
    var.initVariablesDict()
    paths = var.variablesDict[PATHS] = dataMiningPathsManager(sys.argv[1])

    firstCommitDate = None
    for commit in Repository(paths.codebaseURL()).traverse_commits():
        if firstCommitDate == None:
            firstCommitDate = commit.author_date
            break

    f = open(paths.getPathToStoreCodeRawData(), "w", encoding="utf-8")
    actualCommitNumber = 0
    while firstCommitDate < utc.localize(datetime.now()):
        for commit in Repository(paths.codebaseURL(), since=firstCommitDate, to=(firstCommitDate + relativedelta(years=1)), only_no_merge=True).traverse_commits():
            for file in commit.modified_files:
                fileOldPath = file.old_path if file.old_path != None else NON_EXISTENT_ITEM
                fileNewPath = file.new_path if file.new_path != None else NON_EXISTENT_ITEM
                fileLines = file.nloc if file.nloc != None else 0
                fileComplexity = file.complexity if file.complexity != None else 0

                f.write(
                    fileDataToTxt(commit.hash, commit.author.name, commit.author.email, \
                        fileOldPath, fileNewPath, commit.author_date.ctime(), fileLines, fileComplexity)
                )
                
                methodAnalysis(f, file.methods_before, file.methods, file.changed_methods)
                        
            actualCommitNumber += 1

        firstCommitDate = (firstCommitDate + relativedelta(years=1))

    f.close()
    sortFileElemsByDate(paths.getPathToStoreCodeRawData())
    
    f = open(paths.getPathToStoreMiningProcessResults(), "w", encoding="utf-8")
    f.write("Commits analyzed: {}".format(actualCommitNumber))
    f.close()
