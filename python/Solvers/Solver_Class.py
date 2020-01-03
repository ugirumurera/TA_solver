#This class combines all solvers, either variational inequality, or optimization solver
#It combines an instance of a traffic model with a solver depending whether it is an optimization problem
#or a variational inequality problem

from __future__ import division
# from Frank_Wolfe_Solver_Static import Frank_Wolfe_Solver
from Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver
from Method_Successive_Averages_Solver import Method_of_Successive_Averages_Solver
from Modified_Projection_Method_Solver import Modified_Projection_Method_Solver
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from All_or_Nothing_Function import all_or_nothing
from Extra_Projection_Method_Solver import Extra_Projection_Method_Solver
from Path_Based_Frank_Wolfe_Solver import all_or_nothing
import timeit
import numpy as np
import math
import csv
from copy import copy

class Solver_class():
    def __init__(self, model_manager, solver_algorithm = None):
        self.model_manager = model_manager
        self.solver_algorithm = solver_algorithm

    #This is the function that actually solves a problem
    #The Dec parameter indicates whether we are going to use decomposition or not
    def Solver_function(self, T, sampling_dt, OD_Matrix = None, Decomposition = False):
        #Solvers expect a list of ods, so first extract the list of od objects from the OD_Matrix
        if OD_Matrix is None:
            num_steps = int(T/sampling_dt)
            OD_Matrix = self.model_manager.get_OD_Matrix(num_steps, sampling_dt)
        ods = OD_Matrix.get_all_ods().values()


        start_time1 = timeit.default_timer()

        # Call solver with decompostion, or just call the solver
        if Decomposition:
            #assignment, assignment_vect = self.decomposed_solver(T, sampling_dt, self.solver_algorithm,ods, sim_time)

            # If we want to use the parallel strategy
            # assignment, assignment_vect, sim_time, comm_time = self.parallel_solver(T, sampling_dt, self.solver_algorithm, ods)
            assignment, assignment_vect, sim_time, comm_time = self.decomposed_solver(T, sampling_dt, self.solver_algorithm, ods)

        else:
            assignment, assignment_vect, sim_time, comm_time = self.solver_algorithm(self.model_manager, T, sampling_dt, ods)

        if Decomposition:
            from mpi4py import MPI

            comm = MPI.COMM_WORLD
            rank = comm.Get_rank()
        else:
            rank = 0

        elapsed1 = timeit.default_timer() - start_time1
        if rank ==0:
            print ("\nSolver took  %s seconds" % elapsed1)
            print ("comm time: ", comm_time)
            print ("sim time: ", sim_time)
        
        return assignment, elapsed1

    def decomposed_solver(self, T, sampling_dt, solver_function, ods = None, max_iter=50, stop=1e-2):
        from mpi4py import MPI

        sim_time = 0
        comm_time = 0


        # MPI Directives
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()

        # We first start by initializing an initial solution/ demand assignment
        if ods == None:
            num_steps = T/sampling_dt
            od_temp = list(self.model_manager.get_OD_Matrix(num_steps, sampling_dt).get_all_ods().values())
        else: od_temp = ods

        od = np.asarray(sorted(od_temp, key=lambda h: (h.get_origin(), h.get_destination())))

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
            local_b = math.ceil(min(local_a + local_n_c, n))
            local_n = local_n_c
        else:
            local_a = math.ceil((remainder) * local_n_c + (rank - remainder) * local_n)
            local_b = math.ceil(min(local_a + local_n, n))

        # The set of ods to use for the particular subproblem
        print "rank :", rank, " solving for od's ", local_a, " through ", local_b - 1
        od_subset = od[int(local_a):int(local_b)]

        num_steps = int(T / sampling_dt)
        path_list = dict()
        commodity_list = list(self.model_manager.otm_api.scenario().get_commodity_ids())
        init_assignment = Demand_Assignment_class(path_list, commodity_list,
                                             num_steps, sampling_dt)

        # We start with an initial Demand assignment with demands all equal to zeros
        count = 0
        path_index = 0
        for i in range(len(od)):
            comm_id = od[i].get_comm_id()
            od_path_list = od[i].get_path_list()
            path_list.update(od_path_list)

            for key in od_path_list.keys():
                if count >= local_a and count < local_b:
                    demand = np.zeros(num_steps)
                else:
                    demand = np.ones(num_steps)

                init_assignment.set_all_demands_on_path_comm(key, comm_id, demand)
                path_index += 1

            #print "rank: ", rank, " ", od[count].get_origin_node_id(), od[count].get_destination_node_id()
            count += 1

        # vector for previous iteration solution
        #start_time1 = timeit.default_timer()
        prev_vector = np.asarray(init_assignment.vector_assignment())
        #print prev_vector
        # indices in solution vector corresponding to other ods other than the current subset
        out_od_indices = np.nonzero(prev_vector)
        #print out_od_indices
        prev_vector = np.zeros(len(prev_vector))
        init_assignment.set_demand_with_vector(prev_vector)

        #elapsed1 = timeit.default_timer() - start_time1
        #print "Initializing indices too ", elapsed1

        # Initial solution with all_or_nothing assignment
        init_assignment, path_costs, temp_sim_time = all_or_nothing(self.model_manager, init_assignment, od, None, sampling_dt * num_steps)
        x_k_vector = np.zeros(len(prev_vector))
        sim_time = sim_time + temp_sim_time

        prev_vector = np.asarray(init_assignment.vector_assignment())

        #print "Prev_vector ", prev_vector

        for i in range(max_iter):
            display = 0
            if rank == 0: display = 1

            #start_time1 = timeit.default_timer()

            x_i_assignment, x_i_vector, temp_sim_time, temp_comm_time = solver_function(self.model_manager, T, sampling_dt, od_subset, None,
                                                         assignment = init_assignment, display = display)

            sim_time = sim_time + temp_sim_time
            comm_time = comm_time + temp_comm_time

            #elapsed1 = timeit.default_timer() - start_time1
            #print "Decomposition Iteration took ", elapsed1

            # if rank==0: print "rank ", rank, " prev sol vec: ", x_i_vector

            # First zero out all elements in results not corresponding to current odsubset
            x_i_vector[out_od_indices] = 0

            #writer.writerow(np.asarray(out_od_indices))
            #writer.writerow(prev_vector)

            start_time1 = timeit.default_timer()

            # Combine the x_i_vectors with all_reduce directive into x_k_vector
            comm.Allreduce(x_i_vector, x_k_vector, op=MPI.SUM)

            elapsed1 = timeit.default_timer() - start_time1

            comm_time = comm_time + elapsed1
            #print "Communication took ", elapsed1

            # if rank==0: print "rank ", rank, " comb sol vec: ", x_k_vector

            #writer.writerow(x_k_vector)
            # print x_k_vector[od_indices]

            # Calculate error and if error is below predifined level stop

            # All_or_Nothing Assignment for the whole od
            # z_k_assignment, z_k_path_costs = all_or_nothing(self.model_manager, assignment, od, None, T)
            # z_k_vector = np.asarray(z_k_assignment.vector_assignment())
            # z_k_cost_vector = np.asarray(z_k_path_costs.vector_path_costs())

            prev_error = -1
            count = 0
            rep = 5

            error = round(np.linalg.norm(x_k_vector - prev_vector, 1),4)
            # error = np.abs(np.dot(z_k_cost_vector,  z_k_vector- x_k_vector) /
            # np.dot(z_k_vector, z_k_cost_vector))

            # keeping track of the error values seen
            if (prev_error == -1):
                prev_error = error
            elif (prev_error == error):
                count += 1
                if rank == 0: print "count is now ", count
            else:
                prev_error = error
                count = 1

            if error < stop or count >= rep:
                if rank == 0:
                    if count >=rep: print "error did not change ", count, " iterations"
                    print "Decomposition stop with error: ", error
                #csv_file.close()
                init_assignment.set_demand_with_vector(x_k_vector)
                return init_assignment, x_k_vector, sim_time, comm_time

            # Change assignment with current x_k_vector
            # start_time1 = timeit.default_timer()

            init_assignment.set_demand_with_vector(x_k_vector)

            # elapsed1 = timeit.default_timer() - start_time1
            #print "Setting Demand took ", elapsed1

            if rank == 0: print "Decomposition Iteration ", i, " error: ", error
            prev_vector = copy(x_k_vector)

        #csv_file.close()
        return init_assignment, x_k_vector, sim_time, comm_time


    # This function implements the parallel strategy where only the dependent steps among subproblems are shared
    # For the Path_Based_Frank_Wolfe and Method of Successive Averages it only exchanges information after all_or_nothing
    # For Extra_Projection_Method, it is after each projection since each projection is done per od
    def parallel_solver(self, T, sampling_dt, solver_function, ods = None):
        from mpi4py import MPI

        # MPI Directives
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()

        sim_time = 0
        comm_time = 0

        #rank = 0
        #size = 2

        # We first start by initializing an initial solution/ demand assignment
        if ods == None:
            num_steps = T/sampling_dt
            od_temp = list(self.model_manager.get_OD_Matrix(num_steps, sampling_dt).get_all_ods().values())
        else: od_temp = ods

        od = np.asarray(sorted(od_temp, key=lambda h: (h.get_origin(), h.get_destination())))

        n = len(od)

        if n < size and rank >= size:
            print "Number of ods is smaller than number of process. This process will not run solver"
            return None, None

        local_n_c = math.ceil(float(n) / size)  # local step but ceiled
        local_n = n / size
        remainder = n % size

        if (rank < remainder):
            local_a = math.ceil(rank * local_n_c)
            local_b = math.ceil(min(local_a + local_n_c, n))
            local_n = local_n_c
        else:
            local_a = math.ceil((remainder) * local_n_c + (rank - remainder) * local_n)
            local_b = math.ceil(min(local_a + local_n, n))

        # The set of ods to use for the particular subproblem
        print "Solving for od's ", local_a, " through ", local_b - 1
        od_subset = od[int(local_a):int(local_b)]

        #Want to save the solutions obtained per iteration on each processor
        #outputfile = 'Dec_output' + str(rank) + '.csv'
        #csv_file = open(outputfile, 'wb')
        #writer = csv.writer(csv_file)

        num_steps = int(T / sampling_dt)
        path_list = dict()
        commodity_list = list(self.model_manager.otm_api.scenario().get_commodity_ids())
        init_assignment = Demand_Assignment_class(path_list, commodity_list,
                                             num_steps, sampling_dt)
        # We start with an initial Demand assignment with demands all equal to zeros
        count = 0
        path_index = 0
        for i in range(len(od)):
            comm_id = od[i].get_comm_id()
            od_path_list = od[i].get_path_list()
            path_list.update(od_path_list)

            for key in od_path_list.keys():
                if count >= local_a and count < local_b:
                    demand = np.zeros(num_steps)
                else:
                    demand = np.ones(num_steps)

                init_assignment.set_all_demands_on_path_comm(key, comm_id, demand)
                path_index += 1

            #print "rank: ", rank, " ", od[count].get_origin_node_id(), od[count].get_destination_node_id()
            count += 1

        # vector used to calculated the indices not touched by the current subproblem and used to reinitialize
        # the initial demand assignment
        #start_time1 = timeit.default_timer()
        init_vector = np.asarray(init_assignment.vector_assignment())
        #print prev_vector
        # indices in solution vector corresponding to other ods other than the current subset
        if size == 1: out_od_indices  = None
        else: out_od_indices = np.asarray(np.nonzero(init_vector)[0])
        init_vector = np.zeros(len(init_vector))
        init_assignment.set_demand_with_vector(init_vector)

        display = 0
        if rank == 0: display = 1

        timer = None
        if rank == 0: timer = [0]       #Variable used to time the path costs evaluation just for processor rank 0
        # x_assignment, x_vector = solver_function(self.model_manager, T, sampling_dt, od_subset, out_od_indices,
        #                                          init_assignment, display = display, timer = timer)

        x_assignment, x_vector, sim_time, comm_time  = solver_function(self.model_manager, T, sampling_dt, od_subset, out_od_indices,
                                                 init_assignment, display=display)

        # if rank == 0 and timer is not None: print "Total Path Evaluation took: ", timer[0]

        return x_assignment, x_vector, sim_time, comm_time

        # This function receives the solution assignment and the corresponding path_costs and returns the distance to Nash
    # calculated as of the summation of the excess travel cost for flows on paths compared to the travel cost on the
    # shortest paths for an origin-destination pair
    def distance_to_Nash(self, sol_assignment, path_costs, sampling_dt, OD_Matrix = None):
        num_steps = sol_assignment.get_num_time_step()
        if OD_Matrix == None:
            OD_Matrix = self.model_manager.get_OD_Matrix(num_steps, sampling_dt)

        od = OD_Matrix.get_all_ods().values()
        dist_to_Nash = 0

        # For each OD, we are going to move its demand to the shortest path at current iteration
        for o in od:
            min_cost = 0
            comm_id = o.get_comm_id()
            od_path_list = o.get_path_list()

            for i in range(num_steps):
                num_paths = len(od_path_list.keys())
                min_path_id = -1
                cost_on_paths = np.zeros(num_paths)
                demand_on_paths = np.zeros(num_paths)
                j = 0   # index in cost_on_paths and demand_on_paths arrays

                for path_id in od_path_list.keys():
                    if min_path_id == -1:
                        min_path_id = path_id
                        min_cost = path_costs.get_cost_at_path_comm_time(min_path_id, comm_id, i)
                    elif min_cost > path_costs.get_cost_at_path_comm_time(path_id, comm_id, i):
                        min_path_id = path_id
                        min_cost = path_costs.get_cost_at_path_comm_time(min_path_id, comm_id, i)

                    # Collecting the costs and demands on paths for od o
                    cost_on_paths[j] = path_costs.get_cost_at_path_comm_time(path_id, comm_id, i)
                    demand_on_paths[j] = sol_assignment.get_demand_at_path_comm_time(path_id, comm_id, i)
                    j += 1

                # Adding the excess travel cost to the distance from Nash
                min_costs = np.ones(len(cost_on_paths))*min_cost

                dist_to_Nash += sum(np.abs(((cost_on_paths-min_costs)/3600)*demand_on_paths))
        total_trips = sol_assignment.get_total_trips()
        error_percentage = dist_to_Nash/total_trips*100
        #error_vehicles = dist_to_Nash/total_trips

        return error_percentage