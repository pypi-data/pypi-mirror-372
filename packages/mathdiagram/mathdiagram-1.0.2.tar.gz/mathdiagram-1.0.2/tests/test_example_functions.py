"""
Tests for Example Functions in Grade-Level Modules

This module tests the helper functions in examples_grades_4_6.py, 
examples_grades_7_8.py, and examples_grades_9_10.py that weren't 
covered in other test files.
"""

import unittest
import pytest
import sys
import os
from unittest.mock import patch, Mock, MagicMock
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGrade4To6HelperFunctions(unittest.TestCase):
    """Test helper functions in examples_grades_4_6.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock matplotlib to avoid actual plotting
        self.show_mock = patch('matplotlib.pyplot.show').start()
        self.savefig_mock = patch('matplotlib.pyplot.savefig').start()
        self.clf_mock = patch('matplotlib.pyplot.clf').start()
    
    def tearDown(self):
        """Clean up after each test"""
        patch.stopall()
    
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.bar')
    def test_create_simple_bar_chart(self, mock_bar, mock_figure):
        """Test simple bar chart creation"""
        from examples_grades_4_6 import create_simple_bar_chart
        
        try:
            create_simple_bar_chart()
            
            # Verify figure and bar chart were created
            mock_figure.assert_called_once_with(figsize=(10, 6))
            mock_bar.assert_called_once()
            
            # Verify save was called
            self.savefig_mock.assert_called_once()
            
        except Exception as e:
            self.fail(f"create_simple_bar_chart failed: {e}")
    
    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.pyplot.Circle')
    def test_create_clock_diagram(self, mock_circle, mock_subplots):
        """Test clock diagram creation"""
        from examples_grades_4_6 import create_clock_diagram
        
        # Mock subplot return values
        mock_axes = [Mock(), Mock(), Mock()]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        try:
            create_clock_diagram()
            
            # Should create 3 clock faces
            mock_subplots.assert_called_once_with(1, 3, figsize=(15, 5))
            
            # Each axis should be configured
            for ax in mock_axes:
                ax.set_xlim.assert_called()
                ax.set_ylim.assert_called()
                ax.set_title.assert_called()
                ax.axis.assert_called_with('off')
            
        except Exception as e:
            self.fail(f"create_clock_diagram failed: {e}")
    
    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.pyplot.Circle')
    def test_create_money_diagram(self, mock_circle, mock_subplots):
        """Test money counting diagram creation"""
        from examples_grades_4_6 import create_money_diagram
        
        mock_ax = Mock()
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        try:
            create_money_diagram()
            
            mock_subplots.assert_called_once_with(1, 1, figsize=(12, 6))
            mock_ax.set_xlim.assert_called()
            mock_ax.set_ylim.assert_called()
            mock_ax.set_title.assert_called()
            mock_ax.axis.assert_called_with('off')
            
        except Exception as e:
            self.fail(f"create_money_diagram failed: {e}")


class TestGrade7To8HelperFunctions(unittest.TestCase):
    """Test helper functions in examples_grades_7_8.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.show_mock = patch('matplotlib.pyplot.show').start()
        self.savefig_mock = patch('matplotlib.pyplot.savefig').start()
        self.clf_mock = patch('matplotlib.pyplot.clf').start()
    
    def tearDown(self):
        """Clean up after each test"""
        patch.stopall()
    
    @patch('matplotlib.pyplot.subplots')
    def test_create_slope_demonstration(self, mock_subplots):
        """Test slope demonstration creation"""
        from examples_grades_7_8 import create_slope_demonstration
        
        # Mock 2x2 subplot grid
        mock_axes = [[Mock(), Mock()], [Mock(), Mock()]]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        try:
            create_slope_demonstration()
            
            mock_subplots.assert_called_once_with(2, 2, figsize=(12, 10))
            
            # Each subplot should be configured
            for row in mock_axes:
                for ax in row:
                    ax.grid.assert_called()
                    ax.set_xlim.assert_called()
                    ax.set_ylim.assert_called()
                    ax.set_title.assert_called()
                    ax.legend.assert_called()
            
        except Exception as e:
            self.fail(f"create_slope_demonstration failed: {e}")
    
    @patch('matplotlib.pyplot.subplots')
    def test_create_systems_of_equations(self, mock_subplots):
        """Test systems of equations visualization"""
        from examples_grades_7_8 import create_systems_of_equations
        
        mock_axes = [Mock(), Mock(), Mock()]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        try:
            create_systems_of_equations()
            
            mock_subplots.assert_called_once_with(1, 3, figsize=(18, 6))
            
            # Each axis should show different system types
            for ax in mock_axes:
                ax.plot.assert_called()  # Lines plotted
                ax.grid.assert_called()
                ax.set_title.assert_called()
                ax.legend.assert_called()
            
        except Exception as e:
            self.fail(f"create_systems_of_equations failed: {e}")
    
    @patch('matplotlib.pyplot.subplots')
    def test_create_proportional_relationships(self, mock_subplots):
        """Test proportional relationships demonstration"""
        from examples_grades_7_8 import create_proportional_relationships
        
        mock_axes = [Mock(), Mock()]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        try:
            create_proportional_relationships()
            
            mock_subplots.assert_called_once_with(1, 2, figsize=(14, 6))
            
            # Both axes should show proportional vs non-proportional
            for ax in mock_axes:
                ax.plot.assert_called()
                ax.scatter.assert_called()
                ax.grid.assert_called()
                ax.set_title.assert_called()
                ax.legend.assert_called()
            
        except Exception as e:
            self.fail(f"create_proportional_relationships failed: {e}")
    
    @patch('matplotlib.pyplot.subplots')
    @patch('numpy.percentile')
    def test_create_statistics_plots(self, mock_percentile, mock_subplots):
        """Test statistics plots creation"""
        from examples_grades_7_8 import create_statistics_plots
        
        # Mock 2x2 subplot grid
        mock_axes = [[Mock(), Mock()], [Mock(), Mock()]]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        # Mock percentile calculations
        mock_percentile.side_effect = lambda data, q: q * 0.01 * max(data)
        
        try:
            create_statistics_plots()
            
            mock_subplots.assert_called_once_with(2, 2, figsize=(14, 10))
            
            # Verify each subplot type
            box_ax = mock_axes[0][0]  # Box plot
            hist_ax = mock_axes[0][1]  # Histogram
            scatter_ax = mock_axes[1][0]  # Scatter plot
            bar_ax = mock_axes[1][1]  # Bar chart
            
            # Box plot should have boxplot call
            box_ax.boxplot.assert_called()
            
            # Histogram should have hist call
            hist_ax.hist.assert_called()
            
            # Scatter plot should have scatter call
            scatter_ax.scatter.assert_called()
            
            # Bar chart should have bar call  
            bar_ax.bar.assert_called()
            
        except Exception as e:
            self.fail(f"create_statistics_plots failed: {e}")


