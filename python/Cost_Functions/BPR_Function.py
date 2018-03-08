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

    def evaluate_Cost_Function(self, link_states, Vectorize = False):
        if Vectorize:
            coeff = np.array(self.__Coefficients.values())
            # Stands for coeff[4]*flow^4, where flow is the link states as matrix
            power_4_coeff = np.matmul(np.array(coeff[:, 4]).reshape(len(coeff[:, 4]), 1),
                                      np.ones((1, link_states.shape[1])))
            # Stands for coeff[4]*flow^3, where flow is the link states as matrix
            power_3_coeff = np.matmul(np.array(coeff[:, 3]).reshape(len(coeff[:, 3]), 1),
                                      np.ones((1, link_states.shape[1])))
            # Stands for coeff[4]*flow^2, where flow is the link states as matrix
            power_2_coeff = np.matmul(np.array(coeff[:, 2]).reshape(len(coeff[:, 2]), 1),
                                      np.ones((1, link_states.shape[1])))
            # Stands for coeff[4]*flow^1, where flow is the link states as matrix
            power_1_coeff = np.matmul(np.array(coeff[:, 1]).reshape(len(coeff[:, 1]), 1),
                                      np.ones((1, link_states.shape[1])))
            #Putting all the above together + the free-flow travel time (coeff[0] in the form of matrix)
            link_costs = np.matmul(np.array(coeff[:, 0]).reshape(len(coeff[:, 0]), 1),
                                   np.ones((1, link_states.shape[1]))) + \
                         power_1_coeff * (link_states ** 1) + power_2_coeff * (link_states ** 2) + power_3_coeff * ( link_states ** 3) + \
                         power_4_coeff * (link_states ** 4)
        else:
            num_steps = link_states.get_num_time_step()
            comm_list = link_states.get_comm_list()

            link_list = link_states.get_links_list()
            link_costs = Link_Costs_class(link_list, comm_list, num_steps)
            comm_id = comm_list[0]

            coeff = self.get_coefficients()

            for link_id in link_list:
                x = link_states.get_all_states_on_link_comm(link_id, comm_id)
                for i in range(num_steps):
                    flow = x[i].get_flow()
                    c = coeff.get(link_id)
                    link_cost = c[0] + flow*(c[1] + flow*(c[2] + flow*(c[3] + c[4]*flow)))
                    link_costs.set_cost_at_link_comm_time(link_id, comm_id,i, link_cost)

            #link_costs.print_all()

        return link_costs

    def mod_evaluate_Cost_Function(self,linkstates):
        coeff = np.array(self.__Coefficients.values())
        power_4_coeff = np.matmul(np.array(coeff[:,4]).reshape(len(coeff[:,4]),1),np.ones((1,linkstates.shape[1])))
        #power_4 =power_4_coeff *(linkstates**4)
        power_3_coeff = np.matmul(np.array(coeff[:, 3]).reshape(len(coeff[:, 3]), 1), np.ones((1, linkstates.shape[1])))
        #power_3 =power_3_coeff*(linkstates**3)
        power_2_coeff = np.matmul(np.array(coeff[:, 2]).reshape(len(coeff[:, 2]), 1), np.ones((1, linkstates.shape[1])))
        #power_2 = power_2_coeff * linkstates ** 2
        power_1_coeff = np.matmul(np.array(coeff[:, 1]).reshape(len(coeff[:, 1]), 1), np.ones((1, linkstates.shape[1])))
        #power_1 = power_1_coeff * linkstates ** 1
        #power_0 = np.matmul(np.array(coeff[:, 0]).reshape(len(coeff[:, 0]), 1), np.ones((1, linkstates.shape[1])))

        link_costs = np.matmul(np.array(coeff[:, 0]).reshape(len(coeff[:, 0]), 1), np.ones((1, linkstates.shape[1]))) + \
                     power_1_coeff * (linkstates ** 1) + power_2_coeff * (linkstates ** 2) + power_3_coeff*(linkstates**3) + \
                     power_4_coeff * (linkstates ** 4)

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

        '''
        if num_steps != 1:
            raise "num_steps!=1"

        if len(comm_list) != 1:
            raise "This works only for single commodity"
        '''

        link_list = link_states.get_links_list()
        comm_id = comm_list[0]
        j = 0
        coeff = self.get_coefficients()
        cost_list = np.zeros(num_steps)
        for i in range(num_steps):
            x = link_states.get_all_states_on_comm_time_step( comm_id, i)
            cost = 0
            for link_id in link_list:
                flow = x[link_id].get_flow()
                c = coeff.get(link_id)
                cost += c[0]*flow+ 1/2*c[1]*(flow**2) + 1/3*c[2]*(flow**3) + 1/4*c[3]*flow**4 +1/5*c[4]*flow**5
            cost_list[j] = copy(cost)
            j += 1
        return cost_list

    def evaluate_BPR_Potential_FW(self, flows):
        flows = np.array(flows)
        # this routine is useful for doing a line search
        # computes the potential at flow assignment f
        new_coefficients = np.array(self.__Coefficients.values()) * [1, 1 / 2., 1 / 3., 1 / 4., 1 / 5.]
        x = np.power(flows.reshape((flows.shape[0], 1)), np.array([1, 2, 3, 4, 5]))
        return np.sum(np.einsum('ij,ij->i', x, new_coefficients))
