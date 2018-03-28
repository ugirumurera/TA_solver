# This script initializes a static traffic model, a cost function, and a solver to solve a
# Static Traffic Assignment Problem using the Frank-Wolfe algorithm

from python.Cost_Functions.BPR_Function import BPR_Function_class
from python.Traffic_Models import Static_Model_Class
from python.Solvers.Solver_Class import Solver_class
from py4j.java_gateway import JavaGateway,GatewayParameters

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()


# ==========================================================================================
# This code is used on any Windows systems to self start the Entry_Point_BeATS java code
# This code launches a java server that allow to use Beasts java object
from subprocess import call
import os
import sys
import time
import inspect

this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
jar_file_name = os.path.join(this_folder, 'py4jbeats-1.0-SNAPSHOT-jar-with-dependencies.jar')

port_number = '25335'
process_id = 0

if rank == 0:
    pid = os.fork()

    os_pid1 = os.getpid()

    if pid == 0:
        os_pid = os.getpid()
        print(os_pid)
        print("Staring up the java gateway to access the Beats object")
        retcode = call(['java', '-jar', jar_file_name, port_number])
        print "Exiting"
        sys.exit()

    # Here we wait for 0.5 sec to allow the java server to start
    time.sleep(1)

    # End of Linux specific code
    # ======================================================================================
else:
    time.sleep(5)

# Contains local path to input configfile, for the three_links.xml network
configfile = os.path.join(this_folder,os.path.pardir,'configfiles','seven_links.xml')

#coefficients = {0L:[1,0,0,0,1],1L:[1,0,0,0,1],2L:[2,0,0,0,2]}
coefficients = {0L:[1,0,0,0,1],1L:[1,0,0,0,1],2L:[5,0,0,0,5], 3L:[2,0,0,0,2], 4L:[2,0,0,0,2], 5L:[1,0,0,0,1], 6L:[5,0,0,0,5]}

port_number = int(port_number)
gateway = JavaGateway(gateway_parameters=GatewayParameters(port=port_number))
beats_api = gateway.entry_point.get_BeATS_API()
beats_api.load(configfile)

# This initializes an instance of static model from configfile
scenario  = Static_Model_Class(beats_api, 1, 1)

# If scenario.beast_api is none, it means the configfile provided was not valid for the particular traffic model type
if(scenario.beats_api != None):
    print("\nSuccessfully initialized a static model")

    time_period = 1  # Only have one time period for static model
    paths_list = list(scenario.beats_api.get_path_ids())
    link_list = list(scenario.beats_api.get_link_ids())
    commodity_list = list(scenario.beats_api.get_commodity_ids())

    # Initialize the BPR cost function
    BPR_cost_function = BPR_Function_class(coefficients)


    print("\nRunning Frank-Wolfe on the three links network")
    scenario_solver = Solver_class(scenario, BPR_cost_function)
    Dec = True  # Indicates that Decomposition is going to be used
    number_of_subproblems = 2
    assignment_seq, assignment_dec = scenario_solver.Solver_function(Dec, number_of_subproblems)
    #assignment, flow_sol = scenario_solver.Solver_function()


    # Cost resulting from the path_based Frank-Wolfe
    link_states = scenario.Run_Model(assignment_seq)
    cost_seq_based = BPR_cost_function.evaluate_BPR_Potential(link_states)
    
    link_states1 = scenario.Run_Model(assignment_dec)
    # Cost resulting from link-based Frank-Wolfe
    cost_dec_based = BPR_cost_function.evaluate_BPR_Potential(link_states1)

    #link_states.print_all()
    #link_states1.print_all()
    print "seq-based cost: ", cost_seq_based
    print "dec-based cost: ", cost_dec_based


if rank == 0:
    # Want to stop the java server
    # ===========================================================================================
    # This is used on linux systems to kill the started java process
    print("Terminating the java process")
    #os.kill(0, signal.SIGTERM)
    # ============================================================================================


