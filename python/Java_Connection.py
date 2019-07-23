from subprocess import call
import subprocess
import os
import subprocess
import signal
import platform
import time
import sys
import inspect
from py4j.java_gateway import JavaGateway, GatewayParameters
import socket


class Java_Connection():

    def __init__(self, decomposition_flag = False):

        self.process = None
        self.pid = None

        #If we are using mpi, then the port number should depend on the processors rank
        if decomposition_flag:
            from mpi4py import MPI
            comm = MPI.COMM_WORLD
            rank = comm.Get_rank()
        else: rank = 0

        #Port Number
        port_num = 25333 + rank

        print "port number is:", port_num

        self.port_number = str(port_num)

        jar_name = 'otm-py4j-1.0-SNAPSHOT-jar-with-dependencies.jar'

        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        jar_file_name = os.path.join(this_folder, jar_name)

        #First check if the file exists indeed:
        if os.path.isfile(jar_file_name):

            if platform.system() == "Windows":
                self.openWindows(jar_file_name, self.port_number)
            elif platform.system() in ["Linux", "Darwin"]:
                self.openLinux(jar_file_name, self.port_number)
            else:
                raise Exception('Unknown platform')

            self.gateway = JavaGateway(gateway_parameters=GatewayParameters(port=int(self.port_number)))

            print(platform.system())

        else:
            print "Jar file missing"

    def openWindows(self, jar_file_name, port_number):
        try:
            self.process = subprocess.Popen(['java', '-jar', jar_file_name, port_number],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.pid = self.process.pid
            time.sleep(1)
        except subprocess.CalledProcessError:
            print("caught exception")
            sys.exit()

    def openLinux(self, jar_file_name, port_number):
        subprocess.call('for pid in $(ps -ef | grep otm-py4j-1.0-SNAPSHOT | awk \'{print $2}\' ); do kill -9 $pid; done', shell= True)

        self.pid = os.fork()

        if self.pid == 0:
            self.pid = os.getpid()
            retcode = call(['java', '-jar',jar_file_name, '-port', port_number])
            print retcode
            time.sleep(1)
            sys.exit()

        # Here we wait for 0.5 sec to allow the java server to start
        time.sleep(1)

    def close(self):
        if platform.system() == "Windows":
            os.kill(self.process.pid, signal.CTRL_C_EVENT)
        elif platform.system() in ["Linux", "Darwin"]:
            os.kill(0, signal.SIGTERM)
        else:
            raise Exception('Unknown platform')

    def is_valid(self):
        return self.pid is not None
