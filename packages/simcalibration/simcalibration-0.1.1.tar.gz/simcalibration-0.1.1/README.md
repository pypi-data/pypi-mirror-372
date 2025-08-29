<div align="center">    <h1>SimCal — Meta-Simulation benchmarking in Python</h1></div></br>
SimCal is a Python library for building, testing and calibrating simulation outcomes using [Bayesian Network Structure Learning](https://ermongroup.github.io/cs228-notes/learning/structure/) to help practitioners identify if inferences of ML method selection on real-world data is reflected within learned synthetic datasets.  
</br>  
</br>  
The main goal of this project is to bring empirical understanding to practitioners in environments in which the accuracy of inferences surrounding picking the best ML method for a problem is based on a small number of samples. This uncertainty of representativeness to an underlying distribution is common as most custodians of data only have availablity to the problem via a rich and specific dataset. The traditional approach to ML method selection which is constrained to real-world data, posits to select the problem-method which performs best given what is observable. This however assumes that limited-data captures the underlying complexity of a domain, leading to the risk of drawing conclusions that are not representative of the larger population. What we instead propose is a meta-simulation to extend ML method selection to circumvent limitations arising from constrained data. With SimCal, we designed a framework to help orchestrate meta-simulations and allow custodians of data to build and test the utility of calibrated simulations within ML method selection. Central to this approach is the integration of Structural Learners (SLs) which interprets underlying relationships in data and estimates Directed Acyclic Graphs (DAGs) which depict the characteristics of the domain, this then can be the basis of producing synthetic observations which differ in their alginment to the real-world. This tool makes available to the practitioner the ability to configure the different levels of the meta-simulation environment by selecting ML estimator parameters, SL hyperparameters and the specification of the Bayesian Network used to represent the real-world. 

## Table of contents

- [Table of contents](#table-of-contents)
- [⚙️ Download](#download)
- [📜 Usage](#usage)
  - [👀 Quickstart](#-quickstart)
  - [📦 Define SLs](#-define-sl-learners)
    - [🎯 Score-based - Hill-Climbing](#-sl-hc)
    - [🎯 Score-based - Tabu List](#-sl-tabu)
    - [🕸️ Constraint-based - PC.stable](#-sl-pc)
    - [🕸️ Constraint-based - Grow-Shrink](#-sl-gs)
    - [🎨 Hybrid-based - Max-Min Hill-Climbing](#-sl-mmhc)
    - [🎨 Hybrid-based - RSMAX2](#-sl-rsmax2)
    - [🎨 Hybrid-based - Hybrid HPC](#-sl-h2pc)
  - [📊 Define ML estimator](#-define-ml-problem)
    - [🏷️ Binary Classification](#-ml-binary)
  - [📈 Outputs & Visualization](#-visualization)
- [License](#license)


## Installation

Simcalibration is a Python package for simulation-based calibration with R integration.
It requires **Python (>=3.9)**, **R**, and **Graphviz**.

⚠️ Note: This package is only compatible on **Linux** and **macOS**.
Windows users should install VirtualBox and simulate a compatible environment:

Then install simcalibration with pip:

```bash
pip install simcalibration
```

## Usage

SimCal has been tested on Python 3.8 and R 4.3.2. To setup a meta-simulation, three components (Bayesian Network, Structural Learners and ML estimators) need to be specified. 
The first component is for the user of the framework to provide the structure and parameters of their real-world model. 
Depending on the nature of the problem the Structure (i.e., variables) and Conditional Probability Table (i.e., discrete measure of relationships) may be well or partially known, in this circumstance it is best to import this Bayesian Network as a DagsimModel. Alternativelly if data of the domain is available then it is possible to estimate the structure and parameters and use learning methods offered by Bayesian Network packages (e.g., pgmpy)
The second component is for the user of the framework to provide the SL learners to be used to estimate structural models and perform ML benchmarking. This dictates the algorithms which will function inside the meta-simulation to learn underlying relationships and output DAGs which embody the data-generating process which is of interest.
The third component is for the user of the framework to provide their selection of ML estimator and therefore the shape of the ML problem. The most popular kinds of ML problem are regression and classification. The ML estimators selected for the meta-simulation will be tested in the data environments relevant to the custodian, including in benchmarks of the true real-world, limited real-world and learned calibrated worlds. 

## [👀 Quickstart](#-quickstart)
To begin running a simple meta-simulation, access the main application (i.e., main.py) and configure the three components as above to desired settings. Determine the size of the train/test datasets in benchmarking and provide the scale of experimental repetitions performed for the true real-world, limited real-world and learned calibrated worlds.

## [📦 Define SLs](#-define-sl-learners)
The following are a selection of SL algorithms available for integration within the meta-simulation. Each can be configured with hyperparameters for extended configuration.

## [🎯 Score-based - Hill-Climbing](#-sl-hc)
Hill climbing is a local search algorithm which begins with an initial solution and iteratively makes small changes to enhance it, guided by a heuristic function that assesses solution quality. The process continues until a local maximum is reached, indicating that further improvement is not possible with the current set of moves.

## [🎯 Score-based - Tabu List](#-sl-tabu)
Tabu search is a greedy search algorithm similar to HC, it specifically addresses the tendency of local searches to get stuck in suboptimal regions. Tabu relaxes traditional rules by allowing worsening moves when no improvement is available and introduces prohibitions (tabu) to discourage revisiting previous solutions. Memory structures are employed to track visited solutions or user-defined rules, marking potential solutions as "tabu" if recently visited or violating a rule. The algorithm iteratively explores the neighborhood of each solution, progressing towards an improved solution until a stopping criterion is met.

## [🕸️ Constraint-based - PC.stable](#-sl-pc)
The PC (Peter and Clark) algorithm initiates with a complete graph, where all nodes are connected. In the first step, pairs of nodes undergo conditional independence tests with a specified threshold (i.e., p-value). If the test results indicate conditional independence between node pairs, the corresponding edges are removed from the complete graph. Subsequent steps in the algorithm are primarily focused on orienting the remaining edges. 

## [🕸️ Constraint-based - Grow-Shrink](#-sl-gs)
The Grow-Shrink algorithm is a constraint-based approach which iteratively grows and shrinks a set of candidate edges based on conditional independence tests. It iteratively refines the graph through a two-phase process. In the growing phase, candidate edges are systematically added based on conditional independence tests. Each potential edge is subjected to a statistical evaluation, and if justified by the data, it is incorporated into the evolving graph. Subsequently, the shrinking phase commences, during which existing edges are assessed for removal based on similar conditional independence tests. Edges passing the removal criteria are pruned from the graph.

## [🎨 Hybrid-based - Max-Min Hill-Climbing](#-sl-mmhc)
The Max-Min Hill-Climbing (MMHC) algorithm is a hybrid-based learning method. It begins with an empty graph and employs a two-phase approach. First, it conducts a score-based search resembling hill-climbing, incrementally adding and removing edges based on a chosen scoring metric (e.g., Bayesian Information Criterion (BIC)). Next, MMHC integrates constraint-based techniques, using conditional independence tests to validate and refine the network structure. It iteratively combines score-based and constraint-based strategies, dynamically adjusting the network until the process meets convergence, where no further modifications improve the model fit or meet constraints.

## [🎨 Hybrid-based - RSMAX2](#-sl-rsmax2)
The Restricted Maximisation (RSMAX2) algorithm employs an iterative process that narrows down the search space by restricting the potential parents of each variable to a smaller subset of candidates. This restriction is based on statistical measures, such as mutual information, to identify promising candidate parents for each variable. The algorithm then searches for the network that satisfies these constraints, and the learned network is utilized to refine candidate selections for subsequent iterations. The iterative process continues until convergence, with each iteration refining the candidate parent sets based on the learned network from the previous iteration.

## [🎨 Hybrid-based - Hybrid HPC](#-sl-h2pc)
The Hybrid 2-Phase Construction (H2PC) algorithm combines constraint-based and score-based techniques to enhance the efficiency and accuracy of structure learning. It involves two main phases: a constraint-based phase and a score-based phase. In the first phase, the algorithm utilizes conditional independence tests on the data to identify potential relationships among variables, constructing an initial Bayesian network skeleton. This phase emphasizes exploring conditional dependencies. Moving to the score-based phase, the algorithm employs a scoring metric to evaluate and refine the structure. It considers different candidate structures, assigning scores based on statistical measures to assess their fitness to the observed data. The scoring function aids in selecting the optimal structure by optimizing a predefined criterion, such as BIC.

## [📊 Define ML estimator](#-define-ml-problem)
Specifying the kind of methods that apply to a problem are context-specific. In ML, regression and classification problems are widespread and hence ML estimators have developed to provide better and better methods that address these problems.

## [🏷️ Binary Classification](#-ml-binary)
Binary classification is an example of a problem where the feature and target variables have two finite states. The ML estimators available for binary classification range in complexity and efficency, the problem therefore establishes an interesting selection of options that differ in competition for the problem. 

## [📈 Outputs & Visualization](#-visualization)
When the meta-simulation is finished, all the findings from benchmarking will be saved to the result folder within the project. The visualisations provided in the postprocessing functionality, present a number of perspectives to the data. 

The output scatterplot of all scores taken in the meta-simulation. This visualises the relationship between an x-axis, depicting the true real-world of which all strategies are compared to, and on the y-axis the estimation performance of all strategies (e.g., limited real-world and learned worlds). This output shows a 1:1 identity line alongside the all measures, the closer alternative strategies (i.e., y estimates) match this line, the stronger in realism the employed technique is to rendering true real-world results.

The output boxplot shows all measures in contrast to the true result taken as a distribution within the meta-simulation. This visualises the differences between alternative SL estimates and true real-world measures, emphasising the learner bias among strategies and identifying the margin of their realism.

The output violinplot shows the performance of SLs in relation to their rank-order (e.g., A-E) and the density that these orders appear. This visualises the consistency at which learners produce similiar inferences within ML method selection. 

## License 

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.
