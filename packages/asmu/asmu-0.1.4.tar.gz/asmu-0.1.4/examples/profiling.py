"""File that stores useful commands and a small test code for profiling."""
import numpy as np

# check for line_profiler or memory_profiler in the local scope, both
# are injected by their respective tools or they're absent
# if these tools aren't being used (in which case we need to substitute
# a dummy @profile decorator)
if 'prof' not in dir() and 'profile' not in dir():
    def profile(func):
        def inner(*args, **kwargs):
            return func(*args, **kwargs)
        return inner


@profile
def copy_test():
    a = np.ones((100000, 2))
    b = np.empty(100000)

    np.copyto(b, a[:, 1])
    b[:] = a[:, 1]


def slice_test():
    buffer = np.ones((100000, 2))
    data = np.zeros(20000)
    data2 = np.zeros((20000, 1))

    np.copyto(buffer[500:20500, 1], data)
    buffer[500:20500, 1] = data

    np.copyto(buffer[500:20500, 1:2], data2)
    buffer[500:20500, 1:2] = data2


def random_test():
    buffer = np.zeros(20000)

    rng = np.random.default_rng()
    rng.standard_normal(20000, out=buffer, dtype=np.float64)
    print(np.max(np.abs(buffer)))

    buffer = np.random.randn(20000)


def multiply_test():
    a = np.ones(20000)
    b = np.ones(20000)*5

    a[:] *= 5
    a *= 5

    a[:] *= b
    a *= b


if __name__ == "__main__":
    copy_test()

# kernprof -l -v ./profiling.py
# python -m memory_profiler ./profiling.py
