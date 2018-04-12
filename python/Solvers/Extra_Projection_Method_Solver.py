from __future__ import division
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Solvers.Method_Successive_Averages_Solver import Method_of_Successive_Averages_Solver
from Solvers.Path_Based_Frank_Wolfe_Solver import all_or_nothing, Path_Based_Frank_Wolfe_Solver
from Solvers.Projection_onto_Simplex import Projection_onto_Simplex, Projection_onto_Simplex_old
import numpy as np
from Error_Calculation import distance_to_Nash
import timeit
from copy import copy

def Extra_Projection_Method_Solver(model_manager, T, sampling_dt,od = None, od_out_indices = None, assignment = None,
                                   max_iter=1000, display=1, stopping=1e-6):

    # In this case, x_k is a demand assignment object that maps demand to paths

    num_steps = int(T/sampling_dt)

    # If no subset of od provided, get od from the model manager
    if od is None: od = list(model_manager.get_OD_Matrix(num_steps, sampling_dt))

    # Initialize the algorithm with the solution returned by Method_of_Successive_Averages
    x_k_assignment, x_k_assignment_vector = Method_of_Successive_Averages_Solver(model_manager, T, sampling_dt, od,od_out_indices,
                                                                             assignment, max_iter=100, stop=1e-5)

    # If assignment is None, then return from the solver
    if x_k_assignment is None:
        print "Demand dt is less than sampling dt, or demand not specified properly"
        return None, None
    # tau, sigma and epslon parameters used in the Extra Projection Method
    tau = 0.05*10000
    sigma = 0.9
    epslon = 0.025

    # Keep track of the error seen, so that if there is not change for m iteration, the algorithm stops
    previous_error = -1
    count = 0
    m = 5

    thetha_assignment, current_cost_vector,thetha_assignment_vector = None,None,None

    for i in range(max_iter):
        if thetha_assignment is None:
            # First check if the error is low enough to terminate
            theta_assignment, current_path_costs = all_or_nothing(model_manager, x_k_assignment, od, None,
                                                                  sampling_dt * num_steps)

            #Vectors to be used in error calculation
            current_cost_vector = np.asarray(current_path_costs.vector_path_costs())
            thetha_assignment_vector = np.asarray(theta_assignment.vector_assignment())

        error = np.abs(np.dot(current_cost_vector, thetha_assignment_vector - x_k_assignment_vector)/
                      np.dot(thetha_assignment_vector,current_cost_vector))

        if error < stopping:
            print "EPM Stop with error: ", error
            #path_costs = model_manager.evaluate(x_k_assignment, T)

            #path_costs.print_all()

            #print current_cost_vector

            #print "\n"
            return x_k_assignment, x_k_assignment_vector

        # If we did not terminate, print current error
        print "EPM iteration: ", i, ", error: ", error

        #keeping track of the error values seen
        if(previous_error == -1):previous_error = error
        elif(previous_error == error): count += 1
        else:
            previous_error = error
            count = 1

        if count > m:
            print "Error did not change for the past ", m, " iterations"
            return x_k_assignment, x_k_assignment_vector


        # Step 1: Determining Z_k
        # get coefficients for cost function
        z_k_assignment,new_tau = project_modified_assignment(model_manager, T, tau, x_k_assignment, od)
        tau = new_tau
        # Step 2: Determining x_k=1
        new_x_k_assignment,new_tau = project_modified_assignment(model_manager, T, tau, z_k_assignment, od)

        tau = new_tau

        # Check if we need to change tau
        # All_or_nothing assignment
        new_theta_assignment, new_path_costs = all_or_nothing(model_manager, new_x_k_assignment, od, None, sampling_dt*num_steps)

        # Getting the vectors
        new_x_k_assignment_vector = np.asarray(new_x_k_assignment.vector_assignment())
        new_thetha_assignment_vector = np.asarray(new_theta_assignment.vector_assignment())

        # Update tau as needed
        old_cost_vector = np.asarray(model_manager.evaluate(x_k_assignment, T,
                                                            initial_state=None).vector_path_costs())
        new_cost_vector = np.asarray(model_manager.evaluate(new_x_k_assignment, T,
                                                            initial_state=None).vector_path_costs())
        old_theta = np.dot(old_cost_vector,np.subtract(thetha_assignment_vector, x_k_assignment_vector))
        new_theta = np.dot(new_cost_vector, np.subtract(new_thetha_assignment_vector, new_x_k_assignment_vector))
        new_theta_value = np.abs(np.subtract(new_theta,old_theta))
        mod_theta_assignment = epslon * np.abs(old_theta)

        if (new_theta < old_theta) and \
                new_theta_value > mod_theta_assignment:
            tau = tau * sigma

        # Otherwise, we update x_k_assignment and go back to error checking
        x_k_assignment.set_demand_with_vector(new_x_k_assignment_vector)

        thetha_assignment_vector = copy(new_thetha_assignment_vector)
        x_k_assignment_vector = copy(new_x_k_assignment_vector)
        current_cost_vector = np.asarray(new_path_costs.vector_path_costs())

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
            comm_id = o.get_comm_id()

            path_dict = o.get_path_list()

            # Check if the number of paths is greater than 1
            #if len(path_dict.keys()) == 1:
            #    break

            # Get the demand and cost corresponding to the OD
            for path_id in path_dict.keys():
                temp_demand = np.array(x_interm1.get_all_demands_on_path_comm(path_id,comm_id))
                temp_cost = np.array(path_costs.get_all_costs_on_path_comm(path_id,comm_id))
                od_demand_seq.append(temp_demand)
                od_cost_seq.append(temp_cost)
                od_keys_seq.append((path_id,comm_id))

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