#Abstract base class for the Cost Functions
#All subclasses have to implement all the abstract methods

from abc import ABCMeta, abstractmethod,abstractproperty

class Abstract_Function_F:
    __metaclass__ = ABCMeta

    #Function to evaluate function F
    @abstractmethod
    def evaluate_Cost_Function(self, flows, densities):
        pass

    #Function to evaluate the gradient of F if it exist
    #@abstractmethod
    def evaluate_Gradient(self, flows, densities):
        pass

    #Function to determine whether F is positive definite
    @abstractmethod
    def is_positive_definite(self):
        pass