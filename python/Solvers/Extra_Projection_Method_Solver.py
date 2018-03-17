from __future__ import division
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Solvers.Method_Successive_Averages_Solver import Method_of_Successive_Averages_Solver
from Solvers.Path_Based_Frank_Wolfe_Solver import all_or_nothing, Path_Based_Frank_Wolfe_Solver
from Solvers.Projection_onto_Simplex import Projection_onto_Simplex, Projection_onto_Simplex_old
import numpy as np
import timeit
from copy import copy

def Extra_Projection_Method_Solver(model_manager, T, sampling_dt,od = None, assignment = None, max_iter=100, display=1, stopping=1e-2):

    # In this case, x_k is a demand assignment object that maps demand to paths
    # If no subset of od provided, get od from the model manager
    if od is None: od = model_manager.beats_api.get_od_info()

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

    # Initialize the algorithm with the solution returned by Method_of_Successive_Averages
    x_k_assignment, assignment_vector = Method_of_Successive_Averages_Solver(model_manager, T, sampling_dt, od,
                                                                             assignment, max_iter=50)

    # If assignment is None, then return from the solver
    if x_k_assignment is None:
        print "Demand dt is less than sampling dt, or demand not specified properly"
        return None, None
    # tau, sigma and epslon parameters used in the Extra Projection Method
    tau = 0.5*100000
    sigma = 0.9
    epslon = 0.025

    # Keep track of the error seen, so that if there is not change for m iteration, the algorithm stops
    previous_error = -1
    count = 0
    m = 5
    x_k_assignment_vector = None

    for i in range(max_iter):
        # Step 1: Determining Z_k
        # get coefficients for cost function
        z_k_assignment,new_tau = project_modified_assignment(model_manager, T, tau, x_k_assignment, od)
        tau = new_tau
        # Step 2: Determining x_k=1
        new_x_k_assignment,new_tau = project_modified_assignment(model_manager, T, tau, z_k_assignment, od)

        tau = new_tau

        # Step 3: Calculating the error
        # All_or_nothing assignment
        new_theta_assignment, current_path_costs = all_or_nothing(model_manager, new_x_k_assignment, od, None, sampling_dt*num_steps)
        theta_assignment, theta_path_costs = all_or_nothing(model_manager, x_k_assignment, od, None, sampling_dt*num_steps)


        # Calculating the error
        current_cost_vector = np.asarray(current_path_costs.vector_path_costs())
        x_k_assignment_vector = np.asarray(x_k_assignment.vector_assignment())
        new_x_k_assignment_vector = np.asarray(new_x_k_assignment.vector_assignment())
        new_thetha_assignment_vector = np.asarray(new_theta_assignment.vector_assignment())

        error = np.abs(np.dot(current_cost_vector, new_thetha_assignment_vector - new_x_k_assignment_vector)/
                      np.dot(new_thetha_assignment_vector,current_cost_vector))
        #error = np.abs(np.dot(1/3600*current_cost_vector, new_thetha_assignment_vector - new_x_k_assignment_vector))


        print "EPM iteration: ", i, ", error: ", error
        if error < stopping:
            print "Stop with error: ", error
            return new_x_k_assignment, x_k_assignment_vector

        #keeping track of the error values seen
        if(previous_error == -1):previous_error = error
        elif(previous_error == error): count += 1
        else:
            previous_error = error
            count = 1

        if count > m:
            print "Error did not change for the past ", m, " iterations"
            return new_x_k_assignment, x_k_assignment_vector

        # Update tau as needed
        old_cost_vector = np.asarray(theta_path_costs.vector_path_costs())
        theta_assignment_vector = np.asarray(theta_assignment.vector_assignment())
        theta_value = np.dot(old_cost_vector,np.subtract(theta_assignment_vector,x_k_assignment_vector))
        new_theta_value = np.dot(current_cost_vector,np.subtract(new_thetha_assignment_vector,new_x_k_assignment_vector))
        mod_theta_assignment = epslon * np.abs(theta_value)
        if (new_theta_value < theta_value) and \
                np.abs(np.subtract(new_theta_value,theta_value)) > mod_theta_assignment:
            tau = tau * sigma

        # Otherwise, we update x_k_assignment and go back to step 1
        x_k_assignment.set_demand_with_vector(new_x_k_assignment_vector)

    return x_k_assignment, x_k_assignment_vector

# Projecting the modified assignment into a simplex
def project_modified_assignment(model_manager, T, tau, x_interm1, od):
    # Populating the Demand Assignment, based on the paths associated with ODs
    path_costs = model_manager.evaluate(x_interm1, T, initial_state=None)
    num_steps = x_interm1.get_num_time_step()
    stuck_flag = True
    count = 0   # Counts how many times we have gone through the while loop
    mutiple = 10    # Multiple to use on tau

    while stuck_flag:
        stuck_flag = False
        tau = tau /(mutiple**count)
        for o in od:
            od_demand_seq = list()
            od_cost_seq = list()
            od_keys_seq = list()
            comm_id = o.get_commodity_id()

            # Check if the number of paths is greater than 1
            if len(o.get_subnetworks()) == 1:
                break

            # Get the demand and cost corresponding to the OD
            for path in o.get_subnetworks():
                '''
                if od_demand_val is None:
                od_demand_seq.append(np.array(x_interm1.get_all_demands_on_path_comm(path.getId(),comm_id)))
                od_cost_seq.append(np.array(path_costs.get_all_costs_on_path_comm(path.getId(),comm_id)))
                od_keys_seq.append((path.getId(),comm_id))
                else:
                '''
                temp_demand = np.array(x_interm1.get_all_demands_on_path_comm(path.getId(),comm_id))
                temp_cost = np.array(path_costs.get_all_costs_on_path_comm(path.getId(),comm_id))
                od_demand_seq.append(temp_demand)
                od_cost_seq.append(temp_cost)
                od_keys_seq.append((path.getId(),comm_id))

            #We stack arrays to create matrices
            od_demand_val = np.stack(od_demand_seq)
            od_cost_val = np.stack(od_cost_seq)
            od_keys = np.stack(od_keys_seq)
            od_temp = np.subtract(od_demand_val,tau*od_cost_val)
            od_projected_val = np.zeros(od_temp.shape)

            # Here now we start the projection
            for n in range(num_steps):
                #od_projected_val[:, n] = Projection_onto_Simplex(od_temp[:, n], sum(od_demand_val[:, n]))
                projected_values = Projection_onto_Simplex(od_temp[:, n], sum(od_demand_val[:, n]))

                if projected_values is not None:
                    od_projected_val[:, n] = copy(projected_values)
                else:
                    stuck_flag = True
                    break

                #od_projected_val[:, n] =  Projection_onto_Simplex(od_temp[:, n], sum(od_demand_val[:, n]))

            #change the demand assignment
            if not stuck_flag:
                for i in range(od_projected_val.shape[0]):
                    x_interm1.set_all_demands_on_path_comm(od_keys[i][0], od_keys[i][1], od_projected_val[i,:])
            else:
                break
        count += 1
    return x_interm1, tau