class TestGrade9To10HelperFunctions(unittest.TestCase):
    """Test helper functions in examples_grades_9_10.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.show_mock = patch('matplotlib.pyplot.show').start()
        self.savefig_mock = patch('matplotlib.pyplot.savefig').start()
        self.clf_mock = patch('matplotlib.pyplot.clf').start()
    
    def tearDown(self):
        """Clean up after each test"""
        patch.stopall()
    
    @patch('matplotlib.pyplot.subplots')
    def test_create_exponential_logarithmic(self, mock_subplots):
        """Test exponential and logarithmic functions creation"""
        from examples_grades_9_10 import create_exponential_logarithmic
        
        # Mock 2x2 subplot grid
        mock_axes = [[Mock(), Mock()], [Mock(), Mock()]]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        try:
            create_exponential_logarithmic()
            
            mock_subplots.assert_called_once_with(2, 2, figsize=(14, 12))
            
            # Each subplot should show different function types
            for row in mock_axes:
                for ax in row:
                    ax.plot.assert_called()  # Functions plotted
                    ax.grid.assert_called()
                    ax.set_title.assert_called()
                    ax.legend.assert_called()
            
        except Exception as e:
            self.fail(f"create_exponential_logarithmic failed: {e}")
    
    @patch('matplotlib.pyplot.subplots')
    def test_create_function_transformations(self, mock_subplots):
        """Test function transformations demonstration"""
        from examples_grades_9_10 import create_function_transformations
        
        mock_axes = [[Mock(), Mock()], [Mock(), Mock()]]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        try:
            create_function_transformations()
            
            mock_subplots.assert_called_once_with(2, 2, figsize=(14, 12))
            
            # Each transformation type should be shown
            for row in mock_axes:
                for ax in row:
                    ax.plot.assert_called()
                    ax.grid.assert_called()
                    ax.set_title.assert_called()
                    ax.legend.assert_called()
            
        except Exception as e:
            self.fail(f"create_function_transformations failed: {e}")
    
    @patch('matplotlib.pyplot.subplots')
    def test_create_polynomial_functions(self, mock_subplots):
        """Test polynomial functions demonstration"""
        from examples_grades_9_10 import create_polynomial_functions
        
        mock_axes = [[Mock(), Mock()], [Mock(), Mock()]]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        try:
            create_polynomial_functions()
            
            mock_subplots.assert_called_once_with(2, 2, figsize=(14, 12))
            
            # Each polynomial type should be plotted
            for row in mock_axes:
                for ax in row:
                    ax.plot.assert_called()
                    ax.grid.assert_called()
                    ax.set_title.assert_called()
                    ax.legend.assert_called()
            
        except Exception as e:
            self.fail(f"create_polynomial_functions failed: {e}")
    
    @patch('matplotlib.pyplot.subplots')
    def test_create_rational_functions(self, mock_subplots):
        """Test rational functions with asymptotes"""
        from examples_grades_9_10 import create_rational_functions
        
        mock_axes = [[Mock(), Mock()], [Mock(), Mock()]]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        try:
            create_rational_functions()
            
            mock_subplots.assert_called_once_with(2, 2, figsize=(14, 12))
            
            # Each rational function should show asymptotes
            for row in mock_axes:
                for ax in row:
                    ax.plot.assert_called()  # Function curves
                    ax.axhline.assert_called()  # Horizontal asymptotes
                    ax.grid.assert_called()
                    ax.set_title.assert_called()
                    ax.legend.assert_called()
            
        except Exception as e:
            self.fail(f"create_rational_functions failed: {e}")
    
    @patch('matplotlib.pyplot.subplots')
    def test_create_unit_circle(self, mock_subplots):
        """Test unit circle creation with special angles"""
        from examples_grades_9_10 import create_unit_circle
        
        mock_ax = Mock()
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        try:
            create_unit_circle()
            
            mock_subplots.assert_called_once_with(1, 1, figsize=(12, 12))
            
            # Unit circle should be plotted with points and labels
            mock_ax.plot.assert_called()  # Circle and radial lines
            mock_ax.annotate.assert_called()  # Angle labels
            mock_ax.text.assert_called()  # Quadrant labels
            mock_ax.set_aspect.assert_called_with('equal')
            
        except Exception as e:
            self.fail(f"create_unit_circle failed: {e}")
    
    @patch('matplotlib.pyplot.subplots') 
    def test_create_normal_distribution(self, mock_subplots):
        """Test normal distribution demonstrations"""
        from examples_grades_9_10 import create_normal_distribution
        
        mock_axes = [[Mock(), Mock()], [Mock(), Mock()]]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        try:
            create_normal_distribution()
            
            mock_subplots.assert_called_once_with(2, 2, figsize=(14, 10))
            
            # Each subplot shows different distribution aspects
            for row in mock_axes:
                for ax in row:
                    ax.plot.assert_called()  # Distribution curves
                    ax.set_title.assert_called()
                    ax.legend.assert_called()
                    ax.grid.assert_called()
            
        except Exception as e:
            self.fail(f"create_normal_distribution failed: {e}")
    
    @patch('matplotlib.pyplot.subplots')
    @patch('numpy.cumsum')
    def test_create_sequences_series(self, mock_cumsum, mock_subplots):
        """Test sequences and series demonstration"""
        from examples_grades_9_10 import create_sequences_series
        
        mock_axes = [[Mock(), Mock()], [Mock(), Mock()]]
        mock_fig = Mock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        
        # Mock cumulative sum for series
        mock_cumsum.return_value = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55]
        
        try:
            create_sequences_series()
            
            mock_subplots.assert_called_once_with(2, 2, figsize=(14, 12))
            
            # Should show both sequences and their partial sums
            seq_ax1 = mock_axes[0][0]  # Arithmetic sequence
            seq_ax2 = mock_axes[0][1]  # Geometric sequence
            series_ax1 = mock_axes[1][0]  # Arithmetic series
            series_ax2 = mock_axes[1][1]  # Geometric series
            
            # Sequences should have scatter plots
            seq_ax1.scatter.assert_called()
            seq_ax2.scatter.assert_called()
            
            # Series should have bar charts and line plots
            series_ax1.bar.assert_called()
            series_ax1.plot.assert_called()
            series_ax2.bar.assert_called()
            series_ax2.plot.assert_called()
            
        except Exception as e:
            self.fail(f"create_sequences_series failed: {e}")


class TestMainExampleFunctions(unittest.TestCase):
    """Test main example functions that orchestrate multiple diagrams"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.show_mock = patch('matplotlib.pyplot.show').start()
        self.savefig_mock = patch('matplotlib.pyplot.savefig').start()
        
    def tearDown(self):
        """Clean up after each test"""
        patch.stopall()
    
    @patch('examples_grades_4_6.create_simple_bar_chart')
    @patch('examples_grades_4_6.create_clock_diagram')
    @patch('examples_grades_4_6.create_money_diagram')
    def test_create_grade_4_6_examples(self, mock_money, mock_clock, mock_bar):
        """Test grade 4-6 main example function"""
        from examples_grades_4_6 import create_grade_4_6_examples
        
        try:
            # Mock the MathDiagramGenerator methods
            with patch('examples_grades_4_6.MathDiagramGenerator') as mock_gen_class:
                mock_generator = Mock()
                mock_gen_class.return_value = mock_generator
                
                create_grade_4_6_examples()
                
                # Verify generator methods were called
                mock_generator.number_line.assert_called()
                mock_generator.basic_shapes.assert_called()
                mock_generator.fraction_visual.assert_called()
                
                # Verify helper functions were called
                mock_bar.assert_called_once()
                mock_clock.assert_called_once()
                mock_money.assert_called_once()
                
        except Exception as e:
            self.fail(f"create_grade_4_6_examples failed: {e}")
    
    @patch('examples_grades_7_8.create_slope_demonstration')
    @patch('examples_grades_7_8.create_systems_of_equations')
    @patch('examples_grades_7_8.create_proportional_relationships')
    @patch('examples_grades_7_8.create_statistics_plots')
    def test_create_grade_7_8_examples(self, mock_stats, mock_prop, mock_systems, mock_slope):
        """Test grade 7-8 main example function"""
        from examples_grades_7_8 import create_grade_7_8_examples
        
        try:
            with patch('examples_grades_7_8.MathDiagramGenerator') as mock_gen_class:
                mock_generator = Mock()
                mock_gen_class.return_value = mock_generator
                
                create_grade_7_8_examples()
                
                # Verify generator methods were called
                mock_generator.coordinate_plane.assert_called()
                mock_generator.linear_equation.assert_called()
                mock_generator.area_perimeter_shapes.assert_called()
                
                # Verify helper functions were called
                mock_slope.assert_called_once()
                mock_systems.assert_called_once()
                mock_prop.assert_called_once()
                mock_stats.assert_called_once()
                
        except Exception as e:
            self.fail(f"create_grade_7_8_examples failed: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)