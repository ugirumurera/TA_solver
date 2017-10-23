# Here is implemented the Modified_Projection_Method (MPM) as presented by Nagurney, 1999 (Network Economics)
# The algorithm solves quadratic subproblems in each iteration, for which we use the Path_Based_Frank_Wolfe Algorithm

from __future__ import division
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Data_Types.Path_Costs_Class import Path_Costs_class
from Path_Based_Frank_Wolfe_Solver import all_or_nothing, Path_Based_Frank_Wolfe_Solver
from copy import copy, deepcopy
import numpy as np
import timeit


def Modified_Projection_Method_Solver(model_manager, T, sampling_dt,max_iter=1000, display=1, stop=2):

    # In this case, x_k is a demand assignment object that maps demand to paths
    # Constructing the x_0, the initial demand assignment, where all the demand for an OD is assigned to one path
    # We first create a list of paths from the traffic_scenario
    path_list = dict()
    od = model_manager.beats_api.get_od_info()
    num_steps = int(T/sampling_dt)

    # Initializing the demand assignment
    commodity_list = list(model_manager.beats_api.get_commodity_ids())
    x_k_assignment = Demand_Assignment_class(path_list,commodity_list,
                                         num_steps, sampling_dt)

    # Populating the Demand Assignment, based on the paths associated with ODs
    for o in od:
        count = 0
        comm_id = o.get_commodity_id()

        demand_api = [item * 3600 for item in o.get_total_demand_vps().getValues()]
        demand_api = np.asarray(demand_api)
        demand_size = len(demand_api)
        demand_dt = o.get_total_demand_vps().getDt()

        # Before assigning the demand, we want to make sure it can be properly distributed given the number of
        # Time step in our problem
        if (sampling_dt > demand_dt or demand_dt % sampling_dt > 0) and (demand_size > 1):
            print "Demand specified in xml cannot not be properly divided among time steps"
            return
        #if demand_size > num_steps or num_steps % len(demand_api) != 0:
            #print "Demand specified in xml cannot not be properly divided among time steps"
            #return

        for path in o.get_subnetworks():
            path_list[path.getId()] = path.get_link_ids()
            demand = np.zeros(num_steps)
            x_k_assignment.set_all_demands_on_path_comm(path.getId(), comm_id, demand)

    # x_interm is the initial solution: Step 0
    x_k_assignment, start_cost = all_or_nothing(model_manager, x_k_assignment, od, None, sampling_dt*num_steps)

    # row parameter used in the modified projection method
    row = 1

    for i in range(max_iter):
        # Step 1: Determining X_bar
        # get coefficients for cost function
        coefficients = get_cost_function_coefficients(model_manager,T,row,x_k_assignment,x_k_assignment)
        x_bar_assignment = Path_Based_Frank_Wolfe_Solver(model_manager, T, sampling_dt, cost_function, coefficients)
        #print (cost_function(x_bar_assignment,coefficients))

        # Step 2: Determining x_k=1
        new_coefficients = get_cost_function_coefficients(model_manager,T,row,x_bar_assignment,x_k_assignment)
        new_x_k_assignment = Path_Based_Frank_Wolfe_Solver(model_manager, T, sampling_dt, cost_function, new_coefficients)
        #print (cost_function(new_x_k_assignment, new_coefficients))

        # Step 3
        # Calculating the error
        x_k_assignment_vector = np.asarray(x_k_assignment.vector_assignment())
        new_x_k_assignment_vector = np.asarray(new_x_k_assignment.vector_assignment())

        error = max(np.abs(x_k_assignment_vector- new_x_k_assignment_vector))
        print "MPM iteration: ", i, ", error: ", error
        if error < stop:
            print "Stop with error: ", error
            return new_x_k_assignment

        # Otherwise, we update x_k_assignment and go back to step 1
        x_k_assignment.set_demand_with_vector(new_x_k_assignment_vector)


# This function calculates the coefficient of the cost function for quadratic programming subproblem of the Modified_Projection_Method
# Function Equation = x* + [row*F(x_interm1) - x_interm2], where x* is the varying assignment, x_interm1 and x_interm2 are intermidiate
# demand assignments. The shape of the coefficient object will be m by n:
# m = number of paths in our demand assignment x number of timesteps in problem
# n = 2, number of an affine function (a1*x + a0), a1 and a0 are 2 different coefficents

def get_cost_function_coefficients(model_manager, T, row, x_interm1, x_interm2):
    m = x_interm1.get_num_entries() * x_interm1.get_num_time_step()

    # Calculating F(x_interm1)
    path_costs = model_manager.evaluate(x_interm1, T, initial_state = None)
    cost_vector = np.asarray(path_costs.vector_path_costs())
    #Calculating a0
    x_interm2_vector = np.asarray(x_interm2.vector_assignment())
    a0 = row*cost_vector - x_interm2_vector

    a1 = np.ones(m)     # a1 is all ones since x* has no coefficient in the cost function
    coefficients = np.zeros((m,2))
    coefficients[:,0] = a0
    coefficients[:,1] = a1
    return coefficients

# This function calculates the cost function for quadratic programming subproblem of the Modified_Projection_Method
# Function Equation = x* + [row*F(x_interm1) - x_interm2], where x* is the varying assignment, x_interm1 and x_interm2 are intermidiate
# demand assignments
def cost_function(assignment, coefficients):
    x_vector = np.asarray(assignment.vector_assignment())
    y_x = np.multiply(coefficients[:,1],x_vector)
    cost_vector = coefficients[:,0] + np.multiply(coefficients[:,1],x_vector)
    return cost_vector
