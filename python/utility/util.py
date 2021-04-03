import timeit


def tic():
    start_time = timeit.default_timer()
    return start_time


def toc(start_time):
    elapsed = timeit.default_timer() - start_time
    return elapsed


def print_toc(start_time, printstring, end_time=-1, units="msec"):
    if end_time == -1:
        end_time = timeit.default_timer()

    elapsed = end_time - start_time
    if units == "msec":
        elapsed *= 1000.0
        print(printstring, " {0:5.3f} ms".format(elapsed))
        return elapsed
    else:
        print("unknown units")
        exit()


def next_power_of_2(x):
    return 1 if x == 0 else 2 ** (x - 1).bit_length()


import sys
from types import ModuleType, FunctionType
from gc import get_referents

# Custom objects know their class.
# Function objects seem to know way too much, including modules.
# Exclude modules as well.
BLACKLIST = type, ModuleType, FunctionType


def getsize(obj):
    """sum size of object & members."""
    if isinstance(obj, BLACKLIST):
        raise TypeError('getsize() does not take argument of type: '+ str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size