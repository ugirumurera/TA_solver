#Static Traffic Model, assuming the demand is fixed

import numpy as np

from Traffic_Model import Abstract_Traffic_Model


class Static_Model_Class(Abstract_Traffic_Model):
    #Configfile is needed to initialize the model's scenario via beats_api
    def __init__(self, configfile):
        self.model_type = 's'     #Indicates that this is a static model
        Abstract_Traffic_Model.__init__(self, configfile)

    def Validate_Configfile(self):
        # If the configfile indicates varying demand, return with an error
        # We first want to check the configfile to make sure it is in correct format
        demand_array = self.beats_api.get_demands()
        valid = True
        i = 0 # index in the demand_arrary matrix
        while i < demand_array.__len__() and valid:
            if demand_array[i].getProfile().num_values() > 1:
                return False
            i = i + 1
        return True

    #Overriding the run model function from the base class
    def Run_Model(self, demands, initial_state = None, dt = None, T = None):
        #creates a list of link_ids
        link_id_list = self.get_list_link_ids()
        #creates a list of all commodities
        commodity_list = self.get_list_commodities()

        #Create array for flows
        link_flow = np.zeros((len(link_id_list), len(commodity_list)))

        for demand in demands:
            # check if the demand in demand is defined on paths
            if not demand.is_path:
                print('code assumes all demands are defined on paths')
                return
            # loop through links on the path
            path_info = self.beats_api.get_subnetwork_with_id(demand.getPath_id())  # this is a SubnetworkInfo object
            for link_id in path_info.getLink_ids():
                link_flow[link_id][demand.getCommodity_id()-1] = link_flow[link_id][demand.getCommodity_id()-1] + (demand.getProfile().get_value(0)*3600)

        return link_id_list, commodity_list, link_flow

    #Returns a incident matrix mapping from flow on links to demand on paths
    def Model_Gradient(self, demands,initial_state = None, dt = None, T = None):
        num_links = self.beats_api.get_num_links()
        num_demands = len(demands)
        gradient_matrix = np.zeros((num_links, num_demands))
        i = 0
        for demand in demands:
            if not demand.is_path:
                print('code assumes all demands are defined on paths')
                return
            # Loop through links on the path
            path_info = self.beats_api.get_subnetwork_with_id(demand.getPath_id())  # this is a SubnetworkInfo object
            for link_id in path_info.getLink_ids():
                gradient_matrix[link_id, i] = 1
            i = i+1
        return gradient_matrix

    def construct_od(self):
        # construct a dictionary of the form
        # origin: ([destination],[demand])
        out = {}
        for od_info in self.beats_api.get_od_info():
            origin = od_info.get_origin_node_id()
            out[origin] = ([], [])
            out[origin][0].append(od_info.get_destination_node_id())
            out[origin][1].append(od_info.get_total_demand_vps().get_value(0)*3600)
        return out

    #Returns a dictionary  of all the demands values with time_period: [demand]
    #For static models, returns a list of demands values since the demand is fixed.
    def get_demand_values(self):
        demand_list = list()
        for demand in self.beats_api.get_demands():
        # check if the demand is demand is defined on a path
            if not demand.is_path:
                print('code assumes all demands are defined on paths')
                return
            demand_list.append(demand.getProfile().get_value(0)*3600)
        return demand_list

    #Since this is static model, it is positive definite
    def is_positive_definite(self):
        return True