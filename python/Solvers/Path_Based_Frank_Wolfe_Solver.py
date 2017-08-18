# This is a path_based implementation of Frank-Wolfe
# OD stands for origin destination pair

from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Data_Types.Path_Costs_Class import Path_Costs_class
import numpy as np
import timeit

def Path_Based_Frank_Wolfe_Solver(traffic_model, cost_function, past=10, max_iter=1000, eps=1e-8, \
    q=50, display=1, stop=1e-2):
    # In this case, x_k is a demand assignment object that maps demand to paths
    # Constructing the x_0, the initial demand assignment, where all the demand for an OD is assigned to one path
    # We first create a list of paths from the traffic_scenario
    path_list = dict()
    od = traffic_model.beats_api.get_od_info()

    # Initializing the demand assignment
    commodity_list = list(traffic_model.beats_api.get_commodity_ids())
    num_steps = traffic_model.get_num_steps()
    dt = traffic_model.get_dt()
    assignment = Demand_Assignment_class(path_list,commodity_list,
                                         num_steps, dt)

    start_time1 = timeit.default_timer()
    # Populating the Demand Assignment, based on the paths associated with ODs
    for o in traffic_model.beats_api.get_od_info():
        count = 0
        comm_id = o.get_commodity_id()
        for path in o.get_subnetworks():
            path_list[path.getId()] = path.get_link_ids()
            if count == 0:
                demand = [item*3600 for item in o.get_total_demand_vps().getValues()]
                demand = np.asarray(demand)
                assignment.set_all_demands_on_path_comm(path.getId(),comm_id, demand)
            else:
                demand = np.zeros((num_steps))
                assignment.set_all_demands_on_path_comm(path.getId(), comm_id, demand)
            count += 1
    elapsed1 = timeit.default_timer() - start_time1
    print ("Demand Initialization took  %s seconds" % elapsed1)

    past_assignment = np.zeros((len(path_list.keys()), past), dtype="float64")

    for i in range(max_iter):
        # All_or_nothing assignment
        start_time1 = timeit.default_timer()
        y_assignment, current_path_costs = all_or_nothing(traffic_model, assignment, cost_function, od)
        elapsed1 = timeit.default_timer() - start_time1
        print ("All_or_nothing took  %s seconds" % elapsed1)
        # Calculating the error
        current_cost_vector = current_path_costs.vector_path_costs()
        x_assignment_vector = assignment.vector_assignment()
        y_assignment_vector = y_assignment.vector_assignment()

        error = np.abs(np.dot(current_cost_vector, y_assignment_vector - x_assignment_vector))
        print "iteration: ", i, ", error: ", error
        if error < stop:
            print "Stop with error: ", error
            return assignment

        past_assignment[:,i%past] = y_assignment_vector
        d_assignment = y_assignment_vector-x_assignment_vector

        if i > q:
            # step 3 of Fukushima
            v = np.sum(past_assignment,axis=1) / min(past,i+1) - x_assignment_vector
            norm_v = np.linalg.norm(v,1)
            if norm_v < eps:
                if display >= 1: print 'stop with norm_v: {}'.format(norm_v)
                return assignment
            norm_w = np.linalg.norm(d_assignment,1)
            if norm_w < eps:
                if display >= 1: print 'stop with norm_w: {}'.format(norm_w)
                return assignment
            # step 4 of Fukushima
            gamma_1 = current_cost_vector.dot(v) / norm_v
            gamma_2 = current_cost_vector.dot(d_assignment) / norm_w
            if gamma_2 > -eps:
                if display >= 1: print 'stop with gamma_2: {}'.format(gamma_2)
                return assignment
            d = v if gamma_1 < gamma_2 else d_assignment

        else:
            d = d_assignment

        # step 5 of Fukushima
        start_time1 = timeit.default_timer()
        s = line_search(traffic_model, cost_function, assignment, x_assignment_vector,d)
        elapsed1 = timeit.default_timer() - start_time1
        print ("Line_Search took  %s seconds" % elapsed1)

        if s < eps:
            if display >= 1: print 'stop with step_size: {}'.format(s)
            return assignment
        x_assignment_vector = x_assignment_vector + s*d
        assignment.set_demand_with_vector(x_assignment_vector)

    return assignment

