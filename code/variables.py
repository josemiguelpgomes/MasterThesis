from constants import *

# repositories to study
#REPOSITORIES_SET = ["ansible/ansible", "tensorflow/tensorflow", "hashicorp/terraform", "kubernetes/kubernetes", "bitcoin/bitcoin"]
#REPOSITORIES_SET = ["tensorflow/tensorflow", "kubernetes/kubernetes"]
#REPOSITORIES_SET = ["bitcoin/bitcoin"]
#REPOSITORIES_SET = ["mvt-project/mvt"]
REPOSITORIES_SET = ["ansible/ansible", "bitcoin/bitcoin", "kubernetes/kubernetes", "tensorflow/tensorflow", "hashicorp/terraform"]
#REPOSITORIES_SET = ["ansible/ansible", "tensorflow/tensorflow", "hashicorp/terraform", "kubernetes/kubernetes", "bitcoin/bitcoin"]

# developers from real code bases to ignore
DEVELOPERS_TO_IGNORE = {"tensorflow/tensorflow": ["A. Unique TensorFlower"]}

# net construction
MAX_MONTHS_COLLAB = 1            # maximum months interval to consider collaboration
HOW_MANY_DAYS_IN_A_NET = 90 # time limited networks
DAYS_BETWEEN_NETS = 45     # time limited networks

# ------------------------------------------------------------------------------------------------------
# SIMULATION MODEL

THREADS = 5
NUMBER_OF_NETWORKS = 5

########################################################################################################
# TIMELINE GENERATION

"""
if COPY == True:
    copies different iterations done in REPO_TO_COPY_FROM
else:
    creates based on variable DISTRIBUTIONS
"""
COPY = True 
REPO_TO_COPY_FROM = "fakeRepo/fakeRepo"

"""
when running simulationModel/simulation/main.py:
    if an argument to the program is provided, 
        copies code base attributes from the code base respective to the argument
    else
        code base attributes will be created based on DEFAULT_CODEBASE_ATTRIBUTES
"""
DEFAULT_CODEBASE_ATTRIBUTES = { # DEFAULT PARAMS, change as needed
    NOD: 46,  # number of developers
    NOC: 700, # number of commits
    F_ADD: 214, # total files added
    F_CH: 2242, # total files changed
    F_DEL: 27,  # total files deleted
    CB_DUR: 35602622, # codebase duration (in seconds)
    P_C_ADD: 0.12, # percentage of commits with more than zero files added
    P_C_CH: 0.97, # percentage of commits with more than zero files changed
    P_C_DEL: 0.005 # percentage of commits with more than zero files deleted
}

DISTRIBUTIONS = { # DEFAULT PARAMS, change as needed
    # commits per dev
    NOC_PER_DEV: PL_DIST, 
    
    # rule to choose which developer to commit
    SEL_C_AUTHOR: COMPLEX_RULE, \
        RULE_CHOOSE_DEV_TO_START_TO_COMMIT: PROPORTIONAL_COMMITS_TO_DO,
        RULE_CHOOSE_DEV_TO_COMMIT: PROPORTIONAL_COMMITS_DONE,

    # adds
    F_ADD_PER_C: ALL_IN_FIRST, \
        P_ADDS_FIRST_COMMIT: "-", MULTIPLIER_FILES_ADDED: 1,

    # deletes 
    F_DEL_PER_C: UNIF_DIST, \

    # changes
    F_CH_PER_C: UNIF_DIST, \

    # dates
    D_PER_C: UNIF_DIST, 
}
########################################################################################################

# TIMELINE SIMULATION

# sets of params to build rules similar to a preferential attachment rule with initial acttractiveness
INITIAL_ACTRACTIVENESS_SET = [0]
ATTRACTIVENESS_ALPHA = [1]


# GLOBAL VARIABLES
def initVariablesDict():
    global variablesDict
    variablesDict = {}