# This class represent F in the variational inequality problem formulation
# It allow to implement models that do not provide link states, such as microscopic or simulation-based models
# It takes in a Demand_Assignment_class object, which specifies the demand per path, and returns travel cost per path as
# Path_Costs_Class object.
# Each Model_Manager subclass has to implement the evaluate function.

from abc import ABCMeta, abstractmethod

class Abstract_Model_Manager_class():
    __metaclass__ = ABCMeta

    def __init__(self, traffic_model, cost_function):
        self.traffic_model = traffic_model
        self.cost_function = cost_function

    # Takes in demand per path, returns costs per path
    @abstractmethod
    def evaluate(self,demand_assignments, initial_state, dt, T):
        pass