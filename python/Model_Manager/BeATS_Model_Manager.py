# This is the model manager for link-based models

from Abstract_Model_Manager import Abstract_Model_Manager_class
from Data_Types.Path_Costs_Class import Path_Costs_class


class BeATS_Model_Manager_class(Abstract_Model_Manager_class):

    # Constructor receives a Traffic model and cost functions instances
    def __init__(self, configfile, gateway, dt):
        Abstract_Model_Manager_class.__init__(self, configfile, gateway)
        self.dt = dt

    # This overrides the evaluate function in the abstract class. Returns a Path_Cost object of costs on paths
    def evaluate(self, demand_assignments, dt, T, initial_state = None):

        start_time = 0
        n = int(T/dt)

        # request path travel time output
        for path_id in demand_assignments.get_path_list():
            self.beats_api.request_path_travel_time(path_id, 60)

        # clear demands in beats
        self.beats_api.clear_all_demands()

        # send demand assignment to beats
        for path_comm, demand_list in demand_assignments.get_all_demands().iteritems():
            path_id = path_comm[0]
            comm_id = path_comm[1]
            java_array = self.gateway.jvm.java.util.ArrayList()
            for d in demand_list:
                java_array.add(d)
            self.beats_api.set_demand_on_path_in_vph(path_id, comm_id, start_time, dt, java_array)

        # run BeATS
        self.beats_api.run(start_time, dt, T)

        # extract the path costs
        path_costs = Path_Costs_class(demand_assignments.get_num_time_step(), dt)
        comm_id = 1   # HACK. WHY DO WE NEED COMMODITY ID?
        for path_data in self.beats_api.get_output_data():
            cost_list = path_data.compute_travel_time_for_start_times(start_time, dt, n)
            path_costs.set_costs_path_commodity(path_data.getPathId(), comm_id, cost_list)

        return path_costs
