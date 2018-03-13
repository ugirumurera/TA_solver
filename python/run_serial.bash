#!/bin/bash -l
#SBATCH -p regular
#SBATCH -N 1
#SBATCH -t 00:30:00
#SBATCH -J my_job
#SBATCH -o my_job.o%j
#SBATCH -L SCRATCH

module load java
module load python/2.7-anaconda
source activate myenv

python -u Runner_Static.py &

wait
