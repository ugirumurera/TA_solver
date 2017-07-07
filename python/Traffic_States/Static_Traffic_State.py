#Static Traffic State, Assuming the demand is fixed

from Traffic_State import Abstract_Traffic_State

class Static_Traffic_State_class(Abstract_Traffic_State):
    #In the static case, we only need the flow per link
    def __init__(self):
        Abstract_Traffic_State.__init__(self)
        self.flow = 0

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

    # Print the flow value
    def print_state(self):
        print ( self.flow )
