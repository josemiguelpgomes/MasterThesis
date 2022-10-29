PLACE_HOLDER = 1
DEV_TYPE = "developer"
FILE_TYPE = "file"
METHOD_TYPE = "method"
RESULTSDIR = "../results"
THEOCODEBASES = "theoreticalCodebases"
DIR_TO_COMPARE_CODEBASES = '{}/codebasesComparison'.format(RESULTSDIR)

# NETS

NET_MANAGER = "NETWORK_MANAGER"
ALL_TIME = "allTime"
D2I = "D2I"
I2I = "I2I"
D2D = "D2D"
F2F = "F2F"
D2DM = "D2DM"
D2F = "D2F"
F2F = "F2F"
D2M = "D2M"
M2M = "M2M"
F_CHANGES_BY_DEV = "commitsToFiles"
M_CHANGES_BY_DEV = "commitsToMethods"
NON_EXISTENT_ITEM = "None"
DELETED_ITEM = "ELIMINATED"
ITEM_DATES = "dates"
ITEM_NLOC = "nloc"
ITEM_CC = "comp"
NET_INITIAL_DATE = "initialDate"
NET_FINAL_DATE = "finalDate"
ITEM_COMMITS_DATES = "dates"

ST_WEIGHT = "weight"
D2D_WEIGHT = "oneMonth_numberOfCollabs"

# MISC

PATHS = "paths"
BOTH_TL = "both"
EMP = "empirical"
THEO = "theoretical"
COLLAB_PER_FILE = "collaborationPerFile"

# METRICS TO ANALYSE 

D2F_D_WD = "D2F_DWd"
D2F_D_COMMS = "D2F_DComms"
D2F_F_WD = "D2F_FWd"
D2D_D_D = "D2D_Dd"
D2D_WD = "D2D_DNrWd"
F2F_F_WD = "F2F_FWd"
D2DM_WD = "D2DM_DNrWd"
D2M_D_WD = "D2M_DWd"
D2M_M_WD = "D2M_MWd"
M2M_WD = "M2M_WD"

# GRAPHS

COMPARISON_ACROSS_CODEBASES = "comparisonAcrossTime"
COMPARISON_BETWEEN_METRICS = "comparison"
DSA_OVER_TIME_CORRELATION = "DSAoverTime"

GRAPH_INFO = "graphInfo"
PL_FIT = "powerLawFit"

DATA = "data"
XLABEL = "xlabel"
YLABEL = "ylabel"
PATH_TO_FIG = "pathToSaveFig"
LOGLOG = "loglog"
LEGEND_LABELS = "legendLabels"
IGNORE_POINTS_Y_SMALLER_THAN = "ignorePointsWithYSmallerThan"
ROTATE_X_LABELS = "rotateXTickLabels"
INFO_TO_TXT = "infoToTxt"
DSA_PER_NET = "dsaPerTlNet"

METRICS = [ 
    # >> FILES
    D2F_D_WD, # developers 
    D2F_F_WD, # files 
    D2D_WD,# dev relations
    F2F_F_WD, # file relations 
    ITEM_NLOC,
    ITEM_CC,

    # >> METHODS
    D2DM_WD, # devs
]

COMPARISONS_INFO = {
    D2D_WD: {
        D2DM_WD: {LOGLOG: True, PL_FIT: True}
    }
}

INFO_ABOUT_METRIC = {
    D2F_F_WD: {
        "label": "File D2F WD, $wd$ \n(number of changes in a file)",
        "type": "files",
    },
    D2F_D_WD: {
        "label": "Developer D2F WD, $wd$ \n (number of file changes by a developer)",
        "type": "devs"
    },
    F2F_F_WD: {
        "label": "F2F WD, $wd$\n(sum of number of files in commits where\na certain file is present)",
        "type": "files"
    },
    D2D_WD: {
        "label": "FD2D WD, $wd$\n(number of times that developer $d$ have\ncollaborated with other developers, in files)",
        "type": "D2D"
    },
    D2DM_WD: {
        "label": "MD2D WD, $wd$\n(number of times that developer $d$ have\ncollaborated with other developers, in methods)",
        "type": "D2D"
    },
    ITEM_NLOC: {
        "label": "",
        "type": "files",
    },
    ITEM_CC: {
        "label": "",
        "type": "files",
    }
}

# CODE BASE ASPECTS

CUM_DIST = "cumDist"
CUM_SUM = "cumSum"

