# This is the model manager for link-based models

from Abstract_Model_Manager import Abstract_Model_Manager_class
from Data_Types.Path_Costs_Class import Path_Costs_class
from Traffic_Models.Static_Model import Static_Model_Class
from Traffic_Models.MN_Model import MN_Model_Class
from Cost_Functions.BPR_Function import BPR_Function_class
import numpy as np
import timeit

class Link_Model_Manager_class(Abstract_Model_Manager_class):
    # Constructor receives a Traffic model and cost functions instances
    def __init__(self, configfile, gateway, traffic_model_name, sim_dt, cost_function_name, cost_function_parameters):
        Abstract_Model_Manager_class.__init__(self, configfile, sim_dt, gateway)

        # create the traffic model
        if traffic_model_name == "static":
            self.traffic_model = Static_Model_Class(self.beats_api)

        elif traffic_model_name == "mn":
            self.traffic_model = MN_Model_Class(self.beats_api, gateway)
        else:
            print("Bad traffic_model_name")
            return

        # create the cost function
        if cost_function_name == "bpr":
            self.cost_function = BPR_Function_class(cost_function_parameters)
        else:
            print("Bad cost_function_name")
            return

    # This overides the evaluate function in the abstract class. Returns a Path_Cost object of costs on paths
    def evaluate(self, demand_assignments, T = None, initial_state = None):
        vect = True #indicates whether we use vector based functions or not
        #start_time1 = timeit.default_timer()
        # Run_Model returns a State_Trajectory object, which contains state of each link
        link_states = self.traffic_model.Run_Model(demand_assignments, initial_state, T, Vectorize = vect)
        #elapsed1 = timeit.default_timer() - start_time1
        #print ("Link_States Generation:  %s seconds" % elapsed1)

        #start_time1 = timeit.default_timer()
        # evaluate_Cost_Function returns a link_Costs object, which contains the costs per links
        link_costs = self.cost_function.evaluate_Cost_Function(link_states, Vectorize = vect)
        #elapsed1 = timeit.default_timer() - start_time1
        #print ("Link_Costs generation:  %s seconds" % elapsed1)

        #start_time1 = timeit.default_timer()
        # Getting the paths' costs
        path_costs = Path_Costs_class(demand_assignments.get_num_time_step(), demand_assignments.get_dt())
        path_costs.get_path_costs(link_costs, demand_assignments, Vectorize= vect)
        #elapsed1 = timeit.default_timer() - start_time1
        #print ("Path_costs generation:  %s seconds" % elapsed1)

        #path_costs.print_all()

        return path_costs

