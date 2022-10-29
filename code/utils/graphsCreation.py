import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from constants import *
import variables as var

from utils.auxiliaryFunctions import getStructInFile, saveStructInFile, createDirRec, codebaseNetsPath
from utils.graphInfoClass import GraphInfo

class Chart:
    def __init__(self, graphInfo: GraphInfo):

        self.colors = ['k.', 'g.', 'b.', 'm.', 'r.', 'C9', 'C1']
        self.legendColors = ['black', 'green', 'blue', 'magenta', 'red', 'C9', 'C1']
        self.markers = ['o', 's']
        self.colorToUse = 0
        self.markerToUse = 0
        self.markersize = 3

        self.graphInfo: GraphInfo = graphInfo

        self.data = graphInfo.getData()
        self.xlabel = graphInfo.getXLabel()
        self.ylabel = graphInfo.getYLabel()
        self.pathToSaveFig = graphInfo.getPath()
        self.legendLabels = graphInfo.getLegendLabels()
        self.rotateXTickLabels = graphInfo.getRotateXTickLabels()
        self.loglog = graphInfo.getLoglog()
        self.ignorePointsWithYSmallerThan = graphInfo.getIgnorePoints()
        self.infoToTxt = graphInfo.getInfoToTxt()
    
    def draw(self):
        self.saveRelevantInfoInTxt()

        plt.clf()
        self.ax = plt.axes()

        if self.legendLabels != None and len(self.legendLabels) > len(self.colors): # limit legend
            print("Could not create graph.")
            return
        
        self.plotData()
        self.plotExtras()
        self.saveFigIntoPDF()

        self.saveSelfIntoPickle()

    def saveRelevantInfoInTxt(self):
        if self.infoToTxt != "":
            createDirRec("/".join(self.pathToSaveFig.split("/")[:-1]))
            f = open('{}.txt'.format(self.pathToSaveFig.rpartition(".")[0]), "w", encoding="utf-8")
            f.write(self.infoToTxt)
            f.close()

    def plotData(self):
        for pointSet in self.data:
            if self.loglog:
                if self.ignorePointsWithYSmallerThan != None:
                    for i in range(len(pointSet[1]) - 1, -1, -1):
                        if pointSet[1][i] < float(self.ignorePointsWithYSmallerThan):
                            del pointSet[0][i]
                            del pointSet[1][i]
                            
            if self.loglog:
                self.ax.set_xscale("log")
                self.ax.set_yscale("log")
            
            self.ax.plot(pointSet[0], pointSet[1], 'o', markersize=self.markersize, color=self.legendColors[self.colorToUse], rasterized=True)
            self.colorToUse += 1

    def plotExtras(self):
        if self.rotateXTickLabels:
            plt.xticks(rotation = 90)

        legend = None
        if len(self.data) > 1: # createLegend
            colorsLen = len(self.data)
            legend = [self.legendColors[:colorsLen], self.legendLabels]

        if legend != None:
            self.createLegend(legend[0], legend[1])

        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)

    def saveFigIntoPDF(self):
        createDirRec("/".join(self.pathToSaveFig.split("/")[:-1]))
        plt.savefig(self.pathToSaveFig, dpi=300, bbox_inches='tight')

        sPath = self.pathToSaveFig.split("/")

        newPath = ""
        for i in range(len(sPath) - 1):
            newPath += "{}/".format(sPath[i])
        newPdfPath = "{}pdfFigs".format(newPath)

        pdfPath = '{}/{}.pdf'.format(newPdfPath, sPath[-1].rpartition(".")[0])
        createDirRec("/".join(pdfPath.split("/")[:-1]))
        plt.savefig(pdfPath, dpi=300, format="pdf", bbox_inches='tight')
        plt.clf()

    def saveSelfIntoPickle(self):
        sPath = self.pathToSaveFig.split("/")
        newPath = ""
        for i in range(len(sPath) - 1):
            newPath += "{}/".format(sPath[i])

        newPicklePath = "{}pickledData".format(newPath)
        picklePath = '{}/{}.pickle'.format(newPicklePath, sPath[-1].rpartition(".")[0])
        createDirRec("/".join(picklePath.split("/")[:-1]))
        saveStructInFile(self.graphInfo, picklePath)

    def createLegend(self, colors, labels, lines=True):
        handles = []
        if lines == True:
            for i in range(len(colors)):
                handles += [mlines.Line2D([0], [0], color = 'w', marker='o', markersize=7, markerfacecolor=colors[i], label=labels[i])]
        else:
            for i in range(len(self.markers)):
                handles += [mlines.Line2D([0], [0], color = 'w', marker=self.markers[i], markersize=7, markerfacecolor=self.legendColors[0], label=labels[i])]
        plt.legend(handles=handles, prop={'size': 8}, loc='best')#, bbox_to_anchor=tuple(legendPos))

def getGraphActors(graphType, metric):
    paths = var.variablesDict[PATHS]
    graphInfo: GraphInfo = var.variablesDict[GRAPH_INFO]

    if graphType == COMPARISON_ACROSS_CODEBASES:
        graphInfo.setYLabel('Cumulative distribution, $P_{wd}^{Cum}$')
        graphInfo.setXLabel(INFO_ABOUT_METRIC[metric]["label"])
        
        pathToComparison = "{}/{}".format(DIR_TO_COMPARE_CODEBASES, INFO_ABOUT_METRIC[metric]["type"])
        createDirRec(pathToComparison)
        graphInfo.setPath('{}/{}.png'.format(pathToComparison, metric))
        graphInfo.setLoglog(True)

    elif graphType == COMPARISON_BETWEEN_METRICS: 
        graphInfo.setXLabel(INFO_ABOUT_METRIC[metric[0]]["label"].split(",")[0])
        graphInfo.setYLabel(INFO_ABOUT_METRIC[metric[1]]["label"].split(",")[0])

        if INFO_ABOUT_METRIC[metric[0]]["type"] == INFO_ABOUT_METRIC[metric[1]]["type"]:
            dirPath = '{}/graphsDir/{}/comparisons/{}'.format(paths.getCodeBaseDir(), codebaseNetsPath(),  INFO_ABOUT_METRIC[metric[1]]["type"])
        else:
            dirPath = '{}/graphsDir/{}/comparisons/miscellaneousComparisons'.format(paths.getCodeBaseDir(), codebaseNetsPath())

        createDirRec(dirPath)
        loglogStr = "_loglog" if graphInfo.getLoglog() else ""
        graphInfo.setPath('{}/{};{}{}'.format(dirPath, metric[0], metric[1], loglogStr))
    
    elif graphType == DSA_OVER_TIME_CORRELATION:
        if metric[1] == "nodesNumber":
            graphInfo.setXLabel("Number of nodes in a $tlnet$")
        else:
            graphInfo.setXLabel("WD sum across all nodes in a $tlnet$")
        graphInfo.setYLabel("Results of DSA in time limited network $tlnet$")
        graphInfo.setPath("{}/{}/{}_DSAOverTimeCorrelationWith_{}.png"\
            .format(paths.getCodeBaseGraphs(), INFO_ABOUT_METRIC[metric[0]]["type"], metric[0], metric[1]))