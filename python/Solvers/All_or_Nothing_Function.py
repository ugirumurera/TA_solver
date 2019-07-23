import numpy as np
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
import timeit

# This function determines the all_or_nothing demand assignment by putting all OD demand on the shortest path per OD
# Timer is used to calculate the time spent in path costs evaluation
def all_or_nothing(model_manager, assignment, od, initial_state = None, T = None, timer = None):
    sampling_dt = assignment.get_dt()

    # Initializing the demand assignment
    commodity_list = assignment.get_commodity_list()
    num_steps = assignment.get_num_time_step()
    path_list = assignment.get_path_list()

    start_time1 = timeit.default_timer()

    path_costs = model_manager.evaluate(assignment,T, initial_state)
    #path_costs.print_all_in_seconds()
    elapsed1 = timeit.default_timer() - start_time1
    # if timer is not None:
    #     timer[0] = timer[0] + elapsed1
    #     print ("Timer is now  %s seconds" % timer[0])

    print "path_eval took: ", elapsed1

    # Below we initialize the all_or_nothing assignment
    y_assignment = Demand_Assignment_class(path_list, commodity_list,
                                         num_steps, sampling_dt)

    y_assignment.set_all_demands(assignment.get_all_demands())

    # For each OD, we are going to move its demand to the shortest path at current iteration
    count = 0
    #start_time1 = timeit.default_timer()

    start_time1 = timeit.default_timer()
    for o in od:
        count += 1
        min_cost = 0
        comm_id = o.get_comm_id()
        od_path_list = o.get_path_list()

        for i in range(num_steps):
            min_path_id = -1
            for path_id in od_path_list.keys():

                #Check if the current entry in not zero, make it zero
                if y_assignment.get_demand_at_path_comm_time(path_id, comm_id, i) > 0:
                    y_assignment.set_demand_at_path_comm_time(path_id, comm_id, i, 0)

                if min_path_id == -1:
                    min_path_id = path_id
                    min_cost = path_costs.get_cost_at_path_comm_time(min_path_id,comm_id,i)
                elif min_cost > path_costs.get_cost_at_path_comm_time(path_id,comm_id,i):
                    min_path_id = path_id
                    min_cost = path_costs.get_cost_at_path_comm_time(min_path_id,comm_id,i)

            # Putting all the demand on the minimum cost path
            demand = o.get_demand()[i]
            y_assignment.set_demand_at_path_comm_time(min_path_id, comm_id, i, demand)

    #print "All_or_nothing for ", count, " ods"

    elapsed1 = timeit.default_timer() - start_time1
    print ("Changing Demand assignment took  %s seconds" % elapsed1)

    #y_assignment.print_all()
    return y_assignment,path_costs

def all_or_nothing_beats(graph, od, time_step=None, decomposition_flag = False):
    '''
    We are given an igraph object 'g' with od in the format {from: ([to], [rate])}
    do all_or_nothing assignment
    '''
    L = np.zeros(len(graph.es), dtype="float64")

    for o in od:

        out = graph.get_shortest_paths(o.get_origin(), to=o.get_destination(), weights="weight", output="epath")

        for i, inds in enumerate(out):
            #L[inds] = L[inds] + (o.get_total_demand_vps().get_value(0))*3600
            if time_step is None:
                L[inds] = L[inds] + o.get_demand()
            else:
                L[inds] = L[inds] + o.get_demand()[time_step]

    if decomposition_flag:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        L_f = np.zeros(len(L))  # final flow that is sent

        start_time1 = timeit.default_timer()
        comm.Allreduce(L, L_f, op=MPI.SUM)
        elapsed1 = timeit.default_timer() - start_time1
        if rank == 0: print ("\nComm Reduce took  %s seconds" % elapsed1)
        L = L_f


    return L