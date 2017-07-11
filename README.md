# Description #
This a general software framework for solving Traffic Assignment problems, both static and dynamic, utilizing the [Beats Simulator api](https://bitbucket.org/gcgomes/beats-tools) to express/encode traffic scenarios. 

# SET UP #

**Step 1.** Install the [JAVA 8](http://www.oracle.com/technetwork/java/javase/downloads/index.html) JDK on your computer.
[This](https://www.java.com/en/download/help/version_manual.xml) will show you how to check your current version of JAVA.

**Step 2.** Install Python on your system if not already installed. Codes was developed with Python 2.7.

** Step 3.** Install [Python-igraph](http://igraph.org/python/#pyinstall). This library is used by numerical algorithms such as Frank-Wolfe. You will need it to run the tests.

**Step 4.** Send and email to Gabriel Gomes (gomes@path.berkeley.edu) requesting access to the TA solver. Include in this email your Bitbucket user name. You will receive two things:

a) An invitation to the BeATS Dropbox folder. From this folder you will need the py4jbeats jar file. py4jbeats allows to utilize the Beats simulator api to encode traffic scenarios. Sync this Dropbox folder with your computer so that you always have the latest version of the simulator. 

b) An invitation to the ta_solver repo on Bitbucket. Fork and clone this repo. 

**Step 5.** Run Test to validate installation:
Run **Test_on_Windows.py** for windows systems, and **Test_on_Linux.py** for Linux systems. This will initialize a small instance of the static traffic assignment problem and solve it using the Frank-Wolfe algorithm. Installation successful if program prints out "Installation Successful!" at the end.