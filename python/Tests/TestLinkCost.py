
import unittest
import os
import inspect
from Java_Connection import Java_Connection
from Model_Manager.Link_Model_Manager import Link_Model_Manager_class


class TestLinkCost(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # make Java connection
        cls.connection = Java_Connection()

        # create a static/bpr model manager
        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links.xml')
        bpr_coefficients = {0L: [1, 0, 0, 0, 1], 1L: [1, 0, 0, 0, 1], 2L: [5, 0, 0, 0, 5], 3L: [2, 0, 0, 0, 2],
                        4L: [2, 0, 0, 0, 2], 5L: [1, 0, 0, 0, 1], 6L: [5, 0, 0, 0, 5]}
        cls.model_manager = Link_Model_Manager_class(configfile, cls.connection, "static", None, "bpr", bpr_coefficients)

    def test(self):

        api = TestLinkCost.model_manager.beats_api
        num_links = api.get_num_links()

        # THIS IS UNFINISHED

        # In order to use the BPR function, we first need to get the flows the state trajectory object as a list

        # flows = list()
        # for state in link_states.get_all_states().values():
        #     flows.append(state[0].get_flow())
        #
        # # Initialize the BPR cost function
        # BPR_cost_function = BPR_Function_class(coefficients)
        # link_costs = Link_Costs_class(link_list, commodity_list, time_period)
        #
        # # Setting the link costs using the results returned by evaluating the BPR function given flows
        # print("\nThe costs per link are as follows (Link_Costs class):")
        # l_costs = BPR_cost_function.evaluate_Cost_Function(flows)
        # l_cost_dict = {}
        # l_cost_dict[(0L, 1L)] = [l_costs[0]]
        # l_cost_dict[(1L, 1L)] = [l_costs[1]]
        # l_cost_dict[(2L, 1L)] = [l_costs[2]]
        #
        # link_costs.set_all_costs(l_cost_dict)
        # link_costs.print_all()
        #
        # # Test for Link_Costs_Class
        # result = link_costs.get_cost_at_link_comm_time(0, 1, 0)
        # result = link_costs.get_all_costs_on_link(2)
        # result = link_costs.get_all_costs_on_link_comm(1, 1)
        # result = link_costs.get_all_costs_on_link_time_step(1, 0)
        # result = link_costs.get_all_costs_for_commodity(1)
        # result = link_costs.get_all_costs_on_comm_time_step(1, 0)
        # result = link_costs.get_all_costs_for_time_step(0)
        #
        # link_costs.set_all_costs(link_costs.get_all_costs())
        # comm_cost = {1L: [20]}
        # link_costs.set_all_costs_on_link(1, comm_cost)
        # print"\n"
        # link_costs.print_all()
        #
        # link_costs.set_all_costs_on_link_comm(1, 1, [-48])
        # print"\n"
        # link_costs.print_all()
        #
        # link_costs.set_all_costs_on_link_time_step(2, 0, {1L: 1085})
        # print"\n"
        # link_costs.print_all()
        #
        # link_costs.set_all_costs_for_commodity(1, comm_cost)
        # print"\n"
        # link_costs.print_all()
        #
        # link_costs.set_all_costs_on_comm_time_step(1, 0, {1L: [4657, 12], 2L: 3649})
        # print"\n"
        # link_costs.print_all()
        #
        # link_costs.set_all_costs_for_time_step(0, {(1L, 1L): 374, (2L, 1L): 4659})
        # print"\n"
        # link_costs.print_all()
