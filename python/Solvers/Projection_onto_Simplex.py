from __future__ import division
import numpy as np
from copy import copy

# This algorithm implements a simple algorithm to project a vector onto a simplex

def Projection_onto_Simplex(vector_to_project, a):

    # a determines the simplex: all vectors (u1, u2, ..., un) in simplex meet the property sum(u1, u2,..., un) = a
    # Step 1: set vector v and find constant rou
    N = len(vector_to_project)
    v = np.asarray(copy(vector_to_project))
    rou = (sum(vector_to_project)-a)/N

    #Step 2
    rel_tol = 1e-09
    current_len_v = N
    new_v = v[np.where(v > (rou+rel_tol))]
    count = 0   # Keeps track of the number of iterations done in

    while len(new_v) != current_len_v and not(np.array_equal(new_v,vector_to_project)):
        current_len_v = len(new_v)
        rou = (sum(new_v)-a)/current_len_v
        new_v = v[np.where(v > (rou+rel_tol))]
        count += 1

    #If new_v = vector_to_project, then the projection is not able to converge, hence requiring a change of tau
    # in the original algorithm. We then return None, and do not project this vector.
    if np.array_equal(new_v,vector_to_project):
        return None

    # Step 3
    tau = rou
    K = len(new_v)

    projection_of_v = np.maximum(np.subtract(v,tau*np.ones(len(v))),np.zeros(len(v)))

    return projection_of_v

def Projection_onto_Simplex_old(vector_to_project, a):
    v = np.asarray(copy(vector_to_project))
    u_vector = np.sort(v)[::-1]
    K = 1

    for i in range(len(u_vector)):
        if i == 0:
            temp_value = (u_vector[0]-a)/(i+1)
        else:
            temp_value = (sum(u_vector[0:i])-a)/(i+1)

        if temp_value < u_vector[i]:
            K = i+1

    if K == 1:
        tau = u_vector[0]-a/K
    else:
        tau = (sum(u_vector[0:(K-1)]) - a) / K

    projection_of_v = np.maximum(np.subtract(v, tau * np.ones(len(v))), np.zeros(len(v)))

    return projection_of_v