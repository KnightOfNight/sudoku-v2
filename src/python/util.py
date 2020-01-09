import time


def nanotime():
    return time.monotonic_ns() / 1000000000
