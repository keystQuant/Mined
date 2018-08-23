import time


def timeit(method):
    """decorator for timing processes"""

    def timed(*args, **kwargs):
        ts = time.time()
        method(*args, **kwargs)
        te = time.time()
        print("Process took " + str(te - ts) + " seconds")

    return timed
