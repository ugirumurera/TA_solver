from subprocess import call
import os
import subprocess
import signal
import platform
import time
import sys
import inspect
from py4j.java_gateway import JavaGateway, GatewayParameters


class Java_Connection():

    def __init__(self):

        self.process = None
        self.pid = None
        rank = 0
        port_num = 25335 + rank
        self.port_number = str(port_num)

        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        jar_file_name = os.path.join(this_folder, 'py4jbeats-1.0-SNAPSHOT-jar-with-dependencies.jar')

        #First check if the file exists indeed:
        if os.path.isfile('py4jbeats-1.0-SNAPSHOT-jar-with-dependencies.jar'):

            if platform.system() == "Windows":
                self.openWindows(jar_file_name, self.port_number)
            elif platform.system() == "Linux":
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

        self.pid = os.fork()

        if self.pid == 0:
            self.pid = os.getpid()
            retcode = call(['java', '-jar', jar_file_name, port_number])
            sys.exit()

        # Here we wait for 0.5 sec to allow the java server to start
        time.sleep(1)

    def close(self):
        if platform.system() == "Windows":
            #self.process.terminate()
            os.kill(self.process.pid, signal.CTRL_C_EVENT)
        elif platform.system() == "Linux":
            os.kill(0, signal.SIGTERM)
        else:
            raise Exception('Unknown platform')

    def is_valid(self):
        return self.pid is not None