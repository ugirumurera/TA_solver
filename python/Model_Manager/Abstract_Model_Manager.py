# This class represent F in the variational inequality problem formulation
# It allow to implement models that do not provide link states, such as microscopic or simulation-based models
# It takes in a Demand_Assignment_class object, which specifies the demand per path, and returns travel cost per path as
# Path_Costs_Class object.
# Each Model_Manager subclass has to implement the evaluate function.

from __future__ import division
from abc import ABCMeta, abstractmethod

class Abstract_Model_Manager_class():
    __metaclass__ = ABCMeta

    def __init__(self, configfile, sim_dt, gateway):
        self.gateway = gateway
        self.configfile = configfile
        self.beats_api = gateway.entry_point.get_BeATS_API()
        timestamps = self.beats_api.load(configfile, sim_dt, True)
        time1 = (timestamps[1] - timestamps[0])/1000
        time2 = (timestamps[2] - timestamps[1])/1000
        print "Load JAXB took: ", time1, " sec"
        print "Create Scenario took: ", time2, " sec"

    def is_valid(self):
        return( self.beats_api is not None) and (self.beats_api.has_scenario())

    # Takes in demand per path, returns costs per path
    @abstractmethod
    def evaluate(self,demand_assignments, T, initial_state ):
        pass