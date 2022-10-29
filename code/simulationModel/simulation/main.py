import sys

from constants import *
import variables as var
from utils.pathClass import simulationPathsManager

from simulationModel.simulation.simManager import SimManager

if __name__ == '__main__':
    var.initVariablesDict()
    var.variablesDict[PATHS] = simulationPathsManager()

    codeBase = sys.argv[1] if len(sys.argv) == 2 else None
    
    sm: SimManager = SimManager(codeBase)
    var.variablesDict[SIM_MANAGER] = sm

    sm.runSimulations()
