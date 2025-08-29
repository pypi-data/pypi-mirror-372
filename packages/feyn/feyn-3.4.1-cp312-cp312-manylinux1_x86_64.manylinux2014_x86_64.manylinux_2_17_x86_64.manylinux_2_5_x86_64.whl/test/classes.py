import unittest
from contextlib import contextmanager


class ErrorTestCase(unittest.TestCase):
    @contextmanager
    def assertRaisesTypeErrorAndContainsParam(self, param):
        with self.assertRaises(TypeError) as ctx:
            yield
        strerr = str(ctx.exception)
        expected = f"{param} should be of type"
        return self.assertTrue(expected in strerr, f"Expected Error '{strerr}'' to contain string '{expected}''.")

    @contextmanager
    def assertRaisesAndContainsMessage(self, errtype, message):
        with self.assertRaises(errtype) as ctx:
            yield
        strerr = str(ctx.exception)
        return self.assertTrue(message in strerr, f"Expected Error '{strerr}'' to contain string '{message}''.")
