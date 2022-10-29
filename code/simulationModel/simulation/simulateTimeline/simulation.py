import networkx as nx

from utils.networksClasses import Network
from simulationModel.simulation.simulateTimeline.classes import Developer, File
from utils.timelineClass import Timeline
import time

class Simulation(Network):
    def __init__(self, context):
        super().__init__(nx.Graph())
        self.context = context
        self.process()
    
    def process(self):
        # if model == generative plus envolving
        self.fileToFileRelationSameCommit = Network(nx.Graph())
        filesPerTimeStamp = {}

        timeline: Timeline = self.context.tl
        for commitId in timeline.getCommitIds():
            author = timeline.getAuthorOfCommitId(commitId)
            d: Developer = self.context.getDeveloperNumbered(author)
            filesInCommit = d.commitToFiles(self, self.context.A, self.context.alpha)
            filesPerTimeStamp[commitId] = filesInCommit
            
            if len(filesInCommit) < 100:
                for i in range(len(filesInCommit)):
                    for j in range(i + 1, len(filesInCommit)):
                        self.fileToFileRelationSameCommit.addEdgeOrWeightToNetwork(filesInCommit[i], filesInCommit[j])
        self.fileToFileRelationSameCommit.getNet().graph["filesPerTimestamp"] = filesPerTimeStamp

    def getFileRelationsInTheSameCommit(self):
        for f in self.getFileNodes():
            self.fileToFileRelationSameCommit.addNode(f)
        return self.fileToFileRelationSameCommit

    def getDegree(self, item):
        if item in self.net.nodes():
            return nx.degree(self.net, item, weight="weight")
        else:
            return 0