#This class combines all solvers, either variational inequality, or optimization solver
#It combines an instance of a traffic model with a solver depending whether it is an optimization problem
#or a variational inequality problem

from __future__ import division
from Frank_Wolfe_Solver_Static import Frank_Wolfe_Solver
from Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver
from Method_Successive_Averages_Solver import Method_of_Successive_Averages_Solver
from Modified_Projection_Method_Solver import Modified_Projection_Method_Solver
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Extra_Projection_Method_Solver import Extra_Projection_Method_Solver
import timeit
import numpy as np
import math

#from mpi4py import MPI

class Solver_class():
    def __init__(self, model_manager, solver_algorithm):
        self.model_manager = model_manager
        self.solver_algorithm = solver_algorithm

    #This is the function that actually solves a problem
    #The Dec parameter indicates whether we are going to use decomposition or not
    def Solver_function(self, T, sampling_dt, solver_name = None, Decomposition = False):
        #The name of algorithm to call is passed as name
        assignment, assignment_vect = None, None

        start_time1 = timeit.default_timer()
        # Call solver with decompostion, or just call the solver
        if Decomposition: self.decomposed_solver(T, sampling_dt, self.solver_algorithm)

        else:
            assignment, assignment_vect = self.solver_algorithm(self.model_manager, T, sampling_dt)

        elapsed1 = timeit.default_timer() - start_time1
        print ("\nSolver took  %s seconds" % elapsed1)
        
        return assignment, assignment_vect


    def decomposed_solver(self, T, sampling_dt, max_iter = 1000, stop=1e-2):
        #MPI Directives
        #comm = MPI.COMM_WORLD
        #rank = comm.Get_rank()
        #size = comm.Get_size()

        rank = 2
        size = 3

        # We first start by initializing an initial solution/ demand assignment
        od = list(self.model_manager.beats_api.get_od_info())

        # Determine which subset of od to be addressed by the current process
        n = len(od)

        if n < size and rank >= size:
            print "Number of ods is smaller than number of process. This process will not run solver"
            return None, None

        local_n_c = math.ceil(float(n) / size)  # local step but ceiled
        local_n = n / size
        remainder = n % size

        if (rank < remainder):
            local_a = math.ceil(rank * local_n_c)
            local_b = math.ceil(min(local_a + local_n_c,n))
            local_n = local_n_c
        else:
            local_a = math.ceil((remainder) * local_n_c + (rank - remainder) * local_n)
            local_b = math.ceil(min(local_a + local_n,n))

        # The set of ods to use for the particular subproblem
        print "Solving for od's ", local_a, " through ", local_b-1
        od_subset = od[int(local_a):int(local_b)]

        num_steps = int(T / sampling_dt)
        path_list = dict()
        commodity_list = list(self.model_manager.beats_api.get_commodity_ids())
        assignment = Demand_Assignment_class(path_list,commodity_list,
                                         num_steps, sampling_dt)

        # We start with an initial Demand assignment with demands all equal to zeros
        count = 0
        for o in od:
            comm_id = o.get_commodity_id()

            demand_api = [item * 3600 for item in o.get_total_demand_vps().getValues()]
            demand_api = np.asarray(demand_api)
            demand_size = len(demand_api)
            demand_dt = o.get_total_demand_vps().getDt()

            # Before assigning the demand, we want to make sure it can be properly distributed given the number of
            # Time step in our problem
            if (sampling_dt > demand_dt or demand_dt % sampling_dt > 0) and (demand_size > 1):
                print "Demand specified in xml cannot not be properly divided among time steps"
                return None, None

            for path in o.get_subnetworks():
                path_list[path.getId()] = path.get_link_ids()
                if count >= local_a and count < local_b:
                    demand = np.zeros(num_steps)
                else: demand = np.ones(num_steps)
                assignment.set_all_demands_on_path_comm(path.getId(), comm_id, demand)
            count += 1

        #vector for previous iteration solution
        prev_vector = np.asarray(assignment.vector_assignment())
        # indices in solution vector corresponding to other ods other than the current subset
        out_od_indices = np.nonzero(prev_vector)
        # indices of current od subset
        od_indices = np.where(prev_vector == 0)[0]
        prev_vector = np.zeros(len(prev_vector))
        #Reseting to zero all demands
        assignment.set_demand_with_vector(prev_vector)
        x_k_vector = np.zeros(len(prev_vector))

        for i in range(max_iter):
            x_i_assignment, x_i_vector = solver_function(self.model_manager, T, sampling_dt,od_subset,assignment)
            #print x_i_vector[od_indices]
            #print x_i_vector[out_od_indices]

            # First zero out all elements in results not corresponding to current odsubset
            x_i_vector[out_od_indices] = 0
            # Combine the x_i_vectors with all_reduce directive into x_k_vector
            #comm.Allreduce(x_i_vector, x_k_vector, op = MPI.SUM)


            # If solution did not change, stop
            error = np.linalg.norm(x_k_vector-prev_vector,1)
            assignment.set_demand_with_vector(x_k_vector)
            
            if error < stop:
                print "Stop with error: ", error
                return assignment, x_k_vector
            
            prev_vector = x_k_vector


    # This function receives the solution assignment and the corresponding path_costs and returns the distance to Nash
    # calculated as of the summation of the excess travel cost for flows on paths compared to the travel cost on the
    # shortest paths for an origin-destination pair
    def distance_to_Nash(self, sol_assignment, path_costs, sampling_dt):
        num_steps = sol_assignment.get_num_time_step()
        od = self.model_manager.beats_api.get_od_info()
        dist_to_Nash = 0

        # For each OD, we are going to move its demand to the shortest path at current iteration
        for o in od:
            min_cost = 0
            comm_id = o.get_commodity_id()

            for i in range(num_steps):
                num_paths = len(o.get_subnetworks())
                min_path_id = -1
                cost_on_paths = np.zeros(num_paths)
                demand_on_paths = np.zeros(num_paths)
                j = 0   # index in cost_on_paths and demand_on_paths arrays

                for path in o.get_subnetworks():
                    if min_path_id == -1:
                        min_path_id = path.getId()
                        min_cost = path_costs.get_cost_at_path_comm_time(min_path_id, comm_id, i)
                    elif min_cost > path_costs.get_cost_at_path_comm_time(path.getId(), comm_id, i):
                        min_path_id = path.getId()
                        min_cost = path_costs.get_cost_at_path_comm_time(min_path_id, comm_id, i)

                    # Collecting the costs and demands on paths for od o
                    cost_on_paths[j] = path_costs.get_cost_at_path_comm_time(path.getId(), comm_id, i)
                    demand_on_paths[j] = sol_assignment.get_demand_at_path_comm_time(path.getId(), comm_id, i)
                    j += 1

                # Adding the excess travel cost to the distance from Nash
                min_costs = np.ones(len(cost_on_paths))*min_cost

                dist_to_Nash += sum(np.abs(((cost_on_paths-min_costs)/3600)*demand_on_paths))
        total_trips = sol_assignment.get_total_trips()
        error_percentage = dist_to_Nash/total_trips*100

        return error_percentage
