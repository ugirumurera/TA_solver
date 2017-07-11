# Description #
This a general software framework for solving traffic assignment problems, both static and dynamic, utilizing the [BeATS API](https://bitbucket.org/gcgomes/beats-sim) to encode traffic scenarios. 

# SET UP #

**Step 1.** Install the [JAVA 8](http://www.oracle.com/technetwork/java/javase/downloads/index.html) JDK on your computer.
[This](https://www.java.com/en/download/help/version_manual.xml) will show you how to check your current version of JAVA.

**Step 2.** Install Python on your system if not already installed. Codes was developed with Python 2.7.

** Step 3.** Install [Python-igraph](http://igraph.org/python/#pyinstall). This library is necessary to validate installation, by solving a small static traffic assignment problem using the Frank-Wolfe algorithm.

**Step 4.** Send an email to Gabriel Gomes (gomes@path.berkeley.edu) requesting access to the BeATS Dropbox folder. Please include your Dropbox user name. This folder contains a jar file named py4jbeats-1.0-SNAPSHOT-jar-with-dependencies.jar. This file packages both the BeATS API as well as a utility called py4j which establishes a connection between Python and Java. You should have Dropbox sync this folder with your computer so that you always have the latest version of the BeATS API.

**Step 5.** Run Test to validate installation:

* On Windows: Run **Test_on_Windows.py**
* On Linux/MacOS: Run **Test_on_Linux.py**

This will initialize a small instance of the static traffic assignment problem and solve it using the Frank-Wolfe algorithm. 

It will print "Installation Successful!" to the console if everything goes well. 

# Contacts #

* **Juliette Ugirumurera**: julymurera@gmail.com
* **Gabriel Gomes**: gomes@path.berkeley.edu