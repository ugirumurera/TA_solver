#This script combines the traffic model, cost function, and solver into one program to solve a
#particular Traffic Assignment Problem

# When running on windows machine, first launch the java code Entry_Point_BeATS.java that is under 'beats-tools/java/py4jbeats/src/main/java'
# And comment out the portion marked for linux system

from Cost_Functions.BPR_Function import BPR_Function_class
from Traffic_Models.Static_Model import Static_Model_Class

from Solvers.Solver import Solver_class


#==========================================================================================
# This code is used on any linux systems to self start the Entry_Point_BeATS java code
# This code launches a java server that allow to use Beasts java object
from subprocess import call
import os
import sys
import signal
import time

jar_file_name = 'py4jbeats-1.0-SNAPSHOT-jar-with-dependencies.jar'
port_number = '25335'

pid = os.fork()

os_pid1 = os.getpid()

if pid == 0:
    os_pid = os.getpid()
    print(os_pid)
    print "child: Spawning Java"
    retcode = call(['java', '-jar', jar_file_name, port_number])
    print "Exiting"
    sys.exit()

#Here we wait for 0.5 sec to allow the java server to start
time.sleep(0.5)

#End of Linux specific code
#======================================================================================

#Inputs from the user or some input file; Location of the scenario configfile
configfile = '/global/u2/j/juliette/TA/DTA_with_Beats/VI_Solver/Configfiles/Example1.xml'
#configfile =  'C:/Users/Juliette Ugirumurera/Documents/Post-Doc/beats-tools/python/VI Solver/Configfiles/Example1.xml'
#coefficients = {0L:[1,0,0,0,1],1L:[1,0,0,0,1],2L:[10,0,0,0,1000]}
coefficients = {0L:[1,0,0,0,1],1L:[1,0,0,0,1],2L:[5,0,0,0,5], 3L:[2,0,0,0,2], 4L:[2,0,0,0,2], 5L:[1,0,0,0,1], 6L:[5,0,0,0,5]}

scenario  = Static_Model_Class(configfile)

if(scenario.beats_api != None):
    print(scenario.Model_Gradient(scenario.beats_api.get_demands()))
    print(scenario.Run_Model(scenario.beats_api.get_demands()))
    Travel_Time_Function = BPR_Function_class(coefficients)
    scenario_solver =  Solver_class(scenario, Travel_Time_Function)
    print(scenario_solver.Solver_function())


#===========================================================================================
# This is used on linux systems to kill the started java process
print("Terminating the java process")
os.kill(0, signal.SIGTERM)
#============================================================================================
