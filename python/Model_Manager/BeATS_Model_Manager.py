# This is the model manager for link-based models
from __future__ import division
from Abstract_Model_Manager import Abstract_Model_Manager_class
from Data_Types.Path_Costs_Class import Path_Costs_class
import numpy as np

class BeATS_Model_Manager_class(Abstract_Model_Manager_class):

    # Constructor receives a Traffic model and cost functions instances
    def __init__(self, configfile, gateway, dt):
        Abstract_Model_Manager_class.__init__(self, configfile, gateway)
        self.dt = dt

    # This overrides the evaluate function in the abstract class. Returns a Path_Cost object of costs on paths
    def evaluate(self, demand_assignment, sim_dt, time_horizon, initial_state=None):
        #print "\n"

        #demand_assignment.print_all()

        comm_id = 1
        start_time = 0.0
        #path_cost_dt = 60.0
        path_cost_dt = float(sim_dt)
        path_cost_n = demand_assignment.get_num_time_step()  # int(time_horizon/path_cost_dt)
        demand_dt = float(sim_dt)
        demand_n = int(time_horizon/demand_dt)

        api = self.beats_api

        # request path travel time output
        for path_id in demand_assignment.get_path_list():
            api.request_path_travel_time(path_id, path_cost_dt)

        # clear demands in beats
        api.clear_all_demands()

        # send demand assignment to beats
        for path_comm, demand_list in demand_assignment.get_all_demands().iteritems():
            path_id = path_comm[0]
            comm_id = path_comm[1]
            java_array = self.gateway.jvm.java.util.ArrayList()
            for d in demand_list:
                java_array.add(float(d))
            api.set_demand_on_path_in_vph(path_id, comm_id, start_time, demand_dt, java_array)

        # run BeATS
        api.run(float(start_time), float(time_horizon))

        # extract the path costs
        path_costs = Path_Costs_class(path_cost_n, demand_dt)
        path_costs.set_path_list(demand_assignment.get_path_list())
        path_costs.set_comm_list(demand_assignment.get_commodity_list())
        count = 0
        cost_dict = {}
        #print "the size of the output is ", (len(api.get_output_data()))
        for path_data in api.get_output_data():
            path_id = path_data.getPathId()
            cost_list = path_data.compute_travel_time_for_start_times(start_time, path_cost_dt, demand_n)
            path_costs.set_costs_path_commodity(path_data.getPathId(), comm_id, cost_list)
            #print "path id ", path_data.getPathId(), " cost ", cost_list
            '''
            if path_id not in cost_dict.keys():
                cost_dict[path_data.getPathId()] = np.zeros(3)
            cost_dict[path_id][0] += cost_list[0]
            cost_dict[path_id][1] += cost_list[1]
            cost_dict[path_id][2] += 1
            '''
            count += 1
        '''
        for key in cost_dict.keys():
            cost_dict[key][0] = cost_dict[key][0]/cost_dict[key][2]
            cost_dict[key][1] = cost_dict[key][1] / cost_dict[key][2]
            print "avg costs: ", cost_dict[key][0:2]
        '''
        
        return path_costs
