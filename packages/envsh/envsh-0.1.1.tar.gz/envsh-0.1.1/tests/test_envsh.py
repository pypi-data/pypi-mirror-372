import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import envsh

is_loaded = envsh.load(verbose=True)

class TestEnvsh(unittest.TestCase):
    """Tests for envsh."""

    def setUp(self) -> None:
        """Set up test environment."""
        if not is_loaded:
            self.skipTest("Environment not loaded")

    def test_read_env_various_types(self) -> None:
        """Test reading variables of different types and arrays."""
        self.assertEqual(envsh.read_env('TEST_INT', int), 123)
        self.assertEqual(envsh.read_env('TEST_FLOAT', float), 45.67)
        self.assertEqual(envsh.read_env('TEST_STR', str), 'Hello, World!')
        self.assertEqual(envsh.read_env('TEST_INT_ARRAY', list[int]), [1, 123, 3, 4, 5])
        self.assertEqual(envsh.read_env('TEST_STR_ARRAY', list[str]), ['foo', 'Hello', 'World!', 'baz'])

    def test_interpolation_and_calculation(self) -> None:
        """Test interpolation and calculations in environment variables."""
        base_int = envsh.read_env('TEST_INT', int)
        base_str = envsh.read_env('TEST_STR', str)
        int_array = envsh.read_env('TEST_INT_ARRAY', list[int])
        str_array = envsh.read_env('TEST_STR_ARRAY', list[str])
        mixed_array = envsh.read_env('TEST_MIXED_INTERPOLATION', list[str])
        calc_array = envsh.read_env('TEST_CALCULATED_ARRAY', list[int])
        self.assertIn(base_int, int_array)
        self.assertIn(base_str.split(',')[0], str_array)
        self.assertTrue(any("base" in item for item in mixed_array))
        self.assertEqual(calc_array, [123, 133, 246])

    def test_empty_and_spaces(self) -> None:
        """Test handling of empty values and spaces."""
        self.assertEqual(envsh.read_env('TEST_EMPTY_STR', str), '')
        self.assertEqual(envsh.read_env('TEST_EMPTY_ARRAY', list[str]), [])
        self.assertEqual(envsh.read_env('TEST_SPACES_ARRAY', list[str]), ['apple', 'banana', 'cherry'])

    def test_errors(self) -> None:
        """Test error handling: nonexistent variable, wrong type, invalid values."""
        with self.assertRaises(EnvironmentError):
            envsh.read_env('NONEXISTENT_VAR', str)
        os.environ['TEST_INVALID_INT'] = 'not_a_number'
        with self.assertRaises(ValueError):
            envsh.read_env('TEST_INVALID_INT', int)
        os.environ['TEST_INVALID_INT_ARRAY'] = '1,not_a_number,3'
        with self.assertRaises(ValueError):
            envsh.read_env('TEST_INVALID_INT_ARRAY', list[int])
        with self.assertRaises(TypeError):
            envsh.read_env('TEST_STR_ARRAY', dict) # type: ignore[arg-type]

    def test_special_and_dynamic(self) -> None:
        """Test special characters and dynamic strings."""
        self.assertEqual(envsh.read_env('TEST_SPECIAL_CHARS', list[str]), ['hello world', 'test@example.com'])
        result = envsh.read_env('TEST_DYNAMIC_STRING', str)
        self.assertIn("Generated", result)
        self.assertTrue(result.startswith("Generated at "))


if __name__ == '__main__':
    unittest.main()
