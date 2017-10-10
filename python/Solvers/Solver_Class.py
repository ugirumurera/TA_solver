#This class combines all solvers, either variational inequality, or optimization solver
#It combines an instance of a traffic model with a solver depending whether it is an optimization problem
#or a variational inequality problem

from Frank_Wolfe_Solver_Static import Frank_Wolfe_Solver
from Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver
import timeit
#from Decomposition_Solver import Decomposition_Solver

class Solver_class():
    def __init__(self, model_manager):
        self.model_manager = model_manager

    #This is the function that actually solves a problem
    #The Dec parameter indicates whether we are going to use decomposition or not
    def Solver_function(self, T, sampling_dt, Dec = False, number_of_subproblems = 1):
        #if problem can be solved as an optimization problem:
        assignment_seq = None
        frank_sol = None

        #call an optimization algorithm like Frank-Wolfe
        start_time1 = timeit.default_timer()
        assignment_seq = Path_Based_Frank_Wolfe_Solver(self.model_manager, T, sampling_dt)
        elapsed1 = timeit.default_timer() - start_time1
        print ("Sequential Path-based took  %s seconds" % elapsed1)

        '''
        assignment_dec = None
        if Dec == True:
            start_time1 = timeit.default_timer()
            assignment_dec, error = Decomposition_Solver(self.traffic_scenario, self.Cost_Function, number_of_subproblems)
            print "Decomposition finished with error ", error
            elapsed1 = timeit.default_timer() - start_time1
            print ("Decomposition Path-based took  %s seconds" % elapsed1)


        print "\n"
        start_time1 = timeit.default_timer()
        frank_sol = Frank_Wolfe_Solver(self.model_manager)
        elapsed1 = timeit.default_timer() - start_time1
        print ("FW link-based took  %s seconds" % elapsed1)
        #Call a algorithm to solve the variational inequality problem - to be developed
        '''
        
        return assignment_seq, frank_sol