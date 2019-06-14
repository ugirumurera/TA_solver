# This class represent F in the variational inequality problem formulation
# It allow to implement models that do not provide link states, such as microscopic or simulation-based models
# It takes in a Demand_Assignment_class object, which specifies the demand per path, and returns travel cost per path as
# Path_Costs_Class object.
# Each Model_Manager subclass has to implement the evaluate function.

from __future__ import division
from abc import ABCMeta, abstractmethod
from python.Data_Types.OD_Matrix_Class import OD_Matrix
import os

class Abstract_Model_Manager_class():
    __metaclass__ = ABCMeta

    def __init__(self, configfile, traffic_model_name, sim_dt, gateway):
        self.gateway = gateway
        self.configfile = configfile
        self.otm_api = gateway.entry_point.get_OTM_API()

        if traffic_model_name == 'static':
            timestamps = self.otm_api.load_for_static_traffic_assignment(configfile)
        else:
            timestamps = self.otm_api.load(configfile, sim_dt, False, traffic_model_name)
        time1 = (timestamps[1] - timestamps[0])/1000
        time2 = (timestamps[2] - timestamps[1])/1000
        print "Load JAXB took: ", time1, " sec"
        print "Create Scenario took: ", time2, " sec"

    def is_valid(self):
        return (self.otm_api is not None) and (self.otm_api.has_scenario())

    def get_OD_Matrix(self, num_steps, sampling_dt):
        #Create the list of od with OD_Class object
        od_beats = self.otm_api.get_od_info()
        ods = OD_Matrix(num_steps,sampling_dt)
        ods.set_ods_with_beats_ods(od_beats)

        return ods

    def get_OD_Matrix_timestep(self, num_steps, sampling_dt, timestep):
        #Create the list of od with OD_Class object
        od_beats = self.otm_api.get_od_info()
        ods = OD_Matrix(num_steps,sampling_dt)
        ods.set_ods_with_beats_ods_timestep(od_beats,timestep)

        return ods

    # Takes in demand per path, returns costs per path
    @abstractmethod
    def evaluate(self,demand_assignments, T, initial_state ):
        pass