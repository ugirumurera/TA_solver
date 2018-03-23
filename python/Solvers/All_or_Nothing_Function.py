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
    if timer is not None: timer[0] = timer[0] + elapsed1
    print ("Timer is now  %s seconds" % timer[0])

    # Below we initialize the all_or_nothing assignment
    y_assignment = Demand_Assignment_class(path_list, commodity_list,
                                         num_steps, sampling_dt)

    y_assignment.set_all_demands(assignment.get_all_demands())

    # For each OD, we are going to move its demand to the shortest path at current iteration
    count = 0
    #start_time1 = timeit.default_timer()
    for o in od:
        count += 1
        min_cost = 0
        comm_id = o.get_commodity_id()

        demand_api = [item * 3600 for item in o.get_total_demand_vps().getValues()]
        demand_api = np.asarray(demand_api)
        demand_size = len(demand_api)

        for i in range(num_steps):
            min_path_id = -1
            paths_demand = dict()
            for path in o.get_subnetworks():
                if min_path_id == -1:
                    min_path_id = path.getId()
                    min_cost = path_costs.get_cost_at_path_comm_time(min_path_id,comm_id,i)
                elif min_cost > path_costs.get_cost_at_path_comm_time(path.getId(),comm_id,i):
                    min_path_id = path.getId()
                    min_cost = path_costs.get_cost_at_path_comm_time(min_path_id,comm_id,i)

                paths_demand[path.getId()]= 0

            # Putting all the demand on the minimum cost path
            # First set to zero all demands on all path for commodity comm_id and time_step i
            y_assignment.set_all_demands_on_comm_time_step(comm_id, i, paths_demand)
            index = int(i / (num_steps / demand_size))
            demand = o.get_total_demand_vps().get_value(index)*3600
            y_assignment.set_demand_at_path_comm_time(min_path_id, comm_id, i, demand)

    #print "All_or_nothing for ", count, " ods"

    #elapsed1 = timeit.default_timer() - start_time1
    #print ("Changing Demand assignment took  %s seconds" % elapsed1)

    #y_assignment.print_all()
    return y_assignment,path_costs

def all_or_nothing_beats(graph, od):
    '''
    We are given an igraph object 'g' with od in the format {from: ([to], [rate])}
    do all_or_nothing assignment
    '''
    L = np.zeros(len(graph.es), dtype="float64")

    for o in od:

        out = graph.get_shortest_paths(o.get_origin_node_id(), to=o.get_destination_node_id(), weights="weight", output="epath")

        for i, inds in enumerate(out):
            L[inds] = L[inds] + (o.get_total_demand_vps().get_value(0))*3600

    return L