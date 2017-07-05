#This class combines all solvers, either variational inequality, or optimization solver
#It combines an instance of a traffic model with a solver depending whether it is an optimization problem
#or a variational inequality problem

from Frank_Wolfe_Algorithm import Frank_Wolfe_Solver

class Solver_class():
    def __init__(self, traffic_model, F_function):
        self.traffic_scenario = traffic_model
        self.F_function = F_function

    #This is the function that actually solves a problem
    def Solver_function(self):
        if self.traffic_scenario.is_positive_definite() and self.F_function.is_positive_definite():
            #call an optimization algorithm like Frank-Wolfe
            return Frank_Wolfe_Solver(self.traffic_scenario, self.F_function)
            #Call a algorithm to solve the variational inequality problem - to be developed