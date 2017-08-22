#This is the abstract base class for all Traffic models
#Each subclass has to implement all abstract method of this class

from abc import ABCMeta, abstractmethod
from py4j.java_gateway import JavaGateway,GatewayParameters

class Abstract_Traffic_Model_class:
    __metaclass__ = ABCMeta

    # The Traffic Class initiates connection to Beats object
    def __init__(self, beats_api, dt_sec=None):
        self.beats_api = beats_api
        self.dt_sec = dt_sec

    def get_dt(self):
        return self.dt_sec

    # Validate the scenario loaded from the configuration file.
    # Returns: A boolean. True if the scenario is valid, False otherwise.
    # This is optional to implement
    def Validate_Configfile(self):
        return True

    '''
    Map from path demands to link states

    Arguments:
    A Demand_Assignment object, demand_assignments
        This object stores a dictionary of the form [path_id, commodity_id] : [demand_t1, demand_t2,...]
        This is to be initialized in the solver algorithm by user and shows the demand per path, per commodity and per
        per time step.
    initial_state: An State Trajectory object that specifies the initial state of links in terms of flow, number of vehicles
                  and queue per link (Ignore in the case of static model)
    dt: simulation time step in seconds. (Ignore in the case of a static model)
    T: simulation time horizon in second. (Ignore in the case of a static model)

    Returns: A State_Trajectory object, which stores a dictionary of the form [link_id, commodity_id] : [traffic_state_t1, traffic_state_t2,...]
    Each Traffic_State object can have:
        flows: corresponds to the average flow on link_id(i) of commodity(j) over time interval k (ie from t=k*dt to t=(k+1)*dt).
            Units: vehicles/hour
        vehicles: corresponds to the total number of vehicles on link_id(i) of commodity(j) at time instant k (ie t=k*dt)
            Units: vehicles
        queue: corresponds to the number of vehicles in link_id(i) of commodity(j) that are in a queue at time instant k (ie t=k*dt).
            Units: vehicles

    Assumtpions on the output:
    + link_ids covers all links with non-zero output flow and state.
    + commodity_ids covers all commodities with non-zero demand
    + Assume that time steps are numbered from 0,1,2,...

    '''
    @abstractmethod
    def Run_Model(self, demand_assignments, initial_state, dt, T):
        pass

    # Gradient of the model
    # Returns the variation of the path costs to small perturbations in the path demands,
    # for a given level of path demands.
    # The input and output format is similar to that of Run_Model, except that on the output
    # side, the values should be interpreted as variations.
    # Implementation of this function is optional. It enables gradient-based algorithms, however,
    # if no gradient can be provided, then return None.
    def Model_Gradient(self, demand_assignments, initial_state, dt, T):
        return None