COMMITS_PER_DEV = "commitsPerDev"
FILES_ADDED_UNTIL_T = "filesAddedPerTimestep"
FILES_DELETED_UNTIL_T = "filesDeletedPerTimestep"
FILES_CHANGED_UNTIL_T = "filesChangedPerTimestep"
DATE_DIFF_PER_T = "datesPerTimestep"
U_GLOBAL = "uniformityOfCommitsAcrossTimeDist"
U_LOCAL = "uniformityOfCommitsAcrossDevExistenceDist"
NEW_DEVS_UNTIL_T = "newDevelopersUntilTimestepT"

CODEBASE_ASPECTS = [COMMITS_PER_DEV, FILES_ADDED_UNTIL_T, FILES_DELETED_UNTIL_T, FILES_CHANGED_UNTIL_T, DATE_DIFF_PER_T, \
    U_GLOBAL, U_LOCAL, NEW_DEVS_UNTIL_T]

CONCRETE_GRAPH_INFO_CB_ASPECTS = {
    COMMITS_PER_DEV: {
        XLABEL: "Number of commits per developer, $wd$",
        YLABEL: "Cumulative distribution, $P_{k}^{Cum}$",
    },
    "datesPerTimestep": {
        XLABEL: "Time step, $t$",
        YLABEL: "Normalized time interval passed since first time step",
    },
    FILES_ADDED_UNTIL_T: {
        XLABEL: "Time step, $t$",
        YLABEL: "Normalized sum of files added until time step $t$",
    },
    FILES_CHANGED_UNTIL_T: {
        XLABEL: "Time step, $t$",
        YLABEL: "Normalized sum of files changed until time step $t$",
    },
    FILES_DELETED_UNTIL_T: {
        XLABEL: "Time step, $t$",
        YLABEL: "Normalized sum of files deleted until time step $t$",
    },
    NEW_DEVS_UNTIL_T: {
        XLABEL: "Time step, $t$",
        YLABEL: "Normalized number of developers that made\n atleast one commit until time step $t$",
    },
    U_LOCAL: {
        XLABEL: "$\\tilde{U}_{local}$",
        YLABEL: "Cumulative distribution, $P_{\\tilde{U}_{local}}^{Cum}$",
    },
    U_GLOBAL: {
        XLABEL: "$\\tilde{U}_{global}$",
        YLABEL: "Cumulative distribution, $P_{\\tilde{U}_{global}}^{Cum}$",
    }
}

# SIMULATION
HYP_RESULTS = "hypothesisResults"
SIM_MANAGER = "simManager"
CA = "cba"
DISTS = "dists"
CH_R = "chR"

DISTS_INFO_FILE = "distsInfo.txt"
CBATTRS_INFO_FILE = "cbAttrsInfo.txt"
PARAMS_ID = "paramsId"

FROM_DATA_TO_COMPARE = "fromDataToCompare"
FROM_OTHER_ATTRIBUTES = "fromOtherAttribs"

# GENERATION 
COMMITS = "commits"
FILES_ADDED = "filesAdded"
FILES_DELETED = "filesDeleted"
FILES_CHANGED = "filesChanged"
DATES = "dates"

# CBA ATTRS
REAL_CODE_BASE = "realCodebase"
P_C_ADD = "pcAdd"
P_C_DEL = "pcDel"
P_C_CH = "pcCh"
NOC = "noc" # number of commits
NOD = "nod" # number of developers
F_ADD = "fAdd"
F_CH = "fCh"
F_DEL = "fDel"
CB_DUR = "cbDur"

# DISTS
NOC_PER_DEV = "commitsDist"
F_ADD_PER_C = "filesAddedDist"
F_DEL_PER_C = "filesDeletedDist"
F_CH_PER_C = "filesChangedDist"
D_PER_C = "datetimeDiffs"
SEL_C_AUTHOR = "selectAuthorRule"
MULTIPLIER_FILES_ADDED = "differentNumberOfFilesAdded"

   # when using COMPLEX_RULE to choose developers
RULE_CHOOSE_DEV_TO_START_TO_COMMIT = "developerToBeChosenToStartToCommit"
RULE_CHOOSE_DEV_TO_COMMIT = "developerToBeChosenToCommit"

# POSSIBLE INPUT DISTS
UNIF_DIST = "uniform"
PL_DIST = "powerlaw"
EXP_DIST = "exponential"
ALL_IN_FIRST = "allInFirst"
P_ADDS_FIRST_COMMIT = "percentageOfAddedFilesInFirstCommit"

RANDOM = "random"
COMPLEX_RULE = "greaterProbability"

PROPORTIONAL_COMMITS_TO_DO = "greaterProbabilityTheMoreCommitsToDo"
PROPORTIONAL_COMMITS_DONE = "greaterProbabilityTheMoreCommitsDone"

# CHANGE RULE
ALPHA = "alpha"
METHOD = "method"
A = "A"

