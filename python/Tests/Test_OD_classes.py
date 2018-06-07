# This script test the OD_Matrix and OD_Pair class
import os
import sys
import inspect
this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
data_types_path = os.path.join(this_folder, os.path.pardir, 'Data_Types')
sys.path.insert(0, data_types_path)


import unittest
from OD_Matrix_Class import OD_Matrix
from OD_Pair_Class import OD_Pair

class TestOD_Matrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        T = 600
        dt = 100
        num_steps = T / dt

        cls.od_matrix = OD_Matrix(num_steps, dt)

        #Adding two ods to the OD_Matrix
        node1 = 1
        node2 = 2
        comm_id = 1
        demand = [10,10,10,10,10,10]

        od1 = OD_Pair(node1, node2, num_steps, comm_id, demand)
        od2 = OD_Pair(node2, node1, num_steps, comm_id, demand*2)

        #Adding the ods to the OD_Matrix
        cls.od_matrix.add_od(od1)
        cls.od_matrix.add_od(od2)


    def test_add_od(self):
        self.assertTrue(sorted(TestOD_Matrix.od_matrix.get_od(origin=1, destination=2).get_demand()),
                        sorted([10,10,10,10,10,10]))
        self.assertTrue(sorted(TestOD_Matrix.od_matrix.get_od(origin=1, destination=2).get_demand()),
                        sorted(2*[10,10,10,10,10,10]))


