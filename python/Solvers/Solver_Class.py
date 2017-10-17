#This class combines all solvers, either variational inequality, or optimization solver
#It combines an instance of a traffic model with a solver depending whether it is an optimization problem
#or a variational inequality problem

from __future__ import division
from Frank_Wolfe_Solver_Static import Frank_Wolfe_Solver
from Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver
from Method_Successive_Averages_Solver import Method_of_Successive_Averages_Solver
import timeit
import numpy as np
#from Decomposition_Solver import Decomposition_Solver

class Solver_class():
    def __init__(self, model_manager):
        self.model_manager = model_manager

    #This is the function that actually solves a problem
    #The Dec parameter indicates whether we are going to use decomposition or not
    def Solver_function(self, T, sampling_dt, solver_name = None, Dec = False, number_of_subproblems = 1):
        #if problem can be solved as an optimization problem:
        assignment_seq = None
        frank_sol = None

        #call an optimization algorithm like Frank-Wolfe
        start_time1 = timeit.default_timer()
        if(solver_name == "MSA"):
            assignment_seq = Method_of_Successive_Averages_Solver(self.model_manager, T, sampling_dt)
        else:
            assignment_seq = Path_Based_Frank_Wolfe_Solver(self.model_manager, T, sampling_dt)

        elapsed1 = timeit.default_timer() - start_time1
        print ("Sequential Path-based took  %s seconds" % elapsed1)

        '''
        assignment_dec = None
        if Dec == True:
            start_time1 = timeit.default_timer()
            assignment_dec, error = Decomposition_Solver(self.traffic_scenario, self.Cost_Function, number_of_subproblems)
            print "Decomposition finished with error ", error
            elapsed1 = timeit.default_timer() - start_time1
            print ("Decomposition Path-based took  %s seconds" % elapsed1)


        print "\n"
        start_time1 = timeit.default_timer()
        frank_sol = Frank_Wolfe_Solver(self.model_manager)
        elapsed1 = timeit.default_timer() - start_time1
        print ("FW link-based took  %s seconds" % elapsed1)
        #Call a algorithm to solve the variational inequality problem - to be developed
        '''
        
        return assignment_seq, frank_sol

    # This function receives the solution assignment and the corresponding path_costs and returns the distance to Nash
    # calculated as of the summation of the excess travel cost for flows on paths compared to the travel cost on the
    # shortest paths for an origin-destination pair
    def distance_to_Nash(self, sol_assignment, path_costs, sampling_dt):
        num_steps = sol_assignment.get_num_time_step()
        od = self.model_manager.beats_api.get_od_info()
        dist_to_Nash = 0

        # For each OD, we are going to move its demand to the shortest path at current iteration
        for o in od:
            min_cost = 0
            comm_id = o.get_commodity_id()

            for i in range(num_steps):
                num_paths = len(o.get_subnetworks())
                min_path_id = -1
                cost_on_paths = np.zeros(num_paths)
                demand_on_paths = np.zeros(num_paths)
                j = 0   # index in cost_on_paths and demand_on_paths arrays

                for path in o.get_subnetworks():
                    if min_path_id == -1:
                        min_path_id = path.getId()
                        min_cost = path_costs.get_cost_at_path_comm_time(min_path_id, comm_id, i)
                    elif min_cost > path_costs.get_cost_at_path_comm_time(path.getId(), comm_id, i):
                        min_path_id = path.getId()
                        min_cost = path_costs.get_cost_at_path_comm_time(min_path_id, comm_id, i)

                    # Collecting the costs and demands on paths for od o
                    cost_on_paths[j] = path_costs.get_cost_at_path_comm_time(path.getId(), comm_id, i)
                    demand_on_paths[j] = sol_assignment.get_demand_at_path_comm_time(path.getId(), comm_id, i)
                    j += 1

                # Adding the excess travel cost to the distance from Nash
                min_costs = np.ones(len(cost_on_paths))*min_cost

                dist_to_Nash += sum(np.abs(((cost_on_paths-min_costs)/3600)*demand_on_paths))

        return dist_to_Nash