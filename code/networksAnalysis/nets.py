from dateutil.relativedelta import relativedelta
import networkx as nx

from constants import ALL_TIME, PATHS
import variables as var
from utils.pathClass import netAnalysisPathsManager

from utils.networksClasses import Network
from utils.auxiliaryFunctions import datetimeIntoStr, codebaseNetsPath

def readNet(softMod, netType, date=ALL_TIME):
    paths: netAnalysisPathsManager = var.variablesDict[PATHS]

    if date == ALL_TIME:
        intervalPath = ""
    else:
        intervalInitialDate = datetimeIntoStr(date)
        intervalFinalDate = datetimeIntoStr(date + relativedelta(days=var.HOW_MANY_DAYS_IN_A_NET))
        intervalPath = "_{}_{}".format(intervalInitialDate, intervalFinalDate)

    return Network(nx.read_gpickle(paths.getCodeBaseDir() + "/networksDir/{}/{}_{}{}.pickle"\
        .format(codebaseNetsPath(), softMod, netType, intervalPath)))
