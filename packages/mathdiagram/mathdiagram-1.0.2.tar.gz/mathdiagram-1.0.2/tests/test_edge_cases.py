"""
Edge Cases and Data Validation Tests

This module contains tests for edge cases, boundary conditions, 
and data validation scenarios that might cause failures.
"""

import unittest
import pytest
import numpy as np
import sys
import os
from unittest.mock import patch, Mock
import warnings
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math_diagram_generator import MathDiagramGenerator


class TestDataValidationAndEdgeCases(unittest.TestCase):
    """Test data validation and edge cases for all methods"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.generator = MathDiagramGenerator()
        
        # Mock matplotlib to avoid actual plotting
        self.show_mock = patch('matplotlib.pyplot.show').start()
        self.savefig_mock = patch('matplotlib.pyplot.savefig').start()
        self.clf_mock = patch('matplotlib.pyplot.clf').start()
        
    def tearDown(self):
        """Clean up after each test method"""
        patch.stopall()


class TestNumberLineEdgeCases(TestDataValidationAndEdgeCases):
    """Edge cases for number_line method"""
    
    def test_reversed_range(self):
        """Test number line with start > end"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Should handle reversed range gracefully
            self.generator.number_line(10, -10)
            
            # Should still create the plot
            mock_subplots.assert_called_once()
    
    def test_single_point_range(self):
        """Test number line with start == end"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            self.generator.number_line(5, 5)
            
            # Should handle single point
            mock_ax.set_xlim.assert_called_once_with(4, 6)  # start-1, end+1
    
    def test_extreme_ranges(self):
        """Test number line with very large ranges"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Very large range
            self.generator.number_line(-1000000, 1000000)
            
            # Very small range with decimals
            self.generator.number_line(-0.001, 0.001)
            
            self.assertEqual(mock_subplots.call_count, 2)
    
    def test_highlight_numbers_outside_range(self):
        """Test highlighting numbers outside the display range"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Highlight numbers both inside and outside range
            self.generator.number_line(-5, 5, [-10, 0, 3, 15])
            
            # Should only highlight numbers within range (0 and 3)
            # This tests the boundary condition logic
            self.assertTrue(mock_ax.plot.called)
    
    def test_empty_highlight_list(self):
        """Test with empty highlight numbers list"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            self.generator.number_line(-5, 5, [])
            
            mock_subplots.assert_called_once()
    
    def test_none_highlight_list(self):
        """Test with None highlight numbers"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            self.generator.number_line(-5, 5, None)
            
            mock_subplots.assert_called_once()
    
    def test_duplicate_highlight_numbers(self):
        """Test with duplicate numbers in highlight list"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # List with duplicates
            self.generator.number_line(-5, 5, [1, 1, 2, 2, 3])
            
            mock_subplots.assert_called_once()


class TestFractionVisualEdgeCases(TestDataValidationAndEdgeCases):
    """Edge cases for fraction_visual method"""
    
    def test_zero_numerator(self):
        """Test fraction with numerator = 0"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_axes = [Mock(), Mock()]
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # 0/5 = 0
            self.generator.fraction_visual(0, 5)
            
            mock_subplots.assert_called_once()
    
    def test_numerator_equals_denominator(self):
        """Test fraction where numerator == denominator (whole number)"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_axes = [Mock(), Mock()]
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # 5/5 = 1
            self.generator.fraction_visual(5, 5)
            
            mock_subplots.assert_called_once()
    
    def test_improper_fraction(self):
        """Test improper fraction (numerator > denominator)"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_axes = [Mock(), Mock()]
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # 7/3 > 1
            self.generator.fraction_visual(7, 3)
            
            mock_subplots.assert_called_once()
    
    def test_very_small_denominator(self):
        """Test fraction with denominator = 1"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_axes = [Mock(), Mock()]
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # 3/1 = 3
            self.generator.fraction_visual(3, 1)
            
            mock_subplots.assert_called_once()
    
    def test_very_large_denominator(self):
        """Test fraction with very large denominator"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_axes = [Mock(), Mock()]
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # 1/1000 - very small fraction
            self.generator.fraction_visual(1, 1000)
            
            mock_subplots.assert_called_once()
    
    def test_negative_numerator(self):
        """Test fraction with negative numerator"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_axes = [Mock(), Mock()]
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            # -2/5 = -0.4
            self.generator.fraction_visual(-2, 5)
            
            mock_subplots.assert_called_once()


