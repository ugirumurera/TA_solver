import numpy as np
import igraph
from Solvers.Projection_onto_Simplex import Projection_onto_Simplex,Projection_onto_Simplex_old

array_p = [56.7,42.78,0.1]
a = 1

#x = Projection_onto_Simplex(array_p,a)
y = Projection_onto_Simplex_old(array_p,a)

#print x
print y