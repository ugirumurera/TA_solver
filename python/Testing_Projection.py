from Solvers.Projection_onto_Simplex import Projection_onto_Simplex

vector = [30,60,80,90,10]

a = 1.4

y = Projection_onto_Simplex(vector,a)
sum_y = sum(y)

print y, " ", sum_y