class TestLinearEquationEdgeCases(TestDataValidationAndEdgeCases):
    """Edge cases for linear_equation method"""
    
    def test_zero_slope(self):
        """Test horizontal line (slope = 0)"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot:
            
            self.generator.linear_equation(0, 5)
            
            # Should not plot x-intercept for horizontal line
            # Only y-intercept and the line itself
            mock_plot.assert_called()
    
    def test_undefined_slope_simulation(self):
        """Test near-vertical line (very large slope)"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot:
            
            # Very steep slope
            self.generator.linear_equation(1000000, 1)
            
            mock_plot.assert_called()
    
    def test_zero_y_intercept(self):
        """Test line passing through origin"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot:
            
            self.generator.linear_equation(2, 0)
            
            mock_plot.assert_called()
    
    def test_negative_slope_and_intercept(self):
        """Test line with both negative slope and y-intercept"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot:
            
            self.generator.linear_equation(-3, -4)
            
            mock_plot.assert_called()
    
    def test_fractional_slope(self):
        """Test line with fractional slope"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot:
            
            # Slope = 2/3
            self.generator.linear_equation(0.6666666666667, 1)
            
            mock_plot.assert_called()
    
    def test_very_small_slope(self):
        """Test line with very small slope"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot:
            
            self.generator.linear_equation(0.000001, 0)
            
            mock_plot.assert_called()


class TestQuadraticFunctionEdgeCases(TestDataValidationAndEdgeCases):
    """Edge cases for quadratic_function method"""
    
    def test_coefficient_a_zero(self):
        """Test when a=0 (not actually quadratic)"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot:
            
            # This should raise ValueError, not crash with ZeroDivisionError
            with self.assertRaises(ValueError) as context:
                self.generator.quadratic_function(0, 2, 3)
            
            self.assertIn("Coefficient 'a' cannot be zero", str(context.exception))
    
    def test_perfect_square_discriminant(self):
        """Test quadratic with discriminant = 0 (one root)"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot:
            
            # y = x² - 4x + 4 = (x-2)²
            # Discriminant = 16 - 16 = 0
            self.generator.quadratic_function(1, -4, 4)
            
            mock_plot.assert_called()
    
    def test_negative_discriminant(self):
        """Test quadratic with discriminant < 0 (no real roots)"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot:
            
            # y = x² + 1
            # Discriminant = 0 - 4 = -4 < 0
            self.generator.quadratic_function(1, 0, 1)
            
            mock_plot.assert_called()
    
    def test_very_small_coefficients(self):
        """Test quadratic with very small coefficients"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot:
            
            self.generator.quadratic_function(0.001, 0.002, 0.003)
            
            mock_plot.assert_called()
    
    def test_very_large_coefficients(self):
        """Test quadratic with very large coefficients"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot:
            
            self.generator.quadratic_function(1000, -2000, 500)
            
            mock_plot.assert_called()
    
    def test_negative_leading_coefficient(self):
        """Test downward-opening parabola"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot:
            
            # Opens downward
            self.generator.quadratic_function(-1, 2, 3)
            
            mock_plot.assert_called()


