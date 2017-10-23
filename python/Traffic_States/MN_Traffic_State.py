#Static Traffic State, Assuming the demand is fixed

from Abstract_Traffic_State import Abstract_Traffic_State_class
from copy import copy

class MN_Traffic_State_class(Abstract_Traffic_State_class):
    #In the static case, we only need the flow per link
    def __init__(self):
        Abstract_Traffic_State_class.__init__(self)
        self.flow = 0
        self.capacity = 0
        self.jam_density = 0
        self.volume = 0

    def get_jam_density(self):
        return self.jam_density

    def set_jam_density(self, jam_density):
        self.jam_density = copy(jam_density)

    def get_capacity(self):
        return self.capacity

    def set_capacity(self, capacity):
        self.capacity = copy(capacity)

    def set_volume(self, volume):
        self.volume = volume

    #Returns the value of flow
    def get_state_value(self):
        return self.flow

    # Returns the flow state
    def get_flow(self):
        return self.flow

    # Sets the flow value
    def set_flow(self, flow):
        self.flow = flow

    # Increments the flow value
    def add_flow(self, flow):
        self.flow = self.flow + flow

    def set_state_parameters(self, volume, jam_density, capacity):
        self.volume = volume
        self.jam_density = jam_density
        self.capacity = capacity
        self.flow = (self.volume * self.capacity) / self.jam_density

    # Print the flow value
    def print_state(self):
        print "flow ", self.flow

    #Check if the flow is negative
    def is_negative(self):
        if self.flow < 0:
            return True
        return False
