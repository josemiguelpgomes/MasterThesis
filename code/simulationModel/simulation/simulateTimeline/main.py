from datetime import datetime
import multiprocessing as mp
import networkx as nx
from math import ceil

from constants import *
import variables as var

from utils.pathClass import simulationPathsManager
from utils.auxiliaryFunctions import saveStructInFile, removeDir, doesPathExist, getItemsInDir

from simulationModel.simulation.simulateTimeline.simulation import Simulation
from simulationModel.simulation.simulateTimeline.classes import Developer, File, Context

def simulateTimeline(timeline, dists, chDist, hypName):
    paths: simulationPathsManager = var.variablesDict[PATHS]

    hypPath = paths.getHypothesisNetsDir()
    if doesPathExist(hypPath) and len(getItemsInDir(hypPath)) in [2 * var.NUMBER_OF_NETWORKS, 3 * var.NUMBER_OF_NETWORKS]:
        return
    
    getRepeatedNetworksOnThisParameters(timeline, dists, chDist, hypName)

def getRepeatedNetworksOnThisParameters(timeline, dists, chDist, hypName):
    paths: simulationPathsManager = var.variablesDict[PATHS]

    print("Simulating {} for dists {}...".format(hypName, dists[PARAMS_ID]))
    for j in range(0, ceil(var.NUMBER_OF_NETWORKS/var.THREADS)):
        
        # ----------------------------------------
        # RUN SEVERAL SIMULATIONS WITH SAME INPUTS

        D2FNets, F2FNets = [], []

        processes = []
        lock = mp.Lock()
        queue = mp.Queue()
        for i in range(var.THREADS):
            p = mp.Process(target=simulationModel, args=(queue, lock, timeline, chDist))
            processes += [p]
            p.start()
        
        for p in processes:
            netDict = queue.get()
            D2FNets += [netDict[D2F]]
            F2FNets += [netDict[F2F]]

        for p in processes:
            p.join()

        processes = []

        # ------------------------
        # SAVE SEVERAL SIMULATIONS

        for n in range(var.THREADS):
            d2fPath = '{}/d2f_{}.pickle'.format(paths.getHypothesisNetsDir(), var.THREADS * j + n)
            nx.write_gpickle(D2FNets[n].getNet(), d2fPath)
            
            f2fPath = '{}/f2f_{}.pickle'.format(paths.getHypothesisNetsDir(), var.THREADS * j + n)
            nx.write_gpickle(F2FNets[n].getNet(), f2fPath)
        
        # -----------
        # SAVE INPUTS

        saveStructInFile(chDist, paths.getGenInfoPickle())

        f = open(paths.getGenDistsInfo(), "w", encoding="utf-8")
        for k, v in dists.items():
            if k == "networksPath":
                continue
            f.write('{}: {}\n'.format(k, v))
        f.close()
    removeDir(paths.getHypothesisGraphsDir())

class simulationModel:
    def __init__(self, queue, lock, timeline, changeDist): 
        self.d2f = None
        self.queue = queue
        self.lock = lock
        self.context = Context(timeline, changeDist)
        self.runSim()

    def runSim(self):
        self.simulate()
        self.lock.acquire()
        self.queue.put({D2F: self.d2f, F2F: self.f2f})
        self.lock.release()

    def simulate(self):
        self.d2f = Simulation(self.context)

        self.d2f.getNet().graph["context"] = self.context
        self.f2f = self.d2f.getFileRelationsInTheSameCommit()