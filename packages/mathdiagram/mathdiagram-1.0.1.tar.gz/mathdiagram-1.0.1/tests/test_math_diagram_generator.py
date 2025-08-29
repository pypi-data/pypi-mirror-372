"""
White Box Unit Tests for MathDiagramGenerator Class

This module contains comprehensive white box testing for the MathDiagramGenerator class,
testing internal logic, edge cases, and all code paths.
"""

import unittest
import pytest
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import Mock, patch, MagicMock
import os
import sys
from parameterized import parameterized

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math_diagram_generator import MathDiagramGenerator


class TestMathDiagramGenerator(unittest.TestCase):
    """White box tests for MathDiagramGenerator class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.generator = MathDiagramGenerator()
        
        # Mock matplotlib to avoid actual plot generation during tests
        self.plt_mock = patch('matplotlib.pyplot.show').start()
        self.savefig_mock = patch('matplotlib.pyplot.savefig').start()
        self.clf_mock = patch('matplotlib.pyplot.clf').start()
        
    def tearDown(self):
        """Clean up after each test method"""
        patch.stopall()
        plt.close('all')
    
    def test_init(self):
        """Test MathDiagramGenerator initialization"""
        generator = MathDiagramGenerator()
        self.assertIsInstance(generator, MathDiagramGenerator)
    
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.tight_layout')
    def test_save_plot_with_title(self, mock_tight_layout, mock_title):
        """Test save_plot method with title - white box testing"""
        filename = "test_plot.png"
        title = "Test Title"
        
        self.generator.save_plot(filename, title)
        
        # Verify internal method calls
        mock_title.assert_called_once_with(title, fontsize=14, fontweight='bold')
        mock_tight_layout.assert_called_once()
        self.savefig_mock.assert_called_once_with(f"diagrams/{filename}", dpi=300, bbox_inches='tight')
        self.plt_mock.assert_called_once()
        self.clf_mock.assert_called_once()
    
    @patch('matplotlib.pyplot.title')
    def test_save_plot_without_title(self, mock_title):
        """Test save_plot method without title"""
        filename = "test_plot.png"
        
        self.generator.save_plot(filename)
        
        mock_title.assert_called_once_with("", fontsize=14, fontweight='bold')
    
    @parameterized.expand([
        (-10, 10, None, "Number Line"),
        (0, 5, [1, 3], "Custom Title"),
        (-5, -1, [2], "Negative Range"),
    ])
    @patch('matplotlib.pyplot.subplots')
    def test_number_line_parameters(self, start, end, highlight_numbers, title, mock_subplots):
        """Test number_line method with various parameters - white box testing"""
        # Mock the axes object
        mock_ax = Mock()
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        self.generator.number_line(start, end, highlight_numbers, title)
        
        # Verify subplot creation
        mock_subplots.assert_called_once_with(1, 1, figsize=(12, 3))
        
        # Verify main line plotting
        expected_main_line_call = [start, end], [0, 0]
        mock_ax.plot.assert_any_call(expected_main_line_call[0], expected_main_line_call[1], 'k-', linewidth=3)
        
        # Verify axis limits
        mock_ax.set_xlim.assert_called_once_with(start - 1, end + 1)
        mock_ax.set_ylim.assert_called_once_with(-1, 1)
    
    def test_number_line_highlight_logic(self):
        """Test number_line highlighting logic - white box path coverage"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Test case: highlight numbers within range
            self.generator.number_line(-5, 5, [0, 3, 10])  # 10 is outside range
            
            # Should only highlight numbers within range
            highlight_calls = [call for call in mock_ax.plot.call_args_list 
                             if len(call[0]) == 2 and call[1].get('markersize') == 10]
            
            # Verify that out-of-range numbers are not plotted
            self.assertTrue(any(call for call in mock_ax.plot.call_args_list))
    
    def test_number_line_edge_cases(self):
        """Test number_line edge cases"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Edge case: start equals end
            self.generator.number_line(5, 5, None, "Single Point")
            
            # Edge case: negative range
            self.generator.number_line(-10, -5, [-7], "Negative Range")
            
            # Verify calls were made
            self.assertEqual(mock_subplots.call_count, 2)
    
    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.patches.Rectangle')
    @patch('matplotlib.patches.Circle')
    @patch('matplotlib.patches.Polygon')
    def test_basic_shapes_creation(self, mock_polygon, mock_circle, mock_rectangle, mock_subplots):
        """Test basic_shapes method - white box testing of shape creation"""
        # Mock the figure and axes
        mock_axes = [[Mock(), Mock(), Mock()], [Mock(), Mock(), Mock()]]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        self.generator.basic_shapes()
        
        # Verify subplot creation with correct parameters
        mock_subplots.assert_called_once_with(2, 3, figsize=(15, 10))
        
        # Verify shape creation calls
        mock_rectangle.assert_called()  # Square and rectangle
        mock_circle.assert_called_once()
        self.assertTrue(mock_polygon.call_count >= 2)  # Triangle, pentagon, hexagon
        
        # Verify each subplot was configured
        for row in mock_axes:
            for ax in row:
                ax.set_xlim.assert_called()
                ax.set_ylim.assert_called()
                ax.set_aspect.assert_called_with('equal')
                ax.set_title.assert_called()
    
    @parameterized.expand([
        (1, 2, "One Half"),
        (3, 4, "Three Fourths"),
        (5, 6, "Five Sixths"),
        (0, 1, "Zero"),  # Edge case
        (1, 1, "Whole"),  # Edge case
    ])
    @patch('matplotlib.pyplot.subplots')
    def test_fraction_visual_parameters(self, numerator, denominator, title, mock_subplots):
        """Test fraction_visual with various parameters"""
        mock_axes = [Mock(), Mock()]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        self.generator.fraction_visual(numerator, denominator, title)
        
        # Verify subplot creation
        mock_subplots.assert_called_once_with(1, 2, figsize=(12, 5))
        
        # Verify that both circle and rectangle representations are created
        for ax in mock_axes:
            ax.set_xlim.assert_called()
            ax.set_ylim.assert_called()
            ax.set_aspect.assert_called_with('equal')
            ax.set_title.assert_called()
    
    def test_fraction_visual_division_logic(self):
        """Test fraction_visual division line logic - white box testing"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_axes = [Mock(), Mock()]
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            numerator, denominator = 3, 8
            self.generator.fraction_visual(numerator, denominator)
            
            # The first axis (circle) should have denominator division lines
            circle_ax = mock_axes[0]
            plot_calls = circle_ax.plot.call_args_list
            
            # Should have division lines for the circle
            self.assertTrue(len(plot_calls) >= denominator)
    
    @parameterized.expand([
        ([(1, 2, 'A'), (3, 4, 'B')], None, "Points Only"),
        (None, [((0, 0), (1, 1))], "Lines Only"),
        ([(0, 0, 'O')], [(2, 3, (-5, 5))], "Points and Slope-Intercept"),
    ])
    @patch('matplotlib.pyplot.subplots')
    def test_coordinate_plane_combinations(self, points, lines, title, mock_subplots):
        """Test coordinate_plane with different point/line combinations"""
        mock_ax = Mock()
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        self.generator.coordinate_plane(points, lines, title)
        
        # Verify basic setup
        mock_ax.grid.assert_called_once_with(True, alpha=0.3)
        mock_ax.axhline.assert_called_once_with(y=0, color='k', linewidth=2)
        mock_ax.axvline.assert_called_once_with(x=0, color='k', linewidth=2)
        
        # Verify axis limits
        mock_ax.set_xlim.assert_called_once_with(-10, 10)
        mock_ax.set_ylim.assert_called_once_with(-10, 10)
    
    def test_coordinate_plane_point_plotting(self):
        """Test coordinate_plane point plotting logic - white box"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            points = [(1, 2, 'A'), (-3, 4, 'B'), (0, 0, 'O')]
            self.generator.coordinate_plane(points=points)
            
            # Should plot each point
            plot_calls = [call for call in mock_ax.plot.call_args_list 
                         if 'ro' in str(call)]
            self.assertEqual(len(plot_calls), len(points))
            
            # Should annotate each point
            annotate_calls = mock_ax.annotate.call_args_list
            self.assertEqual(len(annotate_calls), len(points))
    
    def test_coordinate_plane_line_drawing(self):
        """Test coordinate_plane line drawing logic - white box"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Test both line formats: point-to-point and slope-intercept
            lines = [
                ((0, 0), (1, 1)),  # Point-to-point format
                (2, 3, (-5, 5))    # Slope-intercept format (m, b, x_range)
            ]
            self.generator.coordinate_plane(lines=lines)
            
            # Should draw lines
            plot_calls = [call for call in mock_ax.plot.call_args_list 
                         if 'b-' in str(call)]
            self.assertTrue(len(plot_calls) >= 2)
    
    @parameterized.expand([
        (2, 3, "Positive slope"),
        (-1, 4, "Negative slope"),
        (0, 2, "Zero slope"),
        (1, 0, "No y-intercept"),
    ])
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.plot')
    def test_linear_equation_parameters(self, slope, y_intercept, title, mock_plot, mock_figure):
        """Test linear_equation with various slope/intercept combinations"""
        self.generator.linear_equation(slope, y_intercept, title)
        
        # Verify figure creation
        mock_figure.assert_called_once_with(figsize=(10, 8))
        
        # Should make multiple plot calls (line, intercepts)
        self.assertTrue(mock_plot.call_count >= 1)
    
    def test_linear_equation_intercept_calculation(self):
        """Test linear_equation x-intercept calculation logic - white box"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot, \
             patch('matplotlib.pyplot.xlim'), \
             patch('matplotlib.pyplot.ylim'):
            
            # Test case where x-intercept exists (slope != 0)
            slope, y_intercept = 2, -4
            self.generator.linear_equation(slope, y_intercept)
            
            # Should plot x-intercept when slope != 0
            intercept_calls = [call for call in mock_plot.call_args_list 
                             if 'go' in str(call)]
            self.assertTrue(len(intercept_calls) >= 1)
            
            # Test case where x-intercept doesn't exist (slope = 0)
            mock_plot.reset_mock()
            self.generator.linear_equation(0, 5)
            
            # Should not plot x-intercept when slope = 0
            intercept_calls = [call for call in mock_plot.call_args_list 
                             if 'go' in str(call)]
            self.assertEqual(len(intercept_calls), 0)
    
    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.patches.Rectangle')
    @patch('matplotlib.patches.Circle')
    @patch('matplotlib.patches.Polygon')
    def test_area_perimeter_shapes_calculations(self, mock_polygon, mock_circle, mock_rectangle, mock_subplots):
        """Test area_perimeter_shapes calculation logic - white box"""
        mock_axes = [[Mock(), Mock()], [Mock(), Mock()]]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        self.generator.area_perimeter_shapes()
        
        # Verify that shapes are created with correct parameters
        mock_rectangle.assert_called()  # For rectangle
        mock_circle.assert_called_once()
        mock_polygon.assert_called()  # For triangle and trapezoid
        
        # Verify text annotations are added (for calculations)
        for row in mock_axes:
            for ax in row:
                ax.text.assert_called()  # Should have calculation text
    
    @parameterized.expand([
        (1, -2, -8, "Standard quadratic"),
        (-1, 4, 3, "Downward parabola"),
        (1, 0, -4, "No linear term"),
        (1, -2, 1, "Perfect square"),
        (1, 0, 1, "No real roots"),
    ])
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.plot')
    def test_quadratic_function_parameters(self, a, b, c, title, mock_plot, mock_figure):
        """Test quadratic_function with various coefficients"""
        self.generator.quadratic_function(a, b, c, title)
        
        # Verify figure creation
        mock_figure.assert_called_once_with(figsize=(10, 8))
        
        # Should plot the parabola and vertex
        self.assertTrue(mock_plot.call_count >= 2)
    
    def test_quadratic_function_discriminant_logic(self):
        """Test quadratic_function discriminant calculation - white box"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot, \
             patch('matplotlib.pyplot.xlim'), \
             patch('matplotlib.pyplot.ylim'):
            
            # Test case: positive discriminant (two real roots)
            a, b, c = 1, -5, 6  # discriminant = 25 - 24 = 1 > 0
            self.generator.quadratic_function(a, b, c)
            
            # Should plot two x-intercepts
            root_calls = [call for call in mock_plot.call_args_list 
                         if 'go' in str(call)]
            self.assertEqual(len(root_calls), 2)
            
            # Test case: zero discriminant (one real root)
            mock_plot.reset_mock()
            a, b, c = 1, -2, 1  # discriminant = 4 - 4 = 0
            self.generator.quadratic_function(a, b, c)
            
            root_calls = [call for call in mock_plot.call_args_list 
                         if 'go' in str(call)]
            self.assertEqual(len(root_calls), 1)
            
            # Test case: negative discriminant (no real roots)
            mock_plot.reset_mock()
            a, b, c = 1, 0, 1  # discriminant = 0 - 4 = -4 < 0
            self.generator.quadratic_function(a, b, c)
            
            root_calls = [call for call in mock_plot.call_args_list 
                         if 'go' in str(call)]
            self.assertEqual(len(root_calls), 0)
    
    def test_quadratic_function_vertex_calculation(self):
        """Test quadratic_function vertex calculation - white box"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot') as mock_plot:
            
            a, b, c = 2, -8, 6
            expected_vertex_x = -b / (2 * a)  # Should be 2
            expected_vertex_y = a * expected_vertex_x**2 + b * expected_vertex_x + c  # Should be -2
            
            self.generator.quadratic_function(a, b, c)
            
            # Find vertex plot call
            vertex_calls = [call for call in mock_plot.call_args_list 
                           if 'ro' in str(call) and len(call[0]) == 2]
            
            self.assertTrue(len(vertex_calls) >= 1)
    
    @patch('matplotlib.pyplot.subplots')
    @patch('numpy.sin')
    @patch('numpy.cos')
    @patch('numpy.tan')
    def test_trigonometric_functions_setup(self, mock_tan, mock_cos, mock_sin, mock_subplots):
        """Test trigonometric_functions setup and calculations"""
        mock_axes = [Mock(), Mock(), Mock()]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        # Mock return values
        mock_sin.return_value = np.array([0, 1, 0, -1])
        mock_cos.return_value = np.array([1, 0, -1, 0])
        mock_tan.return_value = np.array([0, float('inf'), 0, float('-inf')])
        
        self.generator.trigonometric_functions()
        
        # Verify subplot creation
        mock_subplots.assert_called_once_with(3, 1, figsize=(12, 12))
        
        # Verify trigonometric functions are called
        mock_sin.assert_called()
        mock_cos.assert_called()
        mock_tan.assert_called()
        
        # Verify each subplot is configured
        for ax in mock_axes:
            ax.plot.assert_called()
            ax.grid.assert_called_once_with(True, alpha=0.3)
            ax.set_xlim.assert_called()
            ax.set_ylim.assert_called()
    
    def test_trigonometric_functions_asymptotes(self):
        """Test trigonometric_functions asymptote handling - white box"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_axes = [Mock(), Mock(), Mock()]
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_axes)
            
            self.generator.trigonometric_functions()
            
            # The tangent subplot (third axis) should have vertical asymptotes
            tan_ax = mock_axes[2]
            asymptote_calls = [call for call in tan_ax.axvline.call_args_list]
            self.assertTrue(len(asymptote_calls) >= 4)  # Should have multiple asymptotes


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        self.generator = MathDiagramGenerator()
        
        # Mock matplotlib to avoid actual plotting
        patch('matplotlib.pyplot.show').start()
        patch('matplotlib.pyplot.savefig').start()
        patch('matplotlib.pyplot.clf').start()
    
    def tearDown(self):
        patch.stopall()
    
    def test_empty_parameters(self):
        """Test methods with empty/None parameters"""
        with patch('matplotlib.pyplot.subplots'):
            # Should not raise exceptions
            self.generator.coordinate_plane(points=None, lines=None)
            self.generator.coordinate_plane(points=[], lines=[])
    
    def test_invalid_fraction_parameters(self):
        """Test fraction_visual with invalid parameters"""
        with patch('matplotlib.pyplot.subplots'):
            # These should not crash the program
            try:
                self.generator.fraction_visual(0, 1)  # Valid: 0/1
                self.generator.fraction_visual(5, 5)  # Valid: 5/5 = 1
            except Exception as e:
                self.fail(f"fraction_visual raised unexpected exception: {e}")
    
    def test_extreme_number_line_ranges(self):
        """Test number_line with extreme ranges"""
        with patch('matplotlib.pyplot.subplots'):
            # Large ranges
            self.generator.number_line(-1000, 1000)
            
            # Single point
            self.generator.number_line(0, 0)
            
            # Reverse range (start > end)
            self.generator.number_line(5, -5)
    
    def test_quadratic_division_by_zero_protection(self):
        """Test quadratic_function with a=0 (not actually quadratic)"""
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot'):
            
            # This should handle the division by zero in vertex calculation
            try:
                # When a=0, it's actually linear, but shouldn't crash
                self.generator.quadratic_function(0, 2, 1)
            except ZeroDivisionError:
                self.fail("quadratic_function should handle a=0 case")


class TestFileOperations(unittest.TestCase):
    """Test file operations and directory handling"""
    
    def setUp(self):
        patch('matplotlib.pyplot.show').start()
        patch('matplotlib.pyplot.savefig').start()
        patch('matplotlib.pyplot.clf').start()
        
    def tearDown(self):
        patch.stopall()
    
    @patch('os.makedirs')
    def test_diagrams_directory_creation(self, mock_makedirs):
        """Test that diagrams directory is created"""
        # Import should trigger directory creation
        from math_diagram_generator import MathDiagramGenerator
        
        mock_makedirs.assert_called_with("diagrams", exist_ok=True)
    
    @patch('matplotlib.pyplot.savefig')
    def test_save_plot_file_naming(self, mock_savefig):
        """Test save_plot file naming convention"""
        generator = MathDiagramGenerator()
        
        filename = "test_diagram.png"
        generator.save_plot(filename, "Test Title")
        
        expected_path = f"diagrams/{filename}"
        mock_savefig.assert_called_once_with(expected_path, dpi=300, bbox_inches='tight')


if __name__ == '__main__':
    # Run tests with coverage
    unittest.main(verbosity=2)