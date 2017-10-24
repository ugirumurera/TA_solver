#Static Traffic State, Assuming the demand is fixed

from Abstract_Traffic_State import Abstract_Traffic_State_class
from copy import copy

class MN_Traffic_State_class(Abstract_Traffic_State_class):
    #In the static case, we only need the flow per link
    def __init__(self):
        Abstract_Traffic_State_class.__init__(self)
        self.flow = 0
        self.capacity = 0
        # self.max_vehicles = 0
        # self.volume = 0

    # def get_max_vehicles(self):
    #     return self.max_vehicles
    #
    # def set_max_vehicles(self, max_vehicles):
    #     self.max_vehicles = copy(max_vehicles)

    def get_capacity(self):
        return self.capacity

    # def set_capacity_vph(self, capacity_vph):
    #     self.capacity_vph = copy(capacity_vph)

    # def set_volume(self, volume):
    #     self.volume = volume

    #Returns the value of flow
    def get_state_value(self):
        return self.flow

    # Returns the flow state
    def get_flow(self):
        return self.flow

    # Sets the flow value
    def set_flow(self, flow):
        self.flow = flow

    # # Increments the flow value
    # def add_flow(self, flow):
    #     self.flow = self.flow + flow

    def set_state_parameters(self, volume, max_vehicles, capacity_vph):
        # self.volume = volume
        # self.max_vehicles = max_vehicles
        self.capacity = capacity_vph
        # self.flow = (self.volume * self.capacity) / self.max_vehicles
        self.flow = (volume * capacity_vph) / max_vehicles


    # Print the flow value
    def print_state(self):
        print "flow ", self.flow

    #Check if the flow is negative
    def is_negative(self):
        if self.flow < 0:
            return True
        return False
