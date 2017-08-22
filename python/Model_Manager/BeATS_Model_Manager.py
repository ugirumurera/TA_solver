# This is the model manager for link-based models

from Abstract_Model_Manager import Abstract_Model_Manager_class
from Data_Types.Path_Costs_Class import Path_Costs_class


class BeATS_Model_Manager_class(Abstract_Model_Manager_class):

    # Constructor receives a Traffic model and cost functions instances
    def __init__(self, configfile, port_number, dt):
        Abstract_Model_Manager_class.__init__(self, configfile, port_number)
        self.dt = dt

    # This overrides the evaluate function in the abstract class. Returns a Path_Cost object of costs on paths
    def evaluate(self, demand_assignments, dt, T, initial_state = None):

        start_time = 0
        n = int(T/dt)

        # request path travel time output
        for path_id in demand_assignments.get_path_list():
            self.beats_api.request_path_travel_time(path_id,60)

        # run BeATS
        self.beats_api.run(start_time, dt, T)

        # extract the path costs
        path_costs = Path_Costs_class(demand_assignments.get_num_time_step(), dt)

        comm_id = 1   # HACK. WHY DO WE NEED COMMODITY ID?
        for path_data in self.beats_api.get_output_data():
            path_costs.add_all_costs_on_path_comm(path_data.getPathId(), comm_id, path_data.compute_travel_time_for_start_times(start_time,dt,n))

        return path_costs
