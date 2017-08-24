# Subclass of the Cost_Function class
# The cost is calculated based on the BPR function: a0 + a1*f + a2*f^2 + a3*f^3 + a4*f^4
# In this way, this cost function always expects static traffic models

from __future__ import division
from Abstract_Cost_Function import Abstract_Cost_Function
from Data_Types.Link_Costs_Class import Link_Costs_class
from copy import copy
import numpy as np

class BPR_Function_class(Abstract_Cost_Function):
    def __init__(self, BPR_Coefficients):
        self.__Coefficients = BPR_Coefficients

    # Get the matrix of coefficients
    def get_coefficients(self):
        return self.__Coefficients

    # Set BPR coefficients
    def set_coefficient(self, coefficients):
        self.__Coefficients = coefficients

    # Overrides the evaluate_Cost_Function in the base class
    # Expects Traffic states to only have flow values. This is the cost function specific to Frank_Wolfe
    def evaluate_Cost_Function_FW(self, flows):
        flows = np.array(flows)
        x = np.power(flows.reshape((flows.shape[0], 1)), np.array([0, 1, 2, 3, 4]))
        link_costs = np.einsum('ij,ij->i', x, np.array(self.__Coefficients.values()))
        return link_costs

    def evaluate_Cost_Function_v1(self, link_states):

        # Getting the flows from link_states object as list
        flows = list()
        for key, state in sorted(link_states.get_all_states().items()):
            flows.append(state[0].get_flow())

        flows = np.array(flows)
        x = np.power(flows.reshape((flows.shape[0], 1)), np.array([0, 1, 2, 3, 4]))
        l_costs = np.einsum('ij,ij->i', x, np.array(self.__Coefficients.values()))

        link_costs = Link_Costs_class(link_states.get_links_list(), link_states.get_comm_list(),
                                   link_states.get_num_time_step())

        i = 0
        for key in link_states.get_all_states().keys():
            link_costs.set_all_costs_on_link_comm(key[0], key[1],[l_costs[i]])
            i += 1

        return link_costs

    def evaluate_Cost_Function(self, link_states):
        num_steps = link_states.get_num_time_step()
        comm_list = link_states.get_comm_list()

        if num_steps != 1:
            raise "num_steps!=1"

        if len(comm_list) != 1:
            raise "This works only for single commodity"

        link_list = link_states.get_links_list()
        link_costs = Link_Costs_class(link_list, comm_list, num_steps)
        comm_id = comm_list[0]

        coeff = self.get_coefficients()

        for link_id in link_list:
            x = link_states.get_all_states_on_link_comm(link_id, comm_id)
            flow = x[0].get_flow()
            c = coeff.get(link_id)
            link_cost = c[0] + flow*(c[1] + flow*(c[2] + flow*(c[3] + c[4]*flow)))
            link_costs.set_all_costs_on_link_comm(link_id, comm_id,[link_cost])

        return link_costs

    # Overrides the evaluate_Gradient in the base class
    def evaluate_Gradient(self, flows):
        flows = np.array(flows)
        new_coefficients = np.array(self.__Coefficients.values())* [0, 1., 2., 3., 4.]
        x = np.power(flows.reshape((flows.shape[0], 1)), np.array([0, 1, 2, 3]))
        return np.einsum('ij,ij->i', x, new_coefficients[:,1:4])

    # Overrides the is_positive_definite in the base class
    def is_positive_definite(self):
        return True

    # Evaluates the potential of the cost function: a0*f + 1/2*a1*f^2 + 1/3*a2*f^3 + 1/4*a3*f^4 + 1/5*a4*f^5
    def evaluate_BPR_Potential(self, link_states):
        num_steps = link_states.get_num_time_step()
        comm_list = link_states.get_comm_list()

        if num_steps != 1:
            raise "num_steps!=1"

        if len(comm_list) != 1:
            raise "This works only for single commodity"

        link_list = link_states.get_links_list()
        comm_id = comm_list[0]

        coeff = self.get_coefficients()
        cost_list = np.zeros(len(link_list))
        i = 0
        for link_id in link_list:
            x = link_states.get_all_states_on_link_comm(link_id, comm_id)
            flow = x[0].get_flow()
            c = coeff.get(link_id)
            cost = c[0]*flow+ 1/2*c[1]*(flow**2) + 1/3*c[2]*(flow**3) + 1/4*c[3]*flow**4 +1/5*c[4]*flow**5
            cost_list[i] = copy(cost)
            i += 1
        return np.sum(cost_list)

    def evaluate_BPR_Potential_FW(self, flows):
        flows = np.array(flows)
        # this routine is useful for doing a line search
        # computes the potential at flow assignment f
        new_coefficients = np.array(self.__Coefficients.values()) * [1, 1 / 2., 1 / 3., 1 / 4., 1 / 5.]
        x = np.power(flows.reshape((flows.shape[0], 1)), np.array([1, 2, 3, 4, 5]))
        return np.sum(np.einsum('ij,ij->i', x, new_coefficients))
