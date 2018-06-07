# This is a dictionary of od_data objects saved with (origin, destination) keys

from OD_Pair_Class import OD_Pair
from copy import deepcopy
import collections

class OD_Matrix():
    # The constructor receives a list of link ids (link_list), a list of commodities (commodity_list), the number
    # of time steps, and dt, the duration of one time_step
    def __init__(self, num_time_steps,dt):
        self.__num_time_steps = num_time_steps
        self.__dt = dt
        self.__ods = {}

    def get_num_time_step(self):
        return self.__num_time_steps

    def get_dt(self):
        return self.__dt

    # Return all the states
    def get_all_ods(self):
        return self.__ods

    # Returns the state of a particular link, commodity, and time_step
    def get_od(self, origin, destination):
        return self.__ods[(origin, destination)]

    def add_od(self, od_pair):
        if isinstance(od_pair, OD_Pair):
            self.__ods[od_pair.get_origin(), od_pair.get_destination()] = od_pair


    def set_ods_with_beats_ods(self, ods):
        count = 0
        for od in ods:
            #print count
            origin = od.get_origin_node_id()
            dest = od.get_destination_node_id()
            temp_od = OD_Pair()
            temp_od.set_od_with_Beats(od,self.__num_time_steps,self.__dt)
            if temp_od == None:
                print "Missing or Incorrect od info; Could not initialize od dictionary"
                return None
            self.__ods[(origin,dest)] = temp_od
            count += 1

    #Creates an od with just one time step of demand as specified by timestep
    def set_ods_with_beats_ods_timestep(self, ods, timestep):
        #count = 0
        for od in ods:
            #print count
            origin = od.get_origin_node_id()
            dest = od.get_destination_node_id()
            temp_od = OD_Pair()
            temp_od.set_od_with_Beats_timestep(od, self.__num_time_steps, self.__dt, timestep)
            if temp_od == None:
                print "Missing or Incorrect od info; Could not initialize od dictionary"
                return None
            self.__ods[(origin,dest)] = temp_od
            #count += 1

    # Sets all states with an state_trajectory dictionary
    def set_all_ods(self, ods):
        if (any(len(key) != 2 for key in ods.keys()) or
            not isinstance(o, OD_Pair) for o in ods.values()):
            print("Error: shape of input ods does not match format of ODS_Class object")
            return None
        self._ods = deepcopy(ods)

    def print_all(self):
        for key, value in sorted(self.__ods.items()):
                self.__ods[key].print_od_data()
                print"\n"

