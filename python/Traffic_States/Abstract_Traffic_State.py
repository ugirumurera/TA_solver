#This is the abstract base class for all Traffic State Models
#Each subclass has to implement all abstract method of this class

from abc import ABCMeta, abstractmethod

class Abstract_Traffic_State_class:
    __metaclass__ = ABCMeta

    # The user has to specify the variables that are important for their traffic state
    #
    def __init__(self):
        pass

    # Function to print all the link states.
    # All subclasses should implement this function to allow viewing the Traffic states
    @abstractmethod
    def print_state(self):
        pass

    # Function to check if any value in traffic state is negative
    # All subclasses should implement this function
    @abstractmethod
    def is_negative(self):
         pass