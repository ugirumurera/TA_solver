# This is an implementation of the Method of Successive Averages used to solved traffic assignment problems

from __future__ import division
import numpy as np
from Solvers.All_or_Nothing_Function import all_or_nothing
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Data_Types.Path_Costs_Class import Path_Costs_class
from Error_Distance_to_Nash_Calculation import distance_to_Nash
import timeit

from copy import copy, deepcopy

#from mpi4py import MPI

# od is used in decomposition mode, where od is the subset of origin-destination pairs to consider for one
# decomposition subproblem
# Added od_out_indices to be used in the parallel version on the algorithm
# od_out_indices are the indices in the assignment vector that is not modified by the current subproblem
# Timer is used to calculate the time spent in path costs evaluation

def Method_of_Successive_Averages_Solver(model_manager, T, sampling_dt, od = None, od_out_indices = None,
                                         init_assignment = None, max_iter=1000, display=1, stop=1e-2, timer = None):

    # In this case, x_k is a demand assignment object that maps demand to paths
    # Constructing the x_0, the initial demand assignment, where all the demand for an OD is assigned to one path

    num_steps = int(T/sampling_dt)

    # If no subset of od provided, get od from the model manager
    if od is None:
        od = list(model_manager.get_OD_Matrix(num_steps, sampling_dt))

    # Initializing the demand assignment only if the assignment variable is None
    if init_assignment is None:
        # We first create a list of paths from the traffic_scenario
        path_list = dict()
        commodity_list = list(model_manager.otm_api.get_commodity_ids())
        init_assignment = Demand_Assignment_class(path_list,commodity_list,
                                         num_steps, sampling_dt)

        # Populating the Demand Assignment, based on the paths associated with ODs
        for o in od:
            comm_id = o.get_comm_id()
            od_path_list = o.get_path_list()
            path_list.update(od_path_list)
            for key in od_path_list.keys():
                demand = np.zeros(num_steps)
                init_assignment.set_all_demands_on_path_comm(key, comm_id, demand)

        assignment, start_cost = all_or_nothing(model_manager, init_assignment, od, None, sampling_dt * num_steps,
                                                timer = timer)

    # Only call the first all or nothing if the given assignment is empty (all zeros)
    else:
        init_vector = np.asarray(init_assignment.vector_assignment())

        if np.count_nonzero(init_vector) == 0:
            assignment, start_cost = all_or_nothing(model_manager, init_assignment, od, None,
                                                    sampling_dt*num_steps, timer = timer)
        else:
            commodity_list = init_assignment.get_commodity_list()
            num_steps = init_assignment.get_num_time_step()
            path_list = init_assignment.get_path_list()
            assignment = Demand_Assignment_class(path_list, commodity_list,
                                                   num_steps, sampling_dt)
            assignment.set_all_demands(init_assignment.get_all_demands())

    prev_error = -1
    assignment_vector_to_return = None
    x_assignment_vector = None

    if od_out_indices is not None:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        temp_vector = np.asarray(assignment.vector_assignment())
        x_assignment_vector = np.zeros(len(temp_vector))

        # First zero out the values corresponding to other subproblems
        temp_vector[od_out_indices] = 0

        # Combine assignment from all subproblems into ass_vector
        start_time1 = timeit.default_timer()
        comm.Allreduce(temp_vector, x_assignment_vector, op=MPI.SUM)
        elapsed1 = timeit.default_timer() - start_time1

        # Update assignment with the combine assignment vector
        assignment.set_demand_with_vector(x_assignment_vector)

    for i in range(max_iter):

        #start_time2 = timeit.default_timer()
        # All_or_nothing assignment
        y_assignment, current_path_costs = all_or_nothing(model_manager, assignment, od, None, sampling_dt*num_steps,
                                                          timer = timer)

        #elapsed2 = timeit.default_timer() - start_time2
        #print ("All_or_Nothing took %s seconds" % elapsed2)
        #current_path_costs.print_all()

        # Calculating the error
        current_cost_vector = np.asarray(current_path_costs.vector_path_costs())

        if x_assignment_vector is None: x_assignment_vector = np.asarray(assignment.vector_assignment())

        # When in parallel strategy, the y_assignment_vector has to be combined from all subproblems
        # If we are doing the parallel strategy, then od_out_indices is not None
        if od_out_indices is not None:
            from mpi4py import MPI
            comm = MPI.COMM_WORLD
            y_temp_vector = np.asarray(y_assignment.vector_assignment())
            y_assignment_vector = np.zeros(len(y_temp_vector))

            # First zero out the values corresponding to other subproblems
            y_temp_vector[od_out_indices] = 0

            # Combine assignment from all subproblems into ass_vector
            start_time1 = timeit.default_timer()
            # Combine assignment from all subproblems into ass_vector
            comm.Allreduce(y_temp_vector, y_assignment_vector, op=MPI.SUM)
            elapsed1 = timeit.default_timer() - start_time1
            if display == 1: print ("Communication took  %s seconds" % elapsed1)

        else:
            y_assignment_vector = np.asarray(y_assignment.vector_assignment())

        error = np.abs(np.dot(current_cost_vector, y_assignment_vector - x_assignment_vector)/
                       np.dot(y_assignment_vector,current_cost_vector))

        #error = distance_to_Nash(assignment,current_path_costs,od)

        if prev_error == -1 or prev_error > error:
            prev_error = error
            assignment_vector_to_return = copy(x_assignment_vector)

        if error < stop:
            if display == 1: print "MSA Stop with error: ", error
            return assignment, x_assignment_vector

        if display == 1: print "MSA iteration: ", i, ", error: ", error

        d_assignment = y_assignment_vector-x_assignment_vector

        #Step size equals t0 1/k, where k is the iteration number
        s = 1/(i+1)

        x_assignment_vector = x_assignment_vector + s*d_assignment
        assignment.set_demand_with_vector(x_assignment_vector)

        #elapsed2 = timeit.default_timer() - start_time2
        #print ("One Iteration took %s seconds" % elapsed2)
        # current_path_costs.print_all()

    assignment.set_demand_with_vector(assignment_vector_to_return)
    return assignment, assignment_vector_to_return