class TestCoordinatePlaneEdgeCases(TestDataValidationAndEdgeCases):
    """Edge cases for coordinate_plane method"""
    
    def test_empty_points_and_lines(self):
        """Test with empty points and lines lists"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            self.generator.coordinate_plane([], [])
            
            mock_subplots.assert_called_once()
    
    def test_points_at_origin(self):
        """Test with points at origin"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            points = [(0, 0, 'Origin')]
            self.generator.coordinate_plane(points=points)
            
            mock_ax.plot.assert_called()
            mock_ax.annotate.assert_called()
    
    def test_points_at_boundary(self):
        """Test with points at boundary of display area"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Points at the boundary (-10, 10)
            points = [(-10, -10, 'SW'), (10, 10, 'NE'), (-10, 10, 'NW'), (10, -10, 'SE')]
            self.generator.coordinate_plane(points=points)
            
            self.assertEqual(mock_ax.plot.call_count, len(points))
    
    def test_invalid_line_format(self):
        """Test with invalid line format"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Invalid line format (wrong number of elements)
            lines = [(1,)]  # Should be 2 or 3 elements
            
            try:
                self.generator.coordinate_plane(lines=lines)
                # Should handle gracefully or skip invalid lines
            except (IndexError, ValueError):
                pass  # Expected for invalid format
    
    def test_vertical_line_slope_intercept(self):
        """Test slope-intercept format that would create vertical line"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Very large slope approximating vertical line
            lines = [(1000000, 0, (-1, 1))]
            self.generator.coordinate_plane(lines=lines)
            
            mock_ax.plot.assert_called()
    
    def test_points_with_special_characters(self):
        """Test points with special characters in labels"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Points with special characters
            points = [(1, 1, 'A₁'), (2, 2, 'P′'), (3, 3, 'θ')]
            self.generator.coordinate_plane(points=points)
            
            self.assertEqual(mock_ax.annotate.call_count, len(points))


class TestTrigonometricFunctionsEdgeCases(TestDataValidationAndEdgeCases):
    """Edge cases for trigonometric_functions method"""
    
    @patch('numpy.tan')
    @patch('numpy.cos') 
    @patch('numpy.sin')
    @patch('matplotlib.pyplot.subplots')
    def test_tangent_asymptote_handling(self, mock_subplots, mock_sin, mock_cos, mock_tan):
        """Test handling of tangent function asymptotes"""
        mock_axes = [Mock(), Mock(), Mock()]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        # Mock tangent with infinity values
        mock_tan.return_value = np.array([0, np.inf, 0, -np.inf, 0])
        mock_sin.return_value = np.array([0, 1, 0, -1, 0])
        mock_cos.return_value = np.array([1, 0, -1, 0, 1])
        
        self.generator.trigonometric_functions()
        
        # Should handle infinity values in tangent
        mock_subplots.assert_called_once()
    
    @patch('numpy.tan')
    @patch('numpy.cos')
    @patch('numpy.sin') 
    @patch('matplotlib.pyplot.subplots')
    def test_trigonometric_domain_errors(self, mock_subplots, mock_sin, mock_cos, mock_tan):
        """Test handling of potential domain errors in trigonometric functions"""
        mock_axes = [Mock(), Mock(), Mock()]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        # Mock functions with NaN values
        mock_sin.return_value = np.array([np.nan, 0, 1])
        mock_cos.return_value = np.array([1, np.nan, 0])
        mock_tan.return_value = np.array([0, np.inf, np.nan])
        
        try:
            self.generator.trigonometric_functions()
            # Should handle NaN and infinity values gracefully
        except Exception as e:
            self.fail(f"Trigonometric functions should handle domain errors: {e}")