def Path_Based_Frank_Wolfe_Solver_Dec(traffic_model, cost_function, assignment, od_subset,path_list,
                                      past=10, max_iter=1000, eps=1e-8, q=50, display=0, stop=1e-2):
    # In this case, x_k is a demand assignment object that maps demand to paths
    # We receive an initial demand assignment object x_0
    od = od_subset
    past_assignment = np.zeros((len(path_list.keys()), past), dtype="float64")

    for i in range(max_iter):
        # All_or_nothing assignment
        y_assignment, current_path_costs = all_or_nothing(traffic_model, assignment, cost_function, od)
        # Calculating the error
        current_cost_vector = current_path_costs.vector_path_costs()
        x_assignment_vector = assignment.vector_assignment()
        y_assignment_vector = y_assignment.vector_assignment()

        error = np.abs(np.dot(current_cost_vector, y_assignment_vector - x_assignment_vector))
        if display >= 1:print "iteration: ", i, ", error: ", error
        if error < stop:
            if display >= 1: print "Stop with error: ", error
            return assignment, x_assignment_vector

        past_assignment[:,i%past] = y_assignment_vector
        d_assignment = y_assignment_vector-x_assignment_vector

        if i > q:
            # step 3 of Fukushima
            v = np.sum(past_assignment,axis=1) / min(past,i+1) - x_assignment_vector
            norm_v = np.linalg.norm(v,1)
            if norm_v < eps:
                if display >= 1: print 'stop with norm_v: {}'.format(norm_v)
                return assignment, x_assignment_vector
            norm_w = np.linalg.norm(d_assignment,1)
            if norm_w < eps:
                if display >= 1: print 'stop with norm_w: {}'.format(norm_w)
                return assignment, x_assignment_vector
            # step 4 of Fukushima
            gamma_1 = current_cost_vector.dot(v) / norm_v
            gamma_2 = current_cost_vector.dot(d_assignment) / norm_w
            if gamma_2 > -eps:
                if display >= 1: print 'stop with gamma_2: {}'.format(gamma_2)
                return assignment, x_assignment_vector
            d = v if gamma_1 < gamma_2 else d_assignment

        else:
            d = d_assignment

        # step 5 of Fukushima
        s = line_search(traffic_model, cost_function, assignment, x_assignment_vector,d)
        if s < eps:
            if display >= 1: print 'stop with step_size: {}'.format(s)
            return assignment, x_assignment_vector
        x_assignment_vector = x_assignment_vector + s*d
        assignment.set_demand_with_vector(x_assignment_vector)

    return assignment, x_assignment_vector

# This function determines the all_or_nothing demand assignment by putting all OD demand on the shortest path per OD
def all_or_nothing(traffic_model, assignment, cost_function, od):
    #assignment.print_all()
    link_states = traffic_model.Run_Model(assignment)
    #link_states.print_all()
    link_costs = cost_function.evaluate_Cost_Function(link_states)
    #link_costs.print_all()
    path_costs = Path_Costs_class(traffic_model.get_num_steps(), traffic_model.get_dt())
    path_costs.get_path_costs(link_costs, assignment)
    #path_costs.print_all()


    # Initializing the demand assignment
    commodity_list = assignment.get_commodity_list()
    num_steps = assignment.get_num_time_step()
    dt = assignment.get_dt()
    path_list = assignment.get_path_list()
    # Below we initialize the all_or_nothing assignment
    y_assignment = Demand_Assignment_class(path_list, commodity_list,
                                         num_steps, dt)
    y_assignment.set_all_demands(assignment.get_all_demands())


    # For each OD, we are going to move its demand to the shortest path at current iteration
    for o in od:
        min_path_id = -1
        min_cost = 0
        comm_id = o.get_commodity_id()
        for i in range(y_assignment.get_num_time_step()):
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
            demand = o.get_total_demand_vps().get_value(i)*3600
            y_assignment.set_demand_at_path_comm_time(min_path_id, comm_id, i, demand)

    #y_assignment.print_all()
    return y_assignment,path_costs

def line_search(traffic_model, cost_function, assignment, x_assignment_vector, d_vector, res=10):
    # on a grid of 2^res points bw 0 and 1, find global minimum
    # of continuous convex function
    d = 1./(2**res-1)
    l, r = 0, 2**res-1

    #First check on edges
    if potential_func(traffic_model, cost_function, assignment, x_assignment_vector, d_vector, l * d) <= \
            potential_func(traffic_model, cost_function, assignment, x_assignment_vector, d_vector,
                           l * d + d): return l * d
    if potential_func(traffic_model, cost_function, assignment, x_assignment_vector, d_vector, r * d - d) >= \
            potential_func(traffic_model, cost_function, assignment, x_assignment_vector, d_vector, r * d): return r * d

    while r-l > 1:
        # otherwise potential_func(l) > potential_func(l+d) and potential_func(r-d) < potential_func(r)
        m1, m2 = (l+r)/2, 1+(l+r)/2
        potential_1 = potential_func(traffic_model, cost_function, assignment, x_assignment_vector, d_vector,m1*d)
        potential_2 = potential_func(traffic_model, cost_function, assignment, x_assignment_vector, d_vector,m2*d)
        if potential_1 < potential_2: r = m1
        if potential_1 > potential_2: l = m2
        if potential_1 == potential_2: return m1*d
    return l*d

def potential_func(traffic_model, cost_function, assignment, x_assignment_vector, d, alfa):
    mod_assignment_vector = x_assignment_vector + alfa*d
    # Initializing the demand assignment
    commodity_list = assignment.get_commodity_list()
    num_steps = assignment.get_num_time_step()
    dt = assignment.get_dt()
    path_list = assignment.get_path_list()
    # Below we initialize the all_or_nothing assignment
    mod_assignment = Demand_Assignment_class(path_list, commodity_list,
                                         num_steps, dt)
    keys = assignment.get_all_demands().keys()
    mod_assignment.set_keys(keys)
    mod_assignment.set_demand_with_vector(mod_assignment_vector)

    link_states = traffic_model.Run_Model(mod_assignment)
    #link_states.print_all()
    potential_cost = cost_function.evaluate_BPR_Potential(link_states)

    return potential_cost

