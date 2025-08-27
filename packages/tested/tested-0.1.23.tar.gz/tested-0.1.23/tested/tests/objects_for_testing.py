"""Some objects to use in tests"""

from functools import partial
from operator import eq


class A:
    def __init__(self, x):
        self.x = x

    def __add__(self, other):
        return self.x + other


class B(A):
    def __eq__(self, other):
        return self.x == other.x


a_list = [1, 2, 3]
a_tuple = (1, 2, 3)
a = A(42)
assert a + 1 == 43
b = B(42)
