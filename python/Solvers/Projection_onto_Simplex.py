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
    current_len_v = N
    new_v = v[np.where(np.asarray(v) > rou)]

    while len(new_v) != current_len_v:
        current_len_v = len(new_v)
        rou = (sum(new_v)-a)/current_len_v
        new_v = v[np.where(v > rou)]

    # Step 3
    tau = rou
    K = len(new_v)

    projection_of_v = np.maximum(np.subtract(v,tau*np.ones(len(v))),np.zeros(len(v)))

    return projection_of_v

