from __future__ import division
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Method_Successive_Averages_Solver import Method_of_Successive_Averages_Solver
from Path_Based_Frank_Wolfe_Solver import all_or_nothing, Path_Based_Frank_Wolfe_Solver
from Projection_onto_Simplex import Projection_onto_Simplex
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
    '''
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
    '''
    x_k_assignment = Method_of_Successive_Averages_Solver(model_manager, T, sampling_dt)
    # tau, sigma and epslon parameters used in the Extra Projection Method
    tau = 0.5*3600
    sigma = 0.9
    epslon = 0.05

    # Keep track of the error seen, so that if there is not change for m iteration, the algorithm stops
    previous_error = -1
    count = 0
    m = 5

    for i in range(max_iter):
        # Step 1: Determining Z_k
        # get coefficients for cost function
        z_k_assignment = project_modified_assignment(model_manager, T, tau, x_k_assignment)

        # Step 2: Determining x_k=1
        new_x_k_assignment = project_modified_assignment(model_manager, T, tau, z_k_assignment)

        # Step 3: Calculating the error
        # All_or_nothing assignment
        new_theta_assignment, current_path_costs = all_or_nothing(model_manager, new_x_k_assignment, od, None, sampling_dt*num_steps)
        theta_assignment, path_costs = all_or_nothing(model_manager, x_k_assignment, od, None, sampling_dt*num_steps)

        # Calculating the error
        current_cost_vector = np.asarray(current_path_costs.vector_path_costs())
        #x_k_assignment_vector = np.asarray(x_k_assignment.vector_assignment())
        new_x_k_assignment_vector = np.asarray(new_x_k_assignment.vector_assignment())
        new_thetha_assignment_vector = np.asarray(new_theta_assignment.vector_assignment())

        #error = np.abs(np.dot(current_cost_vector, new_thetha_assignment_vector - new_x_k_assignment_vector)/
        #               np.dot(new_thetha_assignment_vector,current_cost_vector))
        error = np.abs(np.dot(1/3600*current_cost_vector, new_thetha_assignment_vector - new_x_k_assignment_vector))


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

def project_modified_assignment(model_manager, T, tau, x_interm1):
    # Populating the Demand Assignment, based on the paths associated with ODs
    path_costs = model_manager.evaluate(x_interm1, T, initial_state=None)
    num_steps = x_interm1.get_num_time_step()

    for o in model_manager.beats_api.get_od_info():
        od_demand_val = None
        od_cost_val = None
        od_keys = None
        comm_id = o.get_commodity_id()

        # Check if the number of paths is greater than 1
        if len(o.get_subnetworks()) == 1:
            break

        # Get the demand and cost corresponding to the OD
        for path in o.get_subnetworks():
            if od_demand_val is None:
                od_demand_val = np.array(x_interm1.get_all_demands_on_path_comm(path.getId(),comm_id))
                od_cost_val = np.array(path_costs.get_all_costs_on_path_comm(path.getId(),comm_id))
                od_keys = (path.getId(),comm_id)
            else:
                temp_demand = np.array(x_interm1.get_all_demands_on_path_comm(path.getId(),comm_id))
                temp_cost = np.array(path_costs.get_all_costs_on_path_comm(path.getId(),comm_id))
                od_demand_val = np.stack((od_demand_val,temp_demand))
                od_cost_val = np.stack((od_cost_val,temp_cost))
                od_keys = np.stack((od_keys,(path.getId(),comm_id)))

        od_temp = np.subtract(od_demand_val, 1/3600*tau*od_cost_val)
        od_projected_val = np.zeros(od_temp.shape)

        # Here now we start the projection
        for n in range(num_steps):
            od_projected_val[:,n] = Projection_onto_Simplex(od_temp[:,n],sum(od_demand_val[:,n]))

        #change the demand assignment
        for i in range(od_projected_val.shape[0]):
            x_interm1.set_all_demands_on_path_comm(od_keys[i][0], od_keys[i][1], od_projected_val[i,:])

    return x_interm1