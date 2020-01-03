from multiprocessing import Pool
from contextlib import closing

def f(x):
    return x*x

with closing(Pool(processes=2)) as p:
        print(p.map(f, [1, 2, 3]))
        p.terminate()