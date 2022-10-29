import functools
import numpy as np
from math import floor, ceil
from random import random
import numpy as np

from constants import * 

from utils.auxiliaryFunctions import createDir, getStructInFile, saveStructInFile

def constroyUniformSequence(seqMean, seqLength, seqSum, limitPerI=None, attrib=None):
    sequence = []
    cumSum = 0
    numberOfMeanCeil = ceil((seqMean - floor(seqMean)) * seqLength)
    while (len(sequence) < seqLength):
        if limitPerI != None:
            if attrib == FILES_DELETED: 
                # in case of deletions, it can't delete more than 
                # the number of files added
                if len(sequence) == 0:
                    totalAddsUntilThatPoint = 1
                else:
                    totalAddsUntilThatPoint = limitPerI[len(sequence) - 1]

                if totalAddsUntilThatPoint <= cumSum + ceil(seqMean):
                    sequence += [0]
                    seqMean = (seqSum - cumSum) / ( seqLength - len(sequence))
                    numberOfMeanCeil = ceil((seqMean - floor(seqMean)) * (seqLength - len(sequence)))
                    continue

            elif attrib == FILES_CHANGED: 
                # in case of changes, it can't change more than the number of files
                # added less the number of files deleted, which is the difference.
                if len(sequence) == 0:
                    totalExistingFiles = 0
                else:
                    totalExistingFiles = limitPerI[len(sequence) - 1]
                if totalExistingFiles < ceil(seqMean):
                    sequence += [0]
                    seqMean = (seqSum - cumSum) / ( seqLength - len(sequence))
                    numberOfMeanCeil = ceil((seqMean - floor(seqMean)) * (seqLength - len(sequence)))
                    continue

        if numberOfMeanCeil == 0:
            sequence += [floor(seqMean)]
        else:
            probabilityOfCeil = numberOfMeanCeil / (seqLength - len(sequence))
            
            if random() < probabilityOfCeil: # 1, 2, 2, 2
                sequence += [ceil(seqMean)]
                numberOfMeanCeil -= 1
            else:
                sequence += [floor(seqMean)]
            
        cumSum += sequence[-1]

    i = -1
    while(seqSum > sum(sequence)):
        if limitPerI != None:
            if attrib == FILES_DELETED:
                if int(np.cumsum(sequence)[i]) + 1 >= limitPerI[i - 1]:
                    i -= 1
                    continue
                else:
                    sequence[i] += 1
            elif attrib == FILES_CHANGED:
                if sequence[i] + 1 > limitPerI[i-1]:
                    i -= 1
                    continue
                else:
                    sequence[i] += 1
        else:
            sequence[i] += 1
        
        i -= 1

    i = -1
    while(seqSum < sum(sequence)):
        if sequence[i] != 0:
            sequence[i] -= 1
        i -= 1

    return sequence

def constroyPowerOrExponentialSequence(objectiveDist, seqSum, seqSize, saveInCache, nearValue=False, seeCache=True): # size << commits
    createDir("simulationModel/caches")
    
    # get cache
    if objectiveDist == EXP_DIST: # CACHE STRUCTURE: {size: {sum1: lambda, sum2: lambda}, size2: {sum1: lambda, sum2: lambda} }
        cachePath = "simulationModel/caches/expCache.pkl"
        cache = getStructInFile(cachePath)
        scale = 1

    elif objectiveDist == PL_DIST:
        cachePath = "simulationModel/caches/plCache.pkl"
        cache = getStructInFile(cachePath)
        alpha = 1.1
    
    # verify if exist in cache
    if seeCache:
        if seqSize in cache.keys():
            if nearValue:
                for k in cache[seqSize].keys():
                    if k > seqSum * 0.99 and k < seqSum:
                        return cache[seqSize][k]
            else:
                if seqSum in cache[seqSize].keys():
                    return cache[seqSize][seqSum]
        else:
            cache[seqSize] = {}
    
    actualSum, steps, found = -1, 0, False
    while True:
        sumSet = []
        countSumsTooFar = 0
        while steps < 10000:
            if objectiveDist == EXP_DIST: 
                sequence = list(map(lambda x: ceil(x), np.random.exponential(scale=scale, size=seqSize)))
            elif objectiveDist == PL_DIST:
                sequence = np.random.zipf(a=alpha, size=seqSize)

            # verify value
            actualSum = functools.reduce(lambda x, y: x+y, sequence)
            if nearValue:
                if actualSum > seqSum * 0.99 and actualSum < seqSum and max(sequence) < seqSum / 4:
                    found = True
                    break
            else:
                if actualSum == seqSum and max(sequence) < seqSum / 4:
                    found = True
                    break
                
            # heuristic to verify if it is too far away
            if (actualSum < 0 or seqSum / actualSum > 1.01 or seqSum / actualSum < 0.99):
                if actualSum < 0 or countSumsTooFar == 200:
                    sumSet += [actualSum]
                    countSumsTooFar = 0
                    break
                elif actualSum / seqSum > 1.01 or actualSum / seqSum < 0.99:
                    countSumsTooFar += 1

            steps += 1
            sumSet += [actualSum]

        if found:
            break
        
        # update values to reach sequence
        steps = 0
        if objectiveDist == EXP_DIST:
            if np.mean(sumSet) > seqSum and scale - 0.1 >= 0:
                scale -= 0.1
            else:
                scale += 0.5
        elif objectiveDist == PL_DIST:
            if len(list(filter(lambda x: x < 0, sumSet))) > 0 or np.mean(sumSet) > seqSum:
                alpha += 0.005
            else:
                nextReduction = np.random.random() * 0.001
                if alpha - nextReduction <= 1.1:
                    alpha -= (alpha - 1.1) / 2
                else:
                    alpha -= nextReduction

    if saveInCache:
        cache[seqSize][actualSum] = sequence
        saveStructInFile(cache, cachePath)
        
    return sequence