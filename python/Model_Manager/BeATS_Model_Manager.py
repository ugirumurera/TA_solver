# This is the model manager for link-based models

from Abstract_Model_Manager import Abstract_Model_Manager_class
from Data_Types.Path_Costs_Class import Path_Costs_class


class BeATS_Model_Manager_class(Abstract_Model_Manager_class):

    # Constructor receives a Traffic model and cost functions instances
    def __init__(self, configfile, gateway, dt):
        Abstract_Model_Manager_class.__init__(self, configfile, gateway)
        self.dt = dt

    # This overrides the evaluate function in the abstract class. Returns a Path_Cost object of costs on paths
    def evaluate(self, demand_assignment, dt, T, initial_state = None):

        comm_id = 1
        time_horizon = 3600.0
        start_time = 0.0
        path_cost_dt = 60.0
        path_cost_n = demand_assignment.get_num_time_step()  # int(time_horizon/path_cost_dt)
        demand_dt = 1800.0
        demand_n = int(time_horizon/demand_dt)

        api = self.beats_api

        # request path travel time output
        for path_id in demand_assignment.get_path_list():
            api.request_path_travel_time(path_id, path_cost_dt)

        # clear demands in beats
        api.clear_all_demands()

        # send demand assignment to beats
        for path_comm, demand_list in demand_assignment.get_all_demands().iteritems():
            path_id = path_comm[0]
            comm_id = path_comm[1]
            java_array = self.gateway.jvm.java.util.ArrayList()
            for d in demand_list:
                java_array.add(float(d))
            api.set_demand_on_path_in_vph(path_id, comm_id, start_time, demand_dt, java_array)

        # run BeATS
        api.run(start_time, time_horizon)

        # extract the path costs
        path_costs = Path_Costs_class(path_cost_n, path_cost_dt)
        for path_data in api.get_output_data():
            cost_list = path_data.compute_travel_time_for_start_times(start_time, path_cost_dt, demand_n)
            path_costs.set_costs_path_commodity(path_data.getPathId(), comm_id, cost_list)

        return path_costs
