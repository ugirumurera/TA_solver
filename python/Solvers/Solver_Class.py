#This class combines all solvers, either variational inequality, or optimization solver
#It combines an instance of a traffic model with a solver depending whether it is an optimization problem
#or a variational inequality problem

from Frank_Wolfe_Solver_Static import Frank_Wolfe_Solver

class Solver_class():
    def __init__(self, traffic_model, Cost_Function):
        self.traffic_scenario = traffic_model
        self.Cost_Function = Cost_Function

    #This is the function that actually solves a problem
    def Solver_function(self):
        #if problem can be solved as an optimization problem:
        #call an optimization algorithm like Frank-Wolfe
        return Frank_Wolfe_Solver(self.traffic_scenario, self.Cost_Function)
        #Call a algorithm to solve the variational inequality problem - to be developed