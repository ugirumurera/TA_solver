#This is the abstract base class for all Traffic models
#Each subclass has to implement all abstract method of this class

from abc import ABCMeta, abstractmethod
from py4j.java_gateway import JavaGateway,GatewayParameters

class Abstract_Traffic_Model:
    __metaclass__ = ABCMeta

    # The Traffic Class initiates connection to Beats object
    def __init__(self, configfile):
        port_number = 25335
        self.gateway = JavaGateway(gateway_parameters=GatewayParameters(port=port_number))
        self.beats_api = self.gateway.entry_point.get_BeATS_API()
        self.beats_api.load(configfile)

        if not self.Validate_Configfile():
            self.beats_api = None
            return

    # Validate the scenario loaded from the configuration file.
    # Returns: A boolean. True if the scenario is valid, False otherwise.
    @abstractmethod
    def Validate_Configfile(self):
        pass

    # Map from path demands to link states
    #
    # Arguments:
    # demands: A list of DemandInfo objects, as returned by self.beats_api.get_demands()
    # initial_state: An initial state, as returned by self.beats_api.get_initial_state()
    #                Ignore in the case of a static model.
    # dt: simulation time step in seconds. (Ignore in the case of a static model)
    # T: simulation time horizon in second. (Ignore in the case of a static model)
    #
    # Returns: A dictionary with these entries:
    #   link_ids: A list of link ids, ordered as the rows of the flow, vehicles, and queue matrices.
    #   commodity_ids: A list of commodity ids, ordered as the columns of the flows, vehicles, and
    #      queue matrices.
    #   flows: A numpy ndarray of dimension 3.
    #      The (i,j,k)th entry corresponds to the average flow on link_id(i) of commodity(j) over time
    #      interval k (ie from t=k*dt to t=(k+1)*dt).
    #      Units: vehicles/hour
    #      Size: length(link_ids) X length(commodity_ids) X (T/dt)
    #   vehicles: A numpy ndarray of dimension 3.
    #      The (i,j,k)th entry corresponds to the total number of vehicles on link_id(i)
    #      of commodity(j) at time instant k (ie t=k*dt)
    #      Units: vehicles
    #      Size: length(link_ids) X length(commodity_ids) X (1 + T/dt)
    #   queue: A numpy ndarray of dimension 3.
    #      The (i,j,k)th entry corresponds to the number of vehicles in link_id(i) of commodity(j)
    #      that are in a queue at time instant k (ie t=k*dt).
    #      Units: vehicles
    #      Size: length(link_ids) X length(commodity_ids) X (1 + T/dt)
    #
    # Assumptions on the input:
    # + It can be assumed that all of the DemandInfo objects have equal start_time, corresponding to
    #   the time of the initial state. All have equal dt, which is an integer multiple of the simulation dt.
    # + Any origin with no corresponding DemandInfo object is assigned zero demand
    # + Any link/commodity not covered by the initial_state has zero initial condition.
    # + T is an integer multiple of dt.
    #
    # Assumtpions on the output:
    # + link_ids covers all links with non-zero output flow and state.
    # + commodity_ids covers all commodities with non-zero demand
    # + the order of the rows and columns in flows, vehicles, and queue corresponds to the order
    #   of link_ids and commodity_ids respectively.
    @abstractmethod
    def Run_Model(self, demands, initial_state, dt, T):
        pass

    # Gradient of the model
    # Returns the variation of the path costs to small perturbations in the path demands,
    # for a given level of path demands.
    # The input and output format is similar to that of Run_Model, except that on the output
    # side, the values should be interpreted as variations.
    # Implementation of this function is optional. It enables gradient-based algorithms, however,
    # if no gradient can be provided, then return None.
    @abstractmethod
    def Model_Gradient(self, demands, initial_state, dt, T):
        return None

