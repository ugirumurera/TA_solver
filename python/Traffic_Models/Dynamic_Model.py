#This is basically a place holder for a dynamic model to be developed later
from Traffic_Model import Abstract_Traffic_Model

class Dynamic_Model_Class(Abstract_Traffic_Model):
    #Configfile is needed to initialize the model's scenario via beats_api
    def __init__(self, configfile):
        Abstract_Traffic_Model.__init__(self, configfile)