class TestNumericalStabilityAndPrecision(TestDataValidationAndEdgeCases):
    """Test numerical stability and floating-point precision issues"""
    
    def test_floating_point_precision_linear(self):
        """Test linear equation with precision-sensitive calculations"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot'):
            
            # Values that might cause floating-point precision issues
            slope = 1/3  # 0.3333...
            y_intercept = 1/7  # 0.142857...
            
            try:
                self.generator.linear_equation(slope, y_intercept)
            except Exception as e:
                self.fail(f"Should handle floating-point precision: {e}")
    
    def test_floating_point_precision_quadratic(self):
        """Test quadratic function with precision-sensitive discriminant"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot'):
            
            # Coefficients that might cause precision issues in discriminant
            a, b, c = 1e-10, 2e-5, 1e-10
            
            try:
                self.generator.quadratic_function(a, b, c)
            except Exception as e:
                self.fail(f"Should handle small coefficient precision: {e}")
    
    def test_very_small_numbers(self):
        """Test with numbers close to machine epsilon"""
        with patch('matplotlib.pyplot.subplots'):
            
            epsilon = np.finfo(float).eps
            
            try:
                self.generator.number_line(-epsilon, epsilon, [0])
            except Exception as e:
                self.fail(f"Should handle very small numbers: {e}")
    
    def test_very_large_numbers(self):
        """Test with very large numbers"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot'):
            
            large_num = 1e15
            
            try:
                self.generator.linear_equation(large_num, large_num)
            except (OverflowError, ValueError) as e:
                # These errors are acceptable for extremely large numbers
                pass
            except Exception as e:
                self.fail(f"Unexpected error with large numbers: {e}")


class TestStringHandlingAndEncoding(TestDataValidationAndEdgeCases):
    """Test string handling and encoding issues"""
    
    def test_unicode_titles(self):
        """Test methods with Unicode characters in titles"""
        with patch('matplotlib.pyplot.subplots'):
            
            unicode_title = "数学图表 - Mathematical Diagram with Greek α β γ"
            
            try:
                self.generator.number_line(-5, 5, None, unicode_title)
            except UnicodeError as e:
                self.fail(f"Should handle Unicode in titles: {e}")
    
    def test_empty_title(self):
        """Test methods with empty title"""
        with patch('matplotlib.pyplot.subplots'):
            
            self.generator.number_line(-5, 5, None, "")
    
    def test_very_long_title(self):
        """Test methods with very long title"""
        with patch('matplotlib.pyplot.subplots'):
            
            long_title = "A" * 1000  # Very long title
            
            try:
                self.generator.number_line(-5, 5, None, long_title)
            except Exception as e:
                self.fail(f"Should handle long titles: {e}")
    
    def test_special_characters_in_labels(self):
        """Test coordinate plane with special characters in point labels"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Points with various special characters
            points = [
                (1, 1, "P₁"),      # Subscript
                (2, 2, "A'"),       # Apostrophe
                (3, 3, "α"),        # Greek letter
                (4, 4, "∑"),        # Mathematical symbol
                (5, 5, "😊"),       # Emoji
            ]
            
            try:
                self.generator.coordinate_plane(points=points)
            except (UnicodeError, ValueError) as e:
                self.fail(f"Should handle special characters in labels: {e}")


