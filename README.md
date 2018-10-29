# Description #
This a general software framework for solving traffic assignment problems, both static and dynamic, utilizing the [OTM API](https://github.com/ggomes/otm-sim) to encode traffic scenarios. 
The included solution algorithms can run in High Performance Computing environments.

# SET UP #

**Step 1.** Install the [JAVA 8](http://www.oracle.com/technetwork/java/javase/downloads/index.html) JDK on your computer.
[This](https://www.java.com/en/download/help/version_manual.xml) will show you how to check your current version of JAVA.

**Step 2.** Install Python on your system if not already installed. Code was developed with Python 2.7.

** Step 3.** Install Python-igraph library. This library is necessary to validate the installation. The installation test solves a small static traffic assignment problem using the Frank-Wolfe algorithm.

* On Windows: Download [the appropriate cp27 Python-igraph](http://www.lfd.uci.edu/~gohlke/pythonlibs/#python-igraph) for your system and run the command 

```
#!python

python -m pip install location_of_wheel

```

* On Linux/MacOS: Follow [these instructions](http://igraph.org/python/#pyinstallosx)

** Step 4.** Install [Py4J](https://www.py4j.org/install.html) to establish a connection between Python and Java code.


** Step 5. ** Install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

** Step 6 ** Set up SSH for Bitbucket. This is optional but it allows you to establish secure connections to Bitbucket without providing your username/password every time. Follow these [instructions](https://confluence.atlassian.com/bitbucket/set-up-ssh-for-git-728138079.html)

** Step 7.** Fork the ta_solver repository and clone it to your computer.

**Step 8.** Send an email to Gabriel Gomes (gomes@path.berkeley.edu) requesting access to the BeATS Dropbox folder. Please include your Dropbox user name. This folder contains a jar file named py4jbeats-1.0-SNAPSHOT-jar-with-dependencies.jar. This file includes the BeATS API and a utility called py4j which establishes a connection between Python and Java. You should have Dropbox sync this folder with your computer so that you always have the latest version of the BeATS API. If this is not possible (e.g. your Dropbox account is full), then ask and we can send you the jar file by email. This is not ideal, since you will not stay up to date with changes to the API. 

Alternatively you can grab the required jar files [here](https://gcgomes.bitbucket.io/).

**Step 9.** Copy py4jbeats-1.0-SNAPSHOT-jar-with-dependencies.jar to the ta_solver directory under ta_solver/python

**Step 10.** Run the scripts below to validate installation:

* Run **First_Test.py** to test the **Static Model**, which should print out **SUCCESS** at the end of the output.


# Contacts #

* **Juliette Ugirumurera**: julymurera@gmail.com
* **Gabriel Gomes**: gomes@path.berkeley.edu

# Description #

The goal of this project is to establish an interface between the traffic modeling and the numerical sides of the traffic assignment problem. The intended users are the modelers. 

To use the system, you must implement three things:

1. A link state data class. This is an implementation of the Traffic_States.Abstract_Traffic_State class. Objects of this class should hold state information for a single link of the network. If your model is multi-commodity, then all commodities should be included. 

2. A traffic model. This is an implementation of Traffic_Models.Abstract_Traffic_Model. 

3. A link cost function. This is an implementation of Cost_Functions.Abstract_Cost_Function. 

## Architecture ##

Below is a diagram of the assumed data flow. The algorithms team (lead by Juliette) is in charge of the SOLVER, which includes numerical methods for convex optimization problems and variational inequalities, running in the HPC environment. 

![Picture1.png](https://bitbucket.org/repo/5q9q4pE/images/1708996569-Picture1.png)


The data classes depicted in the figure are described below. 

![Picture2.png](https://bitbucket.org/repo/5q9q4pE/images/2822392912-Picture2.png)

The generic SOLVER works in a loop in which it generates candidate demand assignments, and expects to be given the corresponding network cost trajectory (`trajectory' here means trajectory in time). This loop continues until an equilibrium demand assignment is reached. 

In addition to evaluating the traffic model and link cost functions, there are additional methods which, if implemented, may increase the efficiency of the solver. 

* Symmetry: If the Jacobian of the demand-to-cost function is symmetric, then the solver may use a convex optimization problem to find the solution. Set the `is_symmetric' flag of the traffic model and the cost functions to 'True' if you want this to happen. 

* Antiderivative: If convex optimization is used, then the cost function of the optimization problem will be the antiderivative of the demand-to-cost function. Some numerical algorithms will require this information. To use these algorithms, you should implement the "evaluate_Antiderivative" method of the cost function. 

* Gradient: Similarly with the gradient of both the cost function and the traffic model.

##  Description of Networks Provided under configfiles Folder ##
* The *three_links.xml* file describes a small, three links, network as shown below:

![three_links.PNG](https://bitbucket.org/repo/kM5M6MM/images/2125839927-three_links.PNG)

* The *seven_links.xml* file describes a network with seven links shown below:

![Seven_links.PNG](https://bitbucket.org/repo/kM5M6MM/images/1757541522-Seven_links.PNG)

* The *chicago_regional.xml* file describes the chicago regional network, obtained from [this github repository](https://github.com/bstabler/TransportationNetworks/tree/master/chicago-regional).