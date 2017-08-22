
from Model_Manager.BeATS_Model_Manager import BeATS_Model_Manager_class
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class

# ==========================================================================================
# This code is used on any Windows systems to self start the Entry_Point_BeATS java code
# This code launches a java server that allow to use Beasts java object
import os
import subprocess
import time
import sys
import inspect

this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

jar_file_name = os.path.join(this_folder,'py4jbeats-1.0-SNAPSHOT-jar-with-dependencies.jar')
port_number = '25335'
print("Staring up the java gateway to access the Beats object")
try:
    process = subprocess.Popen(['java', '-jar', jar_file_name, port_number],
                               stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    time.sleep(0.5)
except subprocess.CalledProcessError:
    print("caught exception")
    sys.exit()


# End of Windows specific code
# ======================================================================================

# Contains local path to input configfile, for the three_links.xml network
configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'seven_links.xml')
dt = 2
num_steps = 10

model_manager = BeATS_Model_Manager_class(configfile, port_number, dt)

# If scenario.beast_api is none, it means the configfile provided was not valid for the particular traffic model type
print model_manager.is_valid()

demand_assignment = Demand_Assignment_class(dict(), list(model_manager.beats_api.get_commodity_ids()), num_steps, dt)
demand_assignment.add_all_demands_on_path_comm(path_id,route,comm_id,demands)

model_manager.evaluate(demand_assignment, dt, num_steps*dt)

# kill jvm
process.terminate()