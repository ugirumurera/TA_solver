# This is an implementation of the Method of Successive Averages used to solved traffic assignment problems

from __future__ import division
import numpy as np
from Solvers.All_or_Nothing_Function import all_or_nothing
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Data_Types.Path_Costs_Class import Path_Costs_class
import timeit

# od is used in decomposition mode, where od is the subset of origin-destination pairs to consider for one
# decomposition subproblem
def Method_of_Successive_Averages_Solver(model_manager, T, sampling_dt, od = None, assignment = None, max_iter=1000,
                                         display=1, stop=1e-2):

    # In this case, x_k is a demand assignment object that maps demand to paths
    # Constructing the x_0, the initial demand assignment, where all the demand for an OD is assigned to one path

    # If no subset of od provided, get od from the model manager
    if od is None: od = model_manager.beats_api.get_od_info()

    num_steps = int(T/sampling_dt)

    # Initializing the demand assignment only if the assignment variable is None
    if assignment is None:
        # We first create a list of paths from the traffic_scenario
        path_list = dict()
        commodity_list = list(model_manager.beats_api.get_commodity_ids())
        assignment = Demand_Assignment_class(path_list,commodity_list,
                                         num_steps, sampling_dt)

        # Populating the Demand Assignment, based on the paths associated with ODs
        for o in od:
            comm_id = o.get_commodity_id()

            demand_api = [item * 3600 for item in o.get_total_demand_vps().getValues()]
            demand_api = np.asarray(demand_api)
            demand_size = len(demand_api)
            demand_dt = o.get_total_demand_vps().getDt()

            # Before assigning the demand, we want to make sure it can be properly distributed given the number of
            # Time step in our problem
            if (sampling_dt > demand_dt or demand_dt % sampling_dt > 0) and (demand_size > 1):
                print "Demand specified in xml cannot not be properly divided among time steps"
                return None, None
            #if demand_size > num_steps or num_steps % len(demand_api) != 0:
                #print "Demand specified in xml cannot not be properly divided among time steps"
                #return

            for i in range(num_steps):
                paths_demand = dict()
                count = 0
                for path in o.get_subnetworks():
                    path_list[path.getId()] = path.get_link_ids()
                    if count == 0:
                        index = int(i / (num_steps / demand_size))
                        demand = o.get_total_demand_vps().get_value(index) * 3600
                        paths_demand[path.getId()] = demand
                        count += 1
                    else:
                        paths_demand[path.getId()] = 0

                # Putting all the demand on the minimum cost path
                # First set to zero all demands on all path for commodity comm_id and time_step i
                assignment.add_demand_at_comm_time_step(comm_id, i, paths_demand)

    assignment, start_cost = all_or_nothing(model_manager, assignment, od, None, sampling_dt*num_steps)
    prev_error = -1
    assignment_to_return = None
    assignment_vector_to_return = None

    for i in range(max_iter):
        # All_or_nothing assignment
        y_assignment, current_path_costs = all_or_nothing(model_manager, assignment, od, None, sampling_dt*num_steps)

        #current_path_costs.print_all()

        # Calculating the error
        current_cost_vector = np.asarray(current_path_costs.vector_path_costs())
        x_assignment_vector = np.asarray(assignment.vector_assignment())
        y_assignment_vector = np.asarray(y_assignment.vector_assignment())

        error = np.abs(np.dot(current_cost_vector, y_assignment_vector - x_assignment_vector)/
                       np.dot(y_assignment_vector,current_cost_vector))

        if prev_error == -1 or prev_error > error:
            prev_error = error
            assignment_to_return = assignment
            assignment_vector_to_return = x_assignment_vector

        print "MSA iteration: ", i, ", error: ", error
        if error < stop:
            print "Stop with error: ", error
            return assignment_to_return, assignment_vector_to_return

        d_assignment = y_assignment_vector-x_assignment_vector

        #Step size equals t0 1/k, where k is the iteration number
        s = 1/(i+1)

        x_assignment_vector = x_assignment_vector + s*d_assignment
        assignment.set_demand_with_vector(x_assignment_vector)

    return assignment_to_return, assignment_vector_to_return

