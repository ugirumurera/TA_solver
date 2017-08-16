# This is a decomposition based solver for the static case
# For now it will ise Frank_Wolfe_Solver_Static as its solver

import numpy as np
from mpi4py import MPI
import math
from Frank_Wolfe_Solver_Static import Frank_Wolfe_Solver_Decomposition
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver_Dec
from copy import deepcopy, copy

def Decomposition_Solver_Static(traffic_scenario, cost_function, number_of_subproblems, epsilon = 1e-2):
    comm = MPI.COMM_WORLD
    error = -1
    # First set an initial flow assignment
    flow = np.zeros(traffic_scenario.beats_api.get_num_links(), dtype="float64")  # initial flow assignment is null
    flow_k = np.zeros(traffic_scenario.beats_api.get_num_links(), dtype="float64")

    while error == -1 or error > epsilon:
        # Divide the problem into subproblems
        # We assume that the number of subproblems is less than the number of ods
        rank = comm.Get_rank()
        size = comm.Get_size()
        od_list = list(traffic_scenario.beats_api.get_od_info())

        n = len(od_list)

        local_n_c = math.ceil(float(n) / size)  # local step but ceiled
        local_n = n / size
        remainder = n % size

        if (rank < remainder):
            local_a = rank * local_n_c
            local_b = local_a + local_n_c
            local_n = local_n_c
        else:
            local_a = (remainder) * local_n_c + (rank - remainder) * local_n
            local_b = local_a + local_n

        # The set of ods to use for the particular subproblem
        od_subset = od_list[local_a:local_b]

        # calling Frank_Wolfe on the particular subproblem
        flow_i = Frank_Wolfe_Solver_Decomposition(traffic_scenario,cost_function,od_subset, flow)
        comm.Allreduce(flow_i, flow_k, op=MPI.SUM)

        error = np.linalg.norm(flow_k-flow,1)
        flow = flow_k

    return flow, error



    # This function implements a decomposition layer by dividing the problem into N (indicated by number of subproblems)
    # and then calls Solver_function on each individual subproblem,
def Decomposition_Solver(traffic_model, cost_function, number_of_subproblems, epsilon=1e-2):
    comm = MPI.COMM_WORLD
    error = -1

    # Initialize demand assignment
    # Constructing the x_0, the initial demand assignment, where all the demand for an OD is assigned to one path
    # We first create a list of paths from the traffic_scenario
    path_list = dict()
    od = traffic_model.beats_api.get_od_info()

    for path in traffic_model.beats_api.get_subnetworks():
        if path.isPath():
            path_list[path.getId()] = path.get_link_ids()

    # Initializing the demand assignment
    commodity_list = list(traffic_model.beats_api.get_commodity_ids())
    num_steps = traffic_model.get_num_steps()
    dt = traffic_model.get_dt()
    assignment = Demand_Assignment_class(path_list, commodity_list,
                                         num_steps, dt)

    #Indices to be used in the subproblems
    # Calling the independent subproblems
    rank = comm.Get_rank()
    size = comm.Get_size()
    n = len(od)

    local_n_c = math.ceil(float(n) / size)  # local step but ceiled
    local_n = n / size
    remainder = n % size

    if (rank < remainder):
        local_a = rank * local_n_c
        local_b = local_a + local_n_c
        local_n = local_n_c
    else:
        local_a = int((remainder) * local_n_c + (rank - remainder) * local_n)
        local_b = int(local_a + local_n-1)

    #print "local_a: ", local_a, " local b: ", local_b

    # Populating the Demand Assignment, based on the paths associated with ODs
    # We also populate a dictionary of (path_id, comm_id) keys associated with ODs
    start_od = 0   # Start of an od demand if demand assignment was to be saved as a vector[demand(path_1, comm_1, t0), demand(path_2,
    # comm_1, t1), ...]
    end_od = 0      # End index of od demand if demand assignment was to be save as a vector[demand(path_1, comm_1, t0), demand(path_2,
    # comm_1, t1), ...]
    od_id = 0
    vector_indices = np.zeros(2)
    for o in traffic_model.beats_api.get_od_info():
        count = 0
        start_od = copy(end_od)
        comm_id = o.get_commodity_id()
        for path in o.get_subnetworks():
            if count == 0:
                demand = [item * 3600 for item in o.get_total_demand_vps().getValues()]
                demand = np.asarray(demand)
                assignment.set_all_demands_on_path_comm(path.getId(), comm_id, demand)
            else:
                demand = np.zeros((num_steps))
                assignment.set_all_demands_on_path_comm(path.getId(), comm_id, demand)
            count += 1
            end_od += num_steps
        if od_id == local_a:
            vector_indices[0] = int(start_od)
        if od_id == local_b:
            vector_indices[1] = int(end_od-1)
        od_id += 1

    #print "rank ", rank, " initial assignment:"
    #assignment.print_all()

    # The set of ods to use for the particular subproblem
    if local_a == local_b:
        od_subset = list()
        od_subset.append(od[local_a])
    else:
        od_subset = od[local_a:local_b]
    
    x_vector = assignment.vector_assignment()
    k_vector = np.zeros(len(x_vector), dtype="float64")
    i = 0

    while error == -1 or error > epsilon:

        # Calling Frank-Wolfe on a subset of ODs
        assignment_i, assignment_vector_i = Path_Based_Frank_Wolfe_Solver_Dec(traffic_model, cost_function, assignment, od_subset, path_list)

        # Combine the results from all the processes
        # We first set to zero all elements not corresponding to the ODs assigned to a particular process
        if vector_indices[0] > 0 or vector_indices[1] < end_od -1:
            if vector_indices[0] == 1:
                assignment_vector_i[0] = 0
            elif vector_indices[0] != 0:
                end_i = int(vector_indices[0]-1)
                for i in range(end_i+1):
                    assignment_vector_i[i] = 0

            if vector_indices[1] == end_od-2:
                assignment_vector_i[end_od-1] = 0
            elif vector_indices[1] != end_od-1:
                start_i = int(vector_indices[1] +1)
                for i in range[start_i: end_od]:
                    assignment_vector_i[i] = 0
                #assignment_vector_i[vector_indices[1]:end_od-1] = 0

        #print "Individual assignment "
        assignment_i.set_demand_with_vector(assignment_vector_i)
        #assignment_i.print_all()

        # Then we do an allreduce to combine the results
        comm.Allreduce(assignment_vector_i, k_vector, op=MPI.SUM)
        
        error = np.linalg.norm(x_vector - k_vector, 1)
        if rank == 0:
            i += 1
            print "Iteration ", i, " error: ", error
        x_vector = deepcopy(k_vector)
        assignment.set_demand_with_vector(x_vector)

        # Printing the assignment received by all the processors
        #print "combined assignment: "
        #print x_vector
        #assignment.print_all()

    return assignment, error


