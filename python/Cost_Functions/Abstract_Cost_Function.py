#Abstract base class for the Cost Functions
#All subclasses have to implement all the abstract methods

from abc import ABCMeta, abstractmethod,abstractproperty

class Abstract_Cost_Function:
    __metaclass__ = ABCMeta

    #Function to evaluate function F
    # Receives a State_Trajectory object that is an array of link states:
    #   Stores a three dimensional array of Traffic State objects.
    #   The traffic state object stores the traffic state per link_id(i), per commodity(j) and per time step k, where
    #   a traffic state can include flow, number of vehicles (density, and queue
    # Returns a Link_Cost object that is an array of cost per link:
    #   Stores a three dimensional array of costs per link.
    #   Each entry (i,j,k) in the array is the cost for link (i) for commodity (j) at time step (k)
    @abstractmethod
    def evaluate_Cost_Function(self, link_states):
        pass

    #Function to evaluate the gradient of F if it exist
    #Input and output similar to that of evaluate_Cost_Function
    # This is optional
    def evaluate_Gradient(self, link_states):
        pass

    #Function to determine whether F is positive definite
    # This is optional
    def is_positive_definite(self):
        pass