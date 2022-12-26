import sys
import time


def time_measure(f):
    def wrapper(*args, **kwargs):
        start = time.time()
        # cProfile.runctx('f(update, context)', globals(), locals())
        result = f(*args, **kwargs)
        delta = time.time() - start
        print(f'{start = :.1f} {delta = :.1f} sec           {f.__name__}()', file=sys.stderr)  # {args = } {kwargs = }',
        return result

    return wrapper
