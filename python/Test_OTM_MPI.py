from __future__ import division
from Java_Connection import Java_Connection
import subprocess

# Flag that indicates whether we are doing decomposition or not
decomposition_flag = True

conn = Java_Connection(decomposition_flag)

if conn.pid is not None:
    # call otm-mpi on command line
    subprocess.call('echo $OTMMPIHOME', shell=True)