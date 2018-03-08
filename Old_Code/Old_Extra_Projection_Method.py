from __future__ import division
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Data_Types.Path_Costs_Class import Path_Costs_class
from Path_Based_Frank_Wolfe_Solver import all_or_nothing, Path_Based_Frank_Wolfe_Solver
from copy import copy, deepcopy
import numpy as np
import timeit
import gc

def Extra_Projection_Method_Solver(model_manager, T, sampling_dt,max_iter=1000, display=1, stopping=1e-2):

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

    # tau, sigma and epslon parameters used in the Extra Projection Method
    tau = 0.5
    sigma = 0.9
    epslon = 0.05

    # Keep track of the error seen, so that if there is not change for m iteration, the algorithm stops
    previous_error = -1
    count = 0
    m = 5

    for i in range(max_iter):
        # Step 1: Determining Z_k
        # get coefficients for cost function
        coefficients = get_cost_function_coefficients(model_manager,T,tau,x_k_assignment)
        z_k_assignment = Path_Based_Frank_Wolfe_Solver(model_manager, T, sampling_dt, cost_function, coefficients)
        #print (cost_function(z_k_assignment,coefficients))

        # Step 2: Determining x_k=1
        new_coefficients = get_cost_function_coefficients(model_manager,T,tau,z_k_assignment)
        new_x_k_assignment = Path_Based_Frank_Wolfe_Solver(model_manager, T, sampling_dt, cost_function, new_coefficients)
        #print (cost_function(new_x_k_assignment, new_coefficients))

        # Step 3: Calculating the error
        # All_or_nothing assignment
        new_theta_assignment, current_path_costs = all_or_nothing(model_manager, new_x_k_assignment, od, None, sampling_dt*num_steps)
        theta_assignment, path_costs = all_or_nothing(model_manager, x_k_assignment, od, None, sampling_dt*num_steps)

        # Calculating the error
        current_cost_vector = np.asarray(current_path_costs.vector_path_costs())
        x_assignment_vector = np.asarray(new_x_k_assignment.vector_assignment())
        new_thetha_assignment_vector = np.asarray(new_theta_assignment.vector_assignment())

        error = np.abs(np.dot(current_cost_vector, new_thetha_assignment_vector - x_assignment_vector)/
                       np.dot(new_thetha_assignment_vector,current_cost_vector))

        new_x_k_assignment_vector = np.asarray(new_x_k_assignment.vector_assignment())

        print "EPM iteration: ", i, ", error: ", error
        if error < stopping:
            print "Stop with error: ", error
            return new_x_k_assignment

        #keeping track of the error values seen
        if(previous_error == -1):previous_error = error
        elif(previous_error == error): count += 1
        else:
            previous_error = error
            count = 1

        if count > m:
            print "Error did not change for the past ", m, " iterations"
            return new_x_k_assignment

        # Otherwise, we update x_k_assignment and go back to step 1
        x_k_assignment.set_demand_with_vector(new_x_k_assignment_vector)

        # Update tau as needed
        theta_assignment_vector = np.asarray(theta_assignment.vector_assignment())
        mod_theta_assignment = epslon * np.abs(theta_assignment_vector)
        if (np.all(new_thetha_assignment_vector < theta_assignment_vector)) and \
                np.all(np.fabs(np.subtract(new_thetha_assignment_vector,theta_assignment_vector)) > mod_theta_assignment):
            tau = tau * sigma
    return x_k_assignment

# This function calculates the coefficient of the cost function for quadratic programming subproblem of the Extra_Projection_Method
# Function Equation = taw*F(x_interm1), where x_interm1 is intermidiate demand assignment.
# The shape of the coefficient object will be m by n:
# m = number of paths in our demand assignment x number of timesteps in problem
# n = 2, number of an affine function (a1*x + a0), a1 and a0 are 2 different coefficents

def get_cost_function_coefficients(model_manager, T, tau, x_interm1):
    path_costs = model_manager.evaluate(x_interm1, T, initial_state=None)
    gc.collect()
    x_interm_vector = np.asarray(x_interm1.vector_assignment())
    cost_vector = np.asarray(path_costs.vector_path_costs())
    coefficients = np.subtract(x_interm_vector,tau*1/3600*cost_vector)
    return coefficients


# This function calculates the cost function for quadratic programming subproblem of the Modified_Projection_Method
# Function Equation = (x - coefficients)^T *(x - coefficients), where x* is the varying assignment, x is the demand assignment
def cost_function(assignment, coefficients):
    x_vector = np.asarray(assignment.vector_assignment())
    cost_vector = (np.subtract(x_vector, coefficients))
    return cost_vector