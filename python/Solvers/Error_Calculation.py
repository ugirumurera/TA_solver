import numpy as np

# This function receives the solution assignment and the corresponding path_costs and returns the distance to Nash
# calculated as of the summation of the excess travel cost for flows on paths compared to the travel cost on the
# shortest paths for an origin-destination pair
def distance_to_Nash(sol_assignment, path_costs, od, sampling_dt = None):
    num_steps = sol_assignment.get_num_time_step()
    dist_to_Nash = 0

    # For each OD, we are going to move its demand to the shortest path at current iteration
    for o in od:
        min_cost = 0
        comm_id = o.get_commodity_id()

        for i in range(num_steps):
            num_paths = len(o.get_subnetworks())
            min_path_id = -1
            cost_on_paths = np.zeros(num_paths)
            demand_on_paths = np.zeros(num_paths)
            j = 0   # index in cost_on_paths and demand_on_paths arrays

            for path in o.get_subnetworks():
                if min_path_id == -1:
                    min_path_id = path.getId()
                    min_cost = path_costs.get_cost_at_path_comm_time(min_path_id, comm_id, i)
                elif min_cost > path_costs.get_cost_at_path_comm_time(path.getId(), comm_id, i):
                    min_path_id = path.getId()
                    min_cost = path_costs.get_cost_at_path_comm_time(min_path_id, comm_id, i)

                # Collecting the costs and demands on paths for od o
                cost_on_paths[j] = path_costs.get_cost_at_path_comm_time(path.getId(), comm_id, i)
                demand_on_paths[j] = sol_assignment.get_demand_at_path_comm_time(path.getId(), comm_id, i)
                j += 1

            # Adding the excess travel cost to the distance from Nash
            min_costs = np.ones(len(cost_on_paths))*min_cost

            dist_to_Nash += sum(np.abs(((cost_on_paths-min_costs)/3600)*demand_on_paths))
    total_trips = sol_assignment.get_total_trips()
    error_percentage = dist_to_Nash/total_trips*100

    return error_percentage


# This is a dot product-based error calculation
def error_dot_product(x_vector, y_vector, current_cost_vector):
    error = np.abs(np.dot(current_cost_vector, y_vector - x_vector) /
                   np.dot(y_vector, current_cost_vector))

    return error

def distance_to_Nash_Over_time_demand(sol_assignment, path_costs, sampling_dt, OD_Matrix):
    num_steps = sol_assignment.get_num_time_step()

    od = OD_Matrix.get_all_ods().values()
    dist_to_Nash = np.zeros(num_steps)

    # For each OD, we are going to move its demand to the shortest path at current iteration
    for o in od:
        min_cost = 0
        comm_id = o.get_comm_id()
        od_path_list = o.get_path_list()

        for i in range(num_steps):
            num_paths = len(od_path_list.keys())
            min_path_id = -1
            cost_on_paths = np.zeros(num_paths)
            demand_on_paths = np.zeros(num_paths)
            j = 0   # index in cost_on_paths and demand_on_paths arrays

            for path_id in od_path_list.keys():
                if min_path_id == -1:
                    min_path_id = path_id
                    min_cost = path_costs.get_cost_at_path_comm_time(min_path_id, comm_id, i)
                elif min_cost > path_costs.get_cost_at_path_comm_time(path_id, comm_id, i):
                    min_path_id = path_id
                    min_cost = path_costs.get_cost_at_path_comm_time(min_path_id, comm_id, i)

                # Collecting the costs and demands on paths for od o
                cost_on_paths[j] = path_costs.get_cost_at_path_comm_time(path_id, comm_id, i)
                demand_on_paths[j] = sol_assignment.get_demand_at_path_comm_time(path_id, comm_id, i)
                j += 1

            # Adding the excess travel cost to the distance from Nash
            min_costs = np.ones(len(cost_on_paths))*min_cost

            indices = np.where((cost_on_paths-min_costs) > 1)[0]

            if len(indices) > 0:
                result = sum((demand_on_paths[indices]))
                if result > 0:
                    a = 1
                dist_to_Nash[i] += sum((demand_on_paths[indices]))
    #total_trips = sol_assignment.get_total_trips_over_time()
    #error_percentage = dist_to_Nash/total_trips*100
    error_percentage = dist_to_Nash

    return error_percentage

def distance_to_Nash_Over_time_cost(sol_assignment, path_costs, sampling_dt, OD_Matrix):
    num_steps = sol_assignment.get_num_time_step()

    od = OD_Matrix.get_all_ods().values()
    dist_to_Nash = np.zeros(num_steps)

    # For each OD, we are going to move its demand to the shortest path at current iteration
    for o in od:
        min_cost = 0
        comm_id = o.get_comm_id()
        od_path_list = o.get_path_list()

        for i in range(num_steps):
            num_paths = len(od_path_list.keys())
            min_path_id = -1
            cost_on_paths = np.zeros(num_paths)
            demand_on_paths = np.zeros(num_paths)
            j = 0   # index in cost_on_paths and demand_on_paths arrays

            for path_id in od_path_list.keys():
                if min_path_id == -1:
                    min_path_id = path_id
                    min_cost = path_costs.get_cost_at_path_comm_time(min_path_id, comm_id, i)
                elif min_cost > path_costs.get_cost_at_path_comm_time(path_id, comm_id, i):
                    min_path_id = path_id
                    min_cost = path_costs.get_cost_at_path_comm_time(min_path_id, comm_id, i)

                # Collecting the costs and demands on paths for od o
                cost_on_paths[j] = path_costs.get_cost_at_path_comm_time(path_id, comm_id, i)
                demand_on_paths[j] = sol_assignment.get_demand_at_path_comm_time(path_id, comm_id, i)
                j += 1

            # Adding the excess travel cost to the distance from Nash
            min_costs = np.ones(len(cost_on_paths))*min_cost

            results = np.abs((cost_on_paths-min_costs))
            dist_to_Nash[i] += sum((results))

    error_percentage = dist_to_Nash

    return error_percentage

#def distance_to_Nash_link_states(sol_state_trajectory, optimal_state_trajectory):
