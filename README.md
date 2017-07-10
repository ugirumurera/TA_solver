# Description #
This a general software framework for solving Traffic Assignment problems, both static and dynamic, utilizing the [Beats Simulator api] (https://bitbucket.org/gcgomes/beats-tools) to express/encode traffic scenarios. 

# SET UP #

**Step 1.** Install the [JAVA 8](http://www.oracle.com/technetwork/java/javase/downloads/index.html) JDK on your computer.
[This](https://www.java.com/en/download/help/version_manual.xml) will show you how to check your current version of JAVA.

**Step 2.** Install Python on your system if not already installed. Codes was developed with Python 2.7.

** Step 3.** Install [Python-igraph] (http://igraph.org/python/#pyinstall). This library is necessary to validate installation, by solving a small static traffic assignment problem using the Frank-Wolfe algorithm.

**Step 4.** Request a copy of the py4jbeats jar file by[email] (mailto:gomes@me.berkeley.edu). The py4jbeats allows to utilize the Beats simulator api to encode traffic scenarios. You will receive an invitation to join a Dropbox folder containing the py4jbeats jar file. You should have Dropbox sync this folder with your computer so that you always have the latest version of the simulator. 

**Step 5.** Download or clone the ta_solver repository to your computer. For this you need a bitbucket account and access to the repo. If you do not have access, send an [email](mailto:gomes@me.berkeley.edu).

**Step 6.** Run Test to validate installation:
Run Test_on_Windows.py for windows systems, and Test_on_Linux for Linux systems. This will initialize a small instance of the static traffic assignment problem and solve it using the Frank-Wolfe algorithm. Installation successful if program prints out "Installation Successful!" at the end.