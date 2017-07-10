#Subclass of the Cost_Function class
#The cost is calculated based on the BPR function: a0 + a1*f + a2*f^2 + a3*f^3 + a4*f^4
# In this way, this cost function always expects static traffic models

from Abstract_Cost_Function import Abstract_Cost_Function
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

    # Overides the evaluate_Cost_Function in the base class
    # Expects Traffic states to only have flow values
    def evaluate_Cost_Function(self, flows):
        flows = np.array(flows)
        x = np.power(flows.reshape((flows.shape[0], 1)), np.array([0, 1, 2, 3, 4]))
        link_costs = np.einsum('ij,ij->i', x, np.array(self.__Coefficients.values()))
        return link_costs

    # Overides the evaluate_Gradient in the base class
    def evaluate_Gradient(self, flows):
        flows = np.array(flows)
        new_coefficients = np.array(self.__Coefficients.values())* [0, 1., 2., 3., 4.]
        x = np.power(flows.reshape((flows.shape[0], 1)), np.array([0, 1, 2, 3]))
        return np.einsum('ij,ij->i', x, new_coefficients[:,1:4])

    # Overides the is_positive_definite in the base class
    def is_positive_definite(self):
        return True

    # Evaluates the potential of the cost function: a0*f + 1/2*a1*f^2 + 1/3*a2*f^3 + 1/4*a3*f^4 + 1/5*a4*f^5
    def evaluate_BPR_Potential(self, flows):
        flows = np.array(flows)
        # this routine is useful for doing a line search
        # computes the potential at flow assignment f
        new_coefficients= np.array(self.__Coefficients.values())*[1, 1/2.,1/3.,1/4.,1/5.]
        x = np.power(flows.reshape((flows.shape[0], 1)), np.array([1,2,3,4,5]))
        return np.sum(np.einsum('ij,ij->i', x, new_coefficients))


