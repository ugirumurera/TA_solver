#Static Traffic Model, assuming the demand is fixed

from Abstract_Traffic_Model import Abstract_Traffic_Model_class
from Data_Types.State_Trajectory_Class import State_Trajectory_class
from Traffic_States.MN_Traffic_State import MN_Traffic_State_class



class MN_Model_Class(Abstract_Traffic_Model_class):
    #Configfile is needed to initialize the model's scenario via beats_api
    def __init__(self, beats_api, gateway):
        self.gateway = gateway
        self.model_type = 'mn'     #Indicates that this is a static model
        Abstract_Traffic_Model_class.__init__(self, beats_api)

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


        start_time = 0.0
        comm_id = 1L
        read_time = demand_assignment.get_dt() * (0.0)  # Hack, heuristic, need a state estimator
        # path_cost_dt = 60.0
        path_cost_dt = float(demand_assignment.get_dt())
        path_cost_n = demand_assignment.get_num_time_step()  # int(time_horizon/path_cost_dt)
        demand_dt = float(demand_assignment.get_dt())
        demand_n = int(time_horizon / demand_dt)

        api = self.beats_api

        # Clear the path requests
        api.clear_output_requests()

        # request link veh output
        for path_id in demand_assignment.get_path_list():
            api.request_link_veh(comm_id, path_id, path_cost_dt)

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


        # cycle through beats outputs

        sampling_dt = demand_assignment.get_dt()
        num_steps = time_horizon/sampling_dt
        link_states = State_Trajectory_class( list(self.beats_api.get_link_ids()),
                                                 list(self.beats_api.get_commodity_ids()), num_steps, sampling_dt)
        for output in api.get_output_data():
            # change later to include dictionary and avoid repeated links
            for link_id in output.get_link_ids():
                print link_id
                profile = output.get_profile_for_linkid(link_id)
                comm = output.get_commodity_id(link_id)
                jam_density = self.beats_api.get_link_with_id(link_id).get_max_vehicles()
                capacity = self.beats_api.get_link_with_id(link_id).get_capacity_vps() * 3600
                for i in range(num_steps):
                    time = i * demand_assignment.get_dt()
                    # Profile1D
                    # change to mn traffic state class
                    state = MN_Traffic_State_class()
                    state.set_parameters(profile.get_value_for_time(time), jam_density, capacity)
                    link_states.set_state_on_link_comm_time(link_id, comm, i, state)
        return link_states

    def get_total_demand(self):
        demands = self.beats_api.get_demands()
        total_demand = 0

        for demand in demands:
            total_demand = total_demand + demand.getProfile().get_value(0)*3600

        return total_demand