import unittest

from scaevola.core import Scaevola


# Subclass of Scaevola to implement basic arithmetic and comparison operations
class ScaevolaSubclass(Scaevola):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return self.value == other.value
        raise NotImplementedError

    def __lt__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return self.value < other.value
        raise NotImplementedError

    def __le__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return self.value <= other.value
        raise NotImplementedError

    def __add__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return ScaevolaSubclass(self.value + other.value)
        raise NotImplementedError

    def __and__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return ScaevolaSubclass(self.value & other.value)
        raise NotImplementedError

    def __divmod__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return divmod(self.value, other.value)
        raise NotImplementedError

    def __floordiv__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return ScaevolaSubclass(self.value // other.value)
        raise NotImplementedError

    def __lshift__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return ScaevolaSubclass(self.value << other.value)
        raise NotImplementedError

    def __matmul__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return ScaevolaSubclass(
                self.value * other.value
            )  # Simulating matrix multiplication
        raise NotImplementedError

    def __mod__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return ScaevolaSubclass(self.value % other.value)
        raise NotImplementedError

    def __mul__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return ScaevolaSubclass(self.value * other.value)
        raise NotImplementedError

    def __or__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return ScaevolaSubclass(self.value | other.value)
        raise NotImplementedError

    def __pow__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return ScaevolaSubclass(self.value**other.value)
        raise NotImplementedError

    def __rshift__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return ScaevolaSubclass(self.value >> other.value)
        raise NotImplementedError

    def __sub__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return ScaevolaSubclass(self.value - other.value)
        raise NotImplementedError

    def __truediv__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return ScaevolaSubclass(self.value / other.value)
        raise NotImplementedError

    def __xor__(self, other):
        if isinstance(other, ScaevolaSubclass):
            return ScaevolaSubclass(self.value ^ other.value)
        raise NotImplementedError


class TestScaevola(unittest.TestCase):
    def setUp(self):
        self.obj1 = ScaevolaSubclass(10)
        self.obj2 = ScaevolaSubclass(20)

    def test_ge(self):
        self.assertTrue(self.obj2 >= 10)
        self.assertFalse(self.obj1 >= 20)

    def test_gt(self):
        self.assertTrue(self.obj2 > 10)
        self.assertFalse(self.obj1 > 20)

    def test_radd(self):
        result = 15 + self.obj1
        self.assertEqual(result.value, 25)

    def test_rand(self):
        result = 15 & self.obj1
        self.assertEqual(result.value, 10 & 15)

    def test_rdivmod(self):
        result = divmod(25, self.obj1)
        self.assertEqual(result, (2, 5))

    def test_rfloordiv(self):
        result = 25 // self.obj1
        self.assertEqual(result.value, 2)

    def test_rlshift(self):
        result = 2 << self.obj1
        self.assertEqual(result.value, 2 << 10)

    def test_rmatmul(self):
        result = 2 @ self.obj1
        self.assertEqual(result.value, 2 * 10)

    def test_rmod(self):
        result = 23 % self.obj1
        self.assertEqual(result.value, 23 % 10)

    def test_rmul(self):
        result = 2 * self.obj1
        self.assertEqual(result.value, 20)

    def test_ror(self):
        result = 2 | self.obj1
        self.assertEqual(result.value, 2 | 10)

    def test_rpow(self):
        result = 2**self.obj1
        self.assertEqual(result.value, 2**10)

    def test_rrshift(self):
        result = 1024 >> self.obj1
        self.assertEqual(result.value, 1024 >> 10)

    def test_rsub(self):
        result = 25 - self.obj1
        self.assertEqual(result.value, 25 - 10)

    def test_rtruediv(self):
        result = 100 / self.obj1
        self.assertEqual(result.value, 100 / 10)

    def test_rxor(self):
        result = 15 ^ self.obj1
        self.assertEqual(result.value, 15 ^ 10)


if __name__ == "__main__":
    unittest.main()
