#Static Traffic Model, assuming the demand is fixed

from Abstract_Traffic_Model import Abstract_Traffic_Model_class
from Data_Types.State_Trajectory import State_Trajectory_class
from Traffic_States.Static_Traffic_State import Static_Traffic_State_class
from Data_Types.Path_Costs_Class import Path_Costs_class
import abc


class MN_Model_Class(Abstract_Traffic_Model_class):
    #Configfile is needed to initialize the model's scenario via beats_api
    def __init__(self, configfile):
        self.model_type = 'mn'     #Indicates that this is a static model
        Abstract_Traffic_Model_class.__init__(self, configfile)

    # def Validate_Configfile(self):
    #     # If the configfile indicates varying demand, return with an error
    #     # We first want to check the configfile to make sure it is in correct format
    #     demand_array = self.beats_api.get_demands()
    #     valid = True
    #     i = 0 # index in the demand_array matrix
    #     while i < demand_array.__len__() and valid:
    #         if demand_array[i].getProfile().num_values() > 1:
    #             return False
    #         i = i + 1
    #     return True

    # Overides the Run_Model function in the abstract class
    # Returns an array of link states where each entry indicates the flow per link, per commodity and per time step
    def Run_Model(self, demand_assignment, initial_state = None,time_horizon = None):
        # num_paths = demand_assignments.get_num_paths()
        # num_commodities = demand_assignments.get_commodities()

        # demand_assignment.print_all()

        start_time = 0.0
        read_time = demand_assignment.get_dt() * (0.0)  # Hack, heuristic, need a state estimator
        # path_cost_dt = 60.0
        path_cost_dt = float(demand_assignment.get_dt())
        path_cost_n = demand_assignment.get_num_time_step()  # int(time_horizon/path_cost_dt)
        demand_dt = float(demand_assignment.get_dt())
        demand_n = int(time_horizon / demand_dt)

        api = self.beats_api

        # Clear the path requests
        api.clear_output_requests()

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
        api.set_random_seed(1)  # Initialize the random seed
        api.run(float(start_time), float(time_horizon))



        # Initialize the State_Trajectory object
        # link_states = State_Trajectory_class(self.beats_api.get_num_links(),


        # # extract the path costs
        # path_costs = Path_Costs_class(path_cost_n, demand_dt)
        # path_costs.set_path_list(demand_assignment.get_path_list())
        # path_costs.set_comm_list(demand_assignment.get_commodity_list())
        #
        # # print "the size of the output is ", (len(api.get_output_data()))
        #
        #
        # for path_data in api.get_output_data():
        #     cost_list = path_data.compute_travel_time_for_start_times(read_time, path_cost_dt, demand_n)
        # path_costs.set_costs_path_commodity(path_data.getPathId(), comm_id, cost_list)
        # # print "path id ", path_data.getPathId(), " cost ", cost_list
        #
        # return path_costs

        # self.beats_api.get_num_commodities(), 1)
        # path_id = 0
        # while path_id <= num_paths-1:
        #     comm_id = 0
        #     while comm_id <= num_commodities-1:
        #         path_info = self.beats_api.get_subnetwork_with_id(path_id+1)  # this is a SubnetworkInfo object
        #         for link_id in path_info.getLink_ids():
        #             if type(link_states.get_state_link_comm_time(link_id, comm_id, 0))is abc.ABCMeta:
        #                 state = Static_Traffic_State_class()
        #                 link_states.set_state_link_comm_time(link_id,comm_id,0, state)
        #
        #             demand_value = demand_assignments.get_demand_at_path_comm_time(path_id, comm_id,0)
        #             link_states.get_state_link_comm_time(link_id, comm_id, 0).add_flow(demand_value)
        #         comm_id = comm_id + 1
        #     path_id = path_id + 1

        return None

    def get_total_demand(self):
        demands = self.beats_api.get_demands()
        total_demand = 0

        for demand in demands:
            total_demand = total_demand + demand.getProfile().get_value(0)*3600

        return total_demand