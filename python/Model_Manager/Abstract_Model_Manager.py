# This class represent F in the variational inequality problem formulation
# It allow to implement models that do not provide link states, such as microscopic or simulation-based models
# It takes in a Demand_Assignment_class object, which specifies the demand per path, and returns travel cost per path as
# Path_Costs_Class object.
# Each Model_Manager subclass has to implement the evaluate function.

from abc import ABCMeta, abstractmethod

class Abstract_Model_Manager_class():
    __metaclass__ = ABCMeta

    def __init__(self, configfile, gateway):
        self.gateway = gateway
        self.beats_api = gateway.entry_point.get_BeATS_API()
        self.beats_api.load(configfile)

    def is_valid(self):
        return self.beats_api is not None

    # Takes in demand per path, returns costs per path
    @abstractmethod
    def evaluate(self,demand_assignments, initial_state, dt, T):
        pass