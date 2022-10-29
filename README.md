Before reading or using this code, it is recommended to read the Master Thesis "Simulation of the emergent patterns of developers’ collaboration through their interactions with files" by José Miguel Pereira Gomes.

Any doubts you may have, please contact me through email: `josemiguelg@tecnico.ulisboa.pt`

# NECESSARY PACKAGES

We use Python as the programming language, more specifically, version 3.9, with pip 22.3. Different packages are used, which are listed below, with the recommended versions:

    - Matplotlib (3.6.1)
    - Networkx (2.8.7)
    - Numpy (1.23.4)
    - Powerlaw (1.5)
    - Pydriller (2.1)
    - Scipy (1.9.3)

# INSTRUCTIONS

This repository is composed of 5 main directories, associated with a certain program: 
- dataMining
- networksConstruction
- networksAnalysis
- simulationModel/construction
- simulationModel/analysis

Normally, they should be ran in the previously described order.

The commands for each program, a description and an example are shown next. It should be noted that `variables.py` have a set of different variables that should be considered before running the programs:
- `THREADS` and `NUMBER_OF_NETWORKS` dictate how many threads you will be using to simulate a determined number of networks, i.e. a determined number of runs of the algorithm per simulation $s^i_k$.
- `COPY`, `REPO_TO_COPY_FROM` and `DISTRIBUTIONS`. If `COPY` is True, it will simulate $sDists_j$ with $j \in [1-8]$ as described in the Thesis. Else if `COPY` is False, $sDists_j$ is created based on the variable `DISTRIBUTIONS`.
- `INITIAL_ACTRACTIVENESS_SET` and `ATTRACTIVENESS_ALPHA` as sets of possible $chR$. If `ATTRACTIVENESS_ALPHA` $= [1]$, then for each value $k$ in `INITIAL_ACTRACTIVENESS_SET`, a different $h_k$ will be used.

For the running of this programs, associate the directory `code` to the `PYTHONPATH`, through the following command:
    
`export PYTHONPATH="${PYTHONPATH}:~/pathWhereCodeDirIs/code`

## Programs
### Empirical Analysis

- Data mining: `python3.9 dataMining/main.py REPO/NAME`
    
    This program mines the necessary data of an open-source repository from Github, whose name is REPO/NAME.
    
    Example for Bitcoin codebase: `python3.9 dataMining/main.py bitcoin/bitcoin`

- Networks construction: `python3.9 networksConstruction/main.py REPO/NAME`
    
    This program constructs the networks based on the data previously mined in 1.
    
    Example for Bitcoin codebase: `python3.9 networksConstruction/main.py bitcoin/bitcoin`

- Networks analysis: `python3.9 networksAnalysis/main.py REPO/NAME`
    
    This program analyses the networks, storing the results in a directory named `results`, at the same level that `code` directory is.
        
    Example for Bitcoin codebase: `python3.9 networksAnalysis/main.py bitcoin/bitcoin`

### Simulations

- Run simulations with restricted *RCB*: `python3.9 simulationModel/simulation/main.py REPO/NAME`
    
    This program generates the timeline and simulates it according to the different variables in `variables.py`, for a specific *RCB* $=$ REPO/NAME.

    Example for Bitcoin codebase: 
    
    `python3.9 simulationModel/simulation/main.py bitcoin/bitcoin`

- Analysis simulations done with restricted *RCB*: `python3.9 simulationModel/analysis/main.py REPO/NAME`
    
    This program analyses the results of the distributions generated through the various simulations done with respect to a determined *RCB*, which in this case is defined by the `REPO/NAME` argument.

    Example for Bitcoin codebase: 
    
    `python3.9 simulationModel/analysis/main.py bitcoin/bitcoin`