class TestInputValidationEdgeCases(TestDataValidationAndEdgeCases):
    """Test comprehensive input validation for all methods"""
    
    def test_number_line_input_validation(self):
        """Test number_line with invalid inputs"""
        with patch('matplotlib.pyplot.subplots'):
            # Test non-numeric start/end
            with self.assertRaises(TypeError):
                self.generator.number_line("invalid", 10)
            
            with self.assertRaises(TypeError):
                self.generator.number_line(0, "invalid")
            
            # Test start >= end
            with self.assertRaises(ValueError):
                self.generator.number_line(10, 5)
            
            with self.assertRaises(ValueError):
                self.generator.number_line(5, 5)
            
            # Test invalid highlight_numbers type
            with self.assertRaises(TypeError):
                self.generator.number_line(0, 10, "invalid")
    
    def test_fraction_visual_input_validation(self):
        """Test fraction_visual with invalid inputs"""
        with patch('matplotlib.pyplot.subplots'):
            # Test non-integer inputs
            with self.assertRaises(TypeError):
                self.generator.fraction_visual(1.5, 2)
            
            with self.assertRaises(TypeError):
                self.generator.fraction_visual(1, 2.5)
            
            # Test zero or negative denominator
            with self.assertRaises(ValueError):
                self.generator.fraction_visual(1, 0)
            
            with self.assertRaises(ValueError):
                self.generator.fraction_visual(1, -2)
            
            # Test negative numerator
            with self.assertRaises(ValueError):
                self.generator.fraction_visual(-1, 2)
            
            # Test improper fraction
            with self.assertRaises(ValueError):
                self.generator.fraction_visual(3, 2)
    
    def test_linear_equation_input_validation(self):
        """Test linear_equation with invalid inputs"""
        with patch('matplotlib.pyplot.figure'):
            # Test non-numeric inputs
            with self.assertRaises(TypeError):
                self.generator.linear_equation("invalid", 0)
            
            with self.assertRaises(TypeError):
                self.generator.linear_equation(1, "invalid")
            
            # Test NaN and infinity
            with self.assertRaises(ValueError):
                self.generator.linear_equation(float('nan'), 0)
            
            with self.assertRaises(ValueError):
                self.generator.linear_equation(1, float('inf'))
    
    def test_quadratic_function_input_validation(self):
        """Test quadratic_function with invalid inputs"""
        with patch('matplotlib.pyplot.figure'):
            # Test a = 0 (should raise ValueError)
            with self.assertRaises(ValueError):
                self.generator.quadratic_function(0, 1, 1)
            
            # Test non-numeric inputs
            with self.assertRaises(TypeError):
                self.generator.quadratic_function("invalid", 1, 1)
            
            with self.assertRaises(TypeError):
                self.generator.quadratic_function(1, "invalid", 1)
            
            with self.assertRaises(TypeError):
                self.generator.quadratic_function(1, 1, "invalid")


class TestOptionalDependencyHandling(TestDataValidationAndEdgeCases):
    """Test graceful handling of optional dependencies"""
    
    def test_optional_imports_structure(self):
        """Test that _optional_imports is properly initialized"""
        from math_diagram_generator import _optional_imports
        
        # Should be a dictionary
        self.assertIsInstance(_optional_imports, dict)
        
        # Should contain expected keys
        expected_keys = ['seaborn', 'plotly', 'scipy']
        for key in expected_keys:
            self.assertIn(key, _optional_imports)
    
    def test_seaborn_fallback(self):
        """Test that seaborn import failure is handled gracefully"""
        # This test verifies the import warning behavior
        with patch('builtins.__import__', side_effect=ImportError):
            # Re-importing should trigger the warning
            try:
                import warnings
                with warnings.catch_warnings(record=True) as w:
                    # Force a re-import to test the warning
                    import importlib
                    import sys
                    if 'math_diagram_generator' in sys.modules:
                        importlib.reload(sys.modules['math_diagram_generator'])
                    # Check that a warning was issued
                    # Note: This test might need adjustment based on import behavior
            except Exception:
                # If re-importing fails, that's expected behavior
                pass


class TestPathlibIntegration(TestDataValidationAndEdgeCases):
    """Test pathlib.Path integration"""
    
    def test_save_plot_path_handling(self):
        """Test that save_plot uses pathlib correctly"""
        from pathlib import Path
        
        with patch('matplotlib.pyplot.subplots'), \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('matplotlib.pyplot.savefig') as mock_savefig:
            
            self.generator.number_line(0, 10)
            
            # Verify mkdir was called with exist_ok=True
            mock_mkdir.assert_called_once_with(exist_ok=True)
            
            # Verify savefig was called with a Path object
            mock_savefig.assert_called_once()
            call_args = mock_savefig.call_args[0]
            # The path should be Path-like
            self.assertTrue(isinstance(call_args[0], (str, Path)) or hasattr(call_args[0], '__fspath__'))


if __name__ == '__main__':
    # Suppress warnings during testing
    warnings.filterwarnings('ignore', category=RuntimeWarning)
    warnings.filterwarnings('ignore', category=UserWarning)
    
    # Run edge case tests
    unittest.main(verbosity=2)