from constants import *
import variables as var

from utils.pathClass import simulationPathsManager
from utils.auxiliaryFunctions import saveStructInFile

ITALIC = "\\textit{"
MTR_BEGIN = "\multirow{4}*{"
C_LINE = "\cline{2-6}"
P_END = "}"

class ComplexEval():
        def __init__(self) -> None:
            self.evalPerSDists = {}

        def addKSforCEval(self, distsId, net, hyp, res):
            self.addCEval(distsId, net, hyp, 'KS', res)

        def addGammaDiffForCEval(self, distsId, net, hyp, res):
            self.addCEval(distsId, net, hyp, 'gammaDiff', res)
        
        def addMaxPercForCEval(self, distsId, net, hyp, res):
            self.addCEval(distsId, net, hyp, 'maxPerc', res)

        def addAspectForCEval(self, distsId, aspect, res):
            if distsId not in self.evalPerSDists:
                self.evalPerSDists[distsId] = {}
            self.evalPerSDists[distsId][aspect] = res

        def addCEval(self, distsId, net, hyp, evalType, res):
            if distsId not in self.evalPerSDists:
                self.evalPerSDists[distsId] = {}
            if net not in self.evalPerSDists[distsId]:
                self.evalPerSDists[distsId][net] = {}
            if hyp not in self.evalPerSDists[distsId][net]:
                self.evalPerSDists[distsId][net][hyp] = {}
            self.evalPerSDists[distsId][net][hyp][evalType] = res
        
        def getKSForCEval(self, distsId, net, hyp):
            return self.getCEval(distsId, net, hyp, 'KS')
        
        def getGammaDiffForCEval(self, distsId, net, hyp):
            return self.getCEval(distsId, net, hyp, 'gammaDiff')

        def getMaxPercForCEval(self, distsId, net, hyp):
            return self.getCEval(distsId, net, hyp, 'maxPerc')

        def getCEval(self, distsId, net, hyp, evalType):
            return self.evalPerSDists[distsId][net][hyp][evalType]

        def getAspectForCEval(self, distsId, aspect):
            return self.evalPerSDists[distsId][aspect]

        def selfToTxt(self):
            paths: simulationPathsManager = var.variablesDict[PATHS]
            f = open(paths.getComplexEvalTxt(), "w")

            f.write("{}\n".format(D2D))

            f.write("\multirow{2}{*}{$j$} & \multirow{2}{*}{$k$} & D2F $\gamma$ diff & D2D $\gamma$ & D2D & D2D & $newDeveloper$ & $\\tilde{U}_{global}dist$ & $\\tilde{U}_{local}dist$\\\\ \n")
            f.write("& & and KS & diff & KS & max diff & $untilT$ KS & KS & KS \\\\ \hline \n")

            for mId, analSet in self.evalPerSDists.items():
                if mId in list(range(3, 9)):
                    analCharac = analSet[D2D]
                    hypCount = 0
                    for hyp in analCharac.keys():
                        d2fGammaDiff = self.getGammaDiffForCEval(mId, D2F, hyp)
                        d2fKS = self.getKSForCEval(mId,  D2F, hyp)
                        d2dGammaDiff = self.getGammaDiffForCEval(mId, D2D, hyp)
                        d2dKS = self.getKSForCEval(mId,  D2D, hyp)
                        d2dMaxPerc = self.getMaxPercForCEval(mId, D2D, hyp)

                        if hypCount >= 1:
                            if hypCount == 3:
                                endLine = "\hline"
                            else:
                                endLine = C_LINE
                            f.write("& {} & ({:.2f}, {:.2f}) & {:.1e} & {} & {} & & & \\\\ {} \n"\
                                .format(hyp.split("_")[-1], d2fGammaDiff, d2fKS,
                                    d2dGammaDiff, d2dKS, d2dMaxPerc, endLine
                                )
                            )
                        else:
                            newDevsKS = self.getAspectForCEval(mId, NEW_DEVS_UNTIL_T)
                            uGlobalKS = self.getAspectForCEval(mId, U_GLOBAL)
                            uLocalKS = self.getAspectForCEval(mId, U_LOCAL)
                            f.write("{}{}{} & {} & ({:.2f}, {:.2f}) & {:.1e} & {} & {} & {}{}{} & {}{}{} & {}{}{} \\\\ {} \n"\
                                .format(MTR_BEGIN, mId, P_END, hyp.split("_")[-1], d2fGammaDiff, d2fKS,
                                    d2dGammaDiff, d2dKS,
                                    d2dMaxPerc, 
                                    MTR_BEGIN, newDevsKS, P_END,
                                    MTR_BEGIN, uGlobalKS, P_END,
                                    MTR_BEGIN, uLocalKS, P_END,
                                    C_LINE
                                )
                            )
                        hypCount += 1
            f.close()

        def selfSave(self):
            paths: simulationPathsManager = var.variablesDict[PATHS]
            saveStructInFile(self, paths.getComplexEvalPath())