import multiprocessing
from itertools import product, izip
from contextlib import contextmanager
import timeit

def merge_names(a, b):
    return '{} & {}'.format(a, b)

def merge_names_unpack(args):
    return merge_names(*args)


@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()

if __name__ == '__main__':
    start_time1 = timeit.default_timer()
    names = ['Brown', 'Sasa', 'Wilson', 'Bartlett', 'Rivera', 'Molloy', 'Opie','hehe', 'Mary']


    with poolcontext(processes=8) as pool:
        results = pool.map(merge_names_unpack, izip(names, names))

    '''
    results = list()
    for p in product(names, repeat = 2):
        results.append(merge_names_unpack(p))
    '''

    print(results)

    elapsed1 = timeit.default_timer() - start_time1
    print ("Function  %s seconds" % elapsed1)