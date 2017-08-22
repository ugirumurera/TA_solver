from subprocess import call
import os
import subprocess
import signal
import platform
import time
import sys
import inspect


class Java_Connection():

    def __init__(self):

        self.process = None
        self.pid = None
        self.port_number = '25335'

        this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        jar_file_name = os.path.join(this_folder, 'py4jbeats-1.0-SNAPSHOT-jar-with-dependencies.jar')

        if platform.system() == "Windows":
            self.openWindows(jar_file_name, self.port_number)
        elif platform.system() == "Linux":
            self.openLinux(jar_file_name, self.port_number)
        else:
            raise Exception('Unknown platform')

        print(platform.system())

    def openWindows(self, jar_file_name, port_number):
        try:
            self.process = subprocess.Popen(['java', '-jar', jar_file_name, port_number],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.pid = self.process.pid
            time.sleep(0.5)
        except subprocess.CalledProcessError:
            print("caught exception")
            sys.exit()

    def openLinux(self, jar_file_name, port_number):

        pid = os.fork()
        # os_pid1 = os.getpid()

        if pid == 0:
            self.pid = os.getpid()
            retcode = call(['java', '-jar', jar_file_name, port_number])
            sys.exit()

        # Here we wait for 0.5 sec to allow the java server to start
        time.sleep(1)

    def close(self):
        if platform.system() == "Windows":
            self.process.terminate()
        elif platform.system() == "Linux":
            os.kill(self.pid, signal.CTRL_C_EVENT)
        else:
            raise Exception('Unknown platform')

    def is_valid(self):
        return self.pid is not None