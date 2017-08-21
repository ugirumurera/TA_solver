# This is the model manager for link-based models

from Abstract_Model_Manager import Abstract_Model_Manager_class
from Data_Types.Path_Costs_Class import Path_Costs_class

class Link_Model_Manager_class(Abstract_Model_Manager_class):
    # Constructor receives a Traffic model and cost functions instances
    def __init__(self, traffic_model, cost_function):
        Abstract_Model_Manager_class.__init__(self, traffic_model, cost_function)

    # This overides the evaluate function in the abstract class. Returns a Path_Cost object of costs on paths
    def evaluate(self, demand_assignments, dt, T, initial_state = None):
        # Run_Model returns a State_Trajectory object, which contains state of each link
        link_states = self.traffic_model.Run_Model(demand_assignments, initial_state, dt, T)

        # evaluate_Cost_Function returns a link_Costs object, which contains the costs per links
        link_costs = self.cost_function.evaluate_Cost_Function(link_states)

        # Getting the paths' costs
        path_costs = Path_Costs_class(demand_assignments.get_num_time_step(), dt)
        path_costs.get_path_costs(link_costs, demand_assignments)

        return path_costs