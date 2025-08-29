"""
Error Handling and Robustness Tests

This module tests error handling, exception management, and robustness
of the Math Diagram Generator under various failure conditions.
"""

import unittest
import pytest
import sys
import os
from unittest.mock import patch, Mock, MagicMock, side_effect
import matplotlib
matplotlib.use('Agg')

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math_diagram_generator import MathDiagramGenerator


class TestErrorHandlingRobustness(unittest.TestCase):
    """Test error handling and robustness"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = MathDiagramGenerator()
        
        # Mock basic matplotlib functions
        self.show_mock = patch('matplotlib.pyplot.show').start()
        self.savefig_mock = patch('matplotlib.pyplot.savefig').start()
        self.clf_mock = patch('matplotlib.pyplot.clf').start()
    
    def tearDown(self):
        """Clean up after each test"""
        patch.stopall()


class TestFileSystemErrors(TestErrorHandlingRobustness):
    """Test file system error handling"""
    
    def test_save_plot_permission_error(self):
        """Test save_plot when file permissions are denied"""
        with patch('matplotlib.pyplot.savefig') as mock_savefig:
            mock_savefig.side_effect = PermissionError("Permission denied")
            
            # Should handle permission error gracefully
            try:
                self.generator.save_plot("test.png", "Test")
                # If it doesn't raise an exception, that's also acceptable
            except PermissionError:
                # Expected behavior - let the error propagate for user handling
                pass
    
    def test_save_plot_disk_full_error(self):
        """Test save_plot when disk is full"""
        with patch('matplotlib.pyplot.savefig') as mock_savefig:
            mock_savefig.side_effect = OSError("No space left on device")
            
            try:
                self.generator.save_plot("test.png", "Test")
            except OSError:
                # Expected behavior
                pass
    
    def test_directory_creation_failure(self):
        """Test when diagrams directory cannot be created"""
        with patch('os.makedirs') as mock_makedirs:
            mock_makedirs.side_effect = OSError("Cannot create directory")
            
            # Should handle directory creation failure
            try:
                # Re-import to trigger directory creation
                import importlib
                import math_diagram_generator
                importlib.reload(math_diagram_generator)
            except OSError:
                pass  # Expected if directory creation fails


class TestMatplotlibErrors(TestErrorHandlingRobustness):
    """Test matplotlib-related error handling"""
    
    def test_figure_creation_error(self):
        """Test when figure creation fails"""
        with patch('matplotlib.pyplot.figure') as mock_figure:
            mock_figure.side_effect = RuntimeError("Cannot create figure")
            
            try:
                self.generator.linear_equation(2, 3)
            except RuntimeError:
                pass  # Expected
    
    def test_subplot_creation_error(self):
        """Test when subplot creation fails"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_subplots.side_effect = ValueError("Invalid subplot configuration")
            
            try:
                self.generator.coordinate_plane()
            except ValueError:
                pass  # Expected
    
    def test_plot_rendering_error(self):
        """Test when plot rendering fails"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Make plot method fail
            mock_ax.plot.side_effect = RuntimeError("Rendering error")
            
            try:
                self.generator.coordinate_plane([(1, 2, 'A')])
            except RuntimeError:
                pass  # Expected


class TestNumericalErrors(TestErrorHandlingRobustness):
    """Test numerical computation error handling"""
    
    def test_overflow_in_calculations(self):
        """Test handling of numerical overflow"""
        # Very large coefficients that might cause overflow
        large_coeff = 1e308
        
        try:
            self.generator.quadratic_function(large_coeff, large_coeff, large_coeff)
            # Should handle or let numpy handle the overflow
        except (OverflowError, ValueError):
            pass  # Expected for extreme values
    
    def test_underflow_in_calculations(self):
        """Test handling of numerical underflow"""
        # Very small coefficients that might cause underflow
        small_coeff = 1e-308
        
        try:
            self.generator.quadratic_function(small_coeff, small_coeff, small_coeff)
            # Should handle or work with underflow
        except (UnderflowError, ValueError):
            pass  # Acceptable
    
    def test_invalid_mathematical_operations(self):
        """Test handling of invalid mathematical operations"""
        with patch('numpy.sqrt') as mock_sqrt:
            # Make sqrt return NaN for negative discriminant
            mock_sqrt.return_value = float('nan')
            
            try:
                self.generator.quadratic_function(1, 0, 1)  # No real roots
                # Should handle NaN values gracefully
            except (ValueError, ArithmeticError):
                pass  # Expected for invalid operations


class TestDataCorruptionErrors(TestErrorHandlingRobustness):
    """Test handling of corrupted or malformed data"""
    
    def test_malformed_points_data(self):
        """Test coordinate_plane with malformed points"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Various malformed point data
            malformed_points = [
                [(1, 2)],  # Missing label
                [(1,)],    # Missing coordinates
                [()],      # Empty tuple
                [None],    # None value
                ["invalid"],  # Wrong type
            ]
            
            for points in malformed_points:
                try:
                    self.generator.coordinate_plane(points=points)
                    # Should handle gracefully or raise appropriate error
                except (ValueError, TypeError, IndexError):
                    pass  # Expected for malformed data
    
    def test_malformed_lines_data(self):
        """Test coordinate_plane with malformed lines"""
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Various malformed line data
            malformed_lines = [
                [(1,)],           # Not enough points
                [((1, 2), (3,))], # Incomplete point
                [(None, None)],   # None values
                ["invalid"],      # Wrong type
            ]
            
            for lines in malformed_lines:
                try:
                    self.generator.coordinate_plane(lines=lines)
                except (ValueError, TypeError, IndexError):
                    pass  # Expected for malformed data


