import unittest

from scaevola.core import Scaevola


class TestScaevolaDocstrings(unittest.TestCase):
    def test_methods_have_docstrings(self):
        methods_to_check = [
            "__ge__",
            "__gt__",
            "__radd__",
            "__rand__",
            "__rdivmod__",
            "__rfloordiv__",
            "__rlshift__",
            "__rmatmul__",
            "__rmod__",
            "__rmul__",
            "__ror__",
            "__rpow__",
            "__rrshift__",
            "__rsub__",
            "__rtruediv__",
            "__rxor__",
        ]

        for name in methods_to_check:
            method = getattr(Scaevola, name, None)
            with self.subTest(method=name):
                self.assertIsNotNone(
                    method.__doc__, f"Method {name} is missing a docstring"
                )
                self.assertGreater(
                    len(method.__doc__.strip()),
                    0,
                    f"Method {name} has an empty docstring",
                )


if __name__ == "__main__":
    unittest.main()
