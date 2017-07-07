#Static Traffic Model, assuming the demand is fixed

from Traffic_Model import Abstract_Traffic_Model
from Data_Types.State_Trajectory import State_Trajectory_class
from Traffic_States.Static_Traffic_State import Static_Traffic_State_class
import abc


class Static_Model_Class(Abstract_Traffic_Model):
    #Configfile is needed to initialize the model's scenario via beats_api
    def __init__(self, configfile):
        self.model_type = 's'     #Indicates that this is a static model
        Abstract_Traffic_Model.__init__(self, configfile)

    def Validate_Configfile(self):
        # If the configfile indicates varying demand, return with an error
        # We first want to check the configfile to make sure it is in correct format
        demand_array = self.beats_api.get_demands()
        valid = True
        i = 0 # index in the demand_arrary matrix
        while i < demand_array.__len__() and valid:
            if demand_array[i].getProfile().num_values() > 1:
                return False
            i = i + 1
        return True

    # Overides the Run_Model function in the abstract class
    # Returns an array of link states where each entry indicates the flow per link, per commodity and per time step
    def Run_Model(self, demand_assignments, initial_state = None, dt = None, T = None):
        num_paths = demand_assignments.get_num_paths()
        num_commodities = demand_assignments.get_commodities()

        # Initialize the State_Trajectory object
        link_states = State_Trajectory_class(self.beats_api.get_num_links(),
                                                 self.beats_api.get_num_commodities(), 1)
        path_id = 0
        while path_id <= num_paths-1:
            comm_id = 0
            while comm_id <= num_commodities-1:
                path_info = self.beats_api.get_subnetwork_with_id(path_id+1)  # this is a SubnetworkInfo object
                for link_id in path_info.getLink_ids():
                    if type(link_states.get_state_link_comm_time(link_id, comm_id, 0))is abc.ABCMeta:
                        state = Static_Traffic_State_class()
                        link_states.set_state_link_comm_time(link_id,comm_id,0, state)

                    demand_value = demand_assignments.get_demand_at_path_comm_time(path_id, comm_id,0)
                    link_states.get_state_link_comm_time(link_id, comm_id, 0).add_flow(demand_value)
                comm_id = comm_id + 1
            path_id = path_id + 1

        return link_states