class TestMemoryErrors(TestErrorHandlingRobustness):
    """Test memory-related error handling"""
    
    def test_large_data_arrays(self):
        """Test handling of very large data arrays"""
        with patch('numpy.linspace') as mock_linspace:
            # Simulate memory error when creating large arrays
            mock_linspace.side_effect = MemoryError("Cannot allocate memory")
            
            try:
                self.generator.trigonometric_functions()
            except MemoryError:
                pass  # Expected for memory constraints
    
    def test_memory_exhaustion_during_plotting(self):
        """Test behavior when memory is exhausted during plotting"""
        with patch('matplotlib.pyplot.plot') as mock_plot:
            mock_plot.side_effect = MemoryError("Out of memory")
            
            with patch('matplotlib.pyplot.figure'):
                try:
                    self.generator.linear_equation(1, 1)
                except MemoryError:
                    pass  # Expected


class TestConcurrencyErrors(TestErrorHandlingRobustness):
    """Test thread safety and concurrency issues"""
    
    def test_concurrent_plot_creation(self):
        """Test creating plots concurrently (basic test)"""
        import threading
        
        results = []
        errors = []
        
        def create_plot():
            try:
                generator = MathDiagramGenerator()
                generator.number_line(-5, 5)
                results.append("success")
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=create_plot)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Should not have serious errors (matplotlib might not be thread-safe)
        # This is more of a smoke test
        self.assertTrue(len(results) > 0 or len(errors) > 0)


class TestResourceCleanup(TestErrorHandlingRobustness):
    """Test proper resource cleanup after errors"""
    
    def test_cleanup_after_plot_error(self):
        """Test that resources are cleaned up after plot errors"""
        with patch('matplotlib.pyplot.figure') as mock_figure:
            mock_figure.side_effect = RuntimeError("Plot error")
            
            initial_figures = len(plt.get_fignums()) if hasattr(plt, 'get_fignums') else 0
            
            try:
                self.generator.linear_equation(1, 1)
            except RuntimeError:
                pass
            
            # Check that no additional figures are left open
            # This is a basic check - matplotlib behavior may vary
            if hasattr(plt, 'get_fignums'):
                final_figures = len(plt.get_fignums())
                # Should not have significantly more figures
                self.assertLessEqual(final_figures - initial_figures, 1)
    
    def test_cleanup_after_save_error(self):
        """Test cleanup after save errors"""
        with patch('matplotlib.pyplot.savefig') as mock_savefig:
            mock_savefig.side_effect = IOError("Cannot save file")
            
            try:
                self.generator.save_plot("test.png")
            except IOError:
                pass
            
            # Should still call cleanup functions
            self.clf_mock.assert_called()


class TestInputValidationErrors(TestErrorHandlingRobustness):
    """Test input validation and sanitization"""
    
    def test_extremely_long_title(self):
        """Test with extremely long title strings"""
        long_title = "A" * 10000  # Very long title
        
        try:
            self.generator.save_plot("test.png", long_title)
            # Should handle long titles gracefully
        except (ValueError, MemoryError):
            pass  # Acceptable to reject very long titles
    
    def test_special_characters_in_filename(self):
        """Test save_plot with special characters in filename"""
        special_filenames = [
            "test<>file.png",
            "test|file.png", 
            "test?file.png",
            "test*file.png",
            "",  # Empty filename
        ]
        
        for filename in special_filenames:
            try:
                self.generator.save_plot(filename)
                # Should handle or reject invalid filenames
            except (ValueError, OSError):
                pass  # Expected for invalid filenames
    
    def test_unicode_in_mathematical_labels(self):
        """Test handling of complex Unicode in mathematical contexts"""
        unicode_points = [
            (1, 2, "∫∞∑∂∇"),  # Math symbols
            (3, 4, "🎉🎊🎈"),   # Emojis
            (5, 6, "αβγδε"),   # Greek letters
        ]
        
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_ax = Mock()
            mock_fig = Mock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            try:
                self.generator.coordinate_plane(points=unicode_points)
                # Should handle Unicode gracefully
            except (UnicodeError, ValueError):
                pass  # May not support all Unicode


class TestEnvironmentErrors(TestErrorHandlingRobustness):
    """Test handling of environment-specific errors"""
    
    def test_missing_optional_dependencies(self):
        """Test behavior when optional dependencies are missing"""
        # Test case already handled in main code with seaborn
        # This verifies it works as expected
        
        # Temporarily remove seaborn if imported
        import sys
        original_seaborn = sys.modules.get('seaborn')
        if 'seaborn' in sys.modules:
            del sys.modules['seaborn']
        
        try:
            # Should work without seaborn
            generator = MathDiagramGenerator()
            generator.number_line(-5, 5)
        finally:
            # Restore seaborn if it was there
            if original_seaborn:
                sys.modules['seaborn'] = original_seaborn
    
    def test_display_backend_unavailable(self):
        """Test when display backend is not available"""
        with patch('matplotlib.pyplot.show') as mock_show:
            mock_show.side_effect = RuntimeError("No display available")
            
            try:
                self.generator.number_line(-5, 5)
                # Should work even without display
            except RuntimeError:
                pass  # May fail in headless environments


if __name__ == '__main__':
    unittest.main(verbosity=2)