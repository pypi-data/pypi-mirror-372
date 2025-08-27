"""
Test suite for gousset timing profiler.
"""

import unittest
import io
from contextlib import redirect_stdout

import gousset
from tests import module_a, module_b


class TestGousset(unittest.TestCase):
    """Test cases for gousset functionality"""

    def test_instrument_module_a(self):
        """Test instrumenting module A and capturing function calls"""
        # Instrument module A
        gousset.instrument(module_a)

        # Use functions multiple times
        for _ in range(5):
            result = module_a.slow_function()  # This calls fast_function internally
            self.assertEqual(result, "slow result")

        for _ in range(3):
            result = module_a.fast_function()
            self.assertEqual(result, "fast result")

        # Verify timing data was collected
        self.assertIn("tests.module_a", gousset.core._timings)
        self.assertIn("slow_function", gousset.core._timings["tests.module_a"])
        self.assertIn("fast_function", gousset.core._timings["tests.module_a"])

        # Should have 5 slow_function calls
        # and 8 fast_function calls (5 nested + 3 direct)
        self.assertEqual(
            len(gousset.core._timings["tests.module_a"]["slow_function"]), 5
        )
        self.assertEqual(
            len(gousset.core._timings["tests.module_a"]["fast_function"]), 8
        )

    def test_instrument_module_b(self):
        """Test instrumenting module B with recursive functions"""
        # Instrument module B
        gousset.instrument(module_b)

        # Test fibonacci
        x = list(range(1, 100))
        for _ in range(3):
            result = module_b.fibo(x)
            self.assertEqual(len(result), 99)

        # Test factorial (recursive - will create multiple calls)
        for _ in range(2):
            result = module_b.factorial(5)
            self.assertEqual(result, 120)

        # Verify timing data
        self.assertIn("tests.module_b", gousset.core._timings)
        self.assertIn("fibo", gousset.core._timings["tests.module_b"])
        self.assertIn("factorial", gousset.core._timings["tests.module_b"])

        # factorial(5) should create 5 calls each time (5, 4, 3, 2, 1)
        # So 2 calls to factorial(5) = 10 total calls
        self.assertEqual(len(gousset.core._timings["tests.module_b"]["factorial"]), 10)

    def test_statistics_output(self):
        """Test that statistics are properly formatted"""
        # Capture output from statistics printing
        with io.StringIO() as buf, redirect_stdout(buf):
            gousset.core._print_all_statistics()
            output = buf.getvalue()

        # Check that output contains expected elements
        self.assertIn("Gousset Timing Statistics", output)
        self.assertIn("Function:", output)
        self.assertIn("Calls:", output)
        self.assertIn("Average:", output)


def main():
    """Main test function demonstrating gousset usage"""
    print("=== Gousset Test Demonstration ===")

    # Test Module A
    print("\n1. Testing Module A (nested function calls)")
    gousset.instrument(module_a)

    for i in range(10):
        _ = module_a.slow_function()  # Calls fast_function internally

    for i in range(5):
        _ = module_a.medium_function()

    # Test Module B
    print("\n2. Testing Module B (recursive functions)")
    gousset.instrument(module_b)

    x = list(range(1, 1000))
    for i in range(5):
        _ = module_b.fibo(x)

    for i in range(3):
        _ = module_b.factorial(100)  # Shows many calls due to recursion

    for i in range(7):
        _ = module_b.sum_squares(1000)

    print("\nDone - statistics will be printed at exit")
    print("Notice how:")
    print("- slow_function calls also increment fast_function (nested calls)")
    print("- factorial shows many calls due to recursion")
    print("- Each module is reported separately")


if __name__ == "__main__":
    # Run the demonstration
    main()
