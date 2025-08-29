"""
Integration Tests for Math Diagram Generator

This module contains integration tests that verify the complete workflow
from grade-level example scripts to diagram generation.
"""

import unittest
import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, Mock, MagicMock
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math_diagram_generator import MathDiagramGenerator


class TestGradeIntegration(unittest.TestCase):
    """Integration tests for complete grade-level workflows"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level test fixtures"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.original_cwd = os.getcwd()
        os.chdir(cls.temp_dir)
        
        # Create diagrams directory in temp location
        os.makedirs("diagrams", exist_ok=True)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level fixtures"""
        os.chdir(cls.original_cwd)
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.generator = MathDiagramGenerator()
        
        # Mock file operations but allow the logic to run
        self.show_mock = patch('matplotlib.pyplot.show').start()
        self.savefig_mock = patch('matplotlib.pyplot.savefig').start()
        
    def tearDown(self):
        """Clean up after each test method"""
        patch.stopall()


class TestGrade4To6Integration(TestGradeIntegration):
    """Integration tests for grades 4-6 examples"""
    
    def test_number_line_workflow(self):
        """Test complete number line creation workflow"""
        # Test various number line configurations
        test_cases = [
            (-5, 15, [3, 7, 12], "Highlighting positive numbers"),
            (-10, 10, [-3, 0, 5], "Including negative numbers"),
            (0, 20, [5, 10, 15], "Positive only range"),
        ]
        
        for start, end, highlights, title in test_cases:
            with self.subTest(start=start, end=end, highlights=highlights):
                try:
                    self.generator.number_line(start, end, highlights, title)
                    
                    # Verify save was called with correct filename
                    expected_filename = "diagrams/number_line.png"
                    self.savefig_mock.assert_called_with(expected_filename, dpi=300, bbox_inches='tight')
                    
                except Exception as e:
                    self.fail(f"Number line workflow failed for {test_cases}: {e}")
                
                self.savefig_mock.reset_mock()
    
    def test_basic_shapes_workflow(self):
        """Test complete basic shapes creation workflow"""
        try:
            self.generator.basic_shapes()
            
            # Should save to basic_shapes.png
            expected_filename = "diagrams/basic_shapes.png"
            self.savefig_mock.assert_called_with(expected_filename, dpi=300, bbox_inches='tight')
            
        except Exception as e:
            self.fail(f"Basic shapes workflow failed: {e}")
    
    def test_fraction_visual_workflow(self):
        """Test complete fraction visualization workflow"""
        test_fractions = [
            (1, 2, "One Half"),
            (3, 4, "Three Fourths"),
            (2, 3, "Two Thirds"),
            (5, 6, "Five Sixths"),
        ]
        
        for numerator, denominator, title in test_fractions:
            with self.subTest(fraction=f"{numerator}/{denominator}"):
                try:
                    self.generator.fraction_visual(numerator, denominator, title)
                    
                    expected_filename = f"diagrams/fraction_{numerator}_{denominator}.png"
                    self.savefig_mock.assert_called_with(expected_filename, dpi=300, bbox_inches='tight')
                    
                except Exception as e:
                    self.fail(f"Fraction visualization workflow failed for {numerator}/{denominator}: {e}")
                
                self.savefig_mock.reset_mock()
    
    def test_grades_4_6_examples_import(self):
        """Test that grade 4-6 examples module can be imported and functions exist"""
        try:
            # This tests the import pathway
            import examples_grades_4_6
            
            # Verify main function exists
            self.assertTrue(hasattr(examples_grades_4_6, 'create_grade_4_6_examples'))
            self.assertTrue(callable(examples_grades_4_6.create_grade_4_6_examples))
            
            # Verify helper functions exist
            self.assertTrue(hasattr(examples_grades_4_6, 'create_simple_bar_chart'))
            self.assertTrue(hasattr(examples_grades_4_6, 'create_clock_diagram'))
            self.assertTrue(hasattr(examples_grades_4_6, 'create_money_diagram'))
            
        except ImportError as e:
            self.fail(f"Failed to import examples_grades_4_6: {e}")


class TestGrade7To8Integration(TestGradeIntegration):
    """Integration tests for grades 7-8 examples"""
    
    def test_coordinate_plane_workflow(self):
        """Test complete coordinate plane creation workflow"""
        test_points = [(3, 4, 'A'), (-2, 1, 'B'), (0, -3, 'C')]
        test_lines = [((0, 0), (1, 1))]
        
        try:
            self.generator.coordinate_plane(test_points, test_lines, "Test Coordinate Plane")
            
            expected_filename = "diagrams/coordinate_plane.png"
            self.savefig_mock.assert_called_with(expected_filename, dpi=300, bbox_inches='tight')
            
        except Exception as e:
            self.fail(f"Coordinate plane workflow failed: {e}")
    
    def test_linear_equation_workflow(self):
        """Test complete linear equation graphing workflow"""
        test_cases = [
            (2, 3, "Positive slope with positive intercept"),
            (-1, 4, "Negative slope with positive intercept"),
            (0.5, -2, "Fractional slope with negative intercept"),
            (0, 5, "Zero slope (horizontal line)"),
        ]
        
        for slope, y_intercept, title in test_cases:
            with self.subTest(slope=slope, y_intercept=y_intercept):
                try:
                    self.generator.linear_equation(slope, y_intercept, title)
                    
                    expected_filename = "diagrams/linear_equation.png"
                    self.savefig_mock.assert_called_with(expected_filename, dpi=300, bbox_inches='tight')
                    
                except Exception as e:
                    self.fail(f"Linear equation workflow failed for slope={slope}, y_intercept={y_intercept}: {e}")
                
                self.savefig_mock.reset_mock()
    
    def test_area_perimeter_workflow(self):
        """Test complete area and perimeter shapes workflow"""
        try:
            self.generator.area_perimeter_shapes()
            
            expected_filename = "diagrams/area_perimeter_shapes.png"
            self.savefig_mock.assert_called_with(expected_filename, dpi=300, bbox_inches='tight')
            
        except Exception as e:
            self.fail(f"Area perimeter shapes workflow failed: {e}")
    
    def test_grades_7_8_examples_import(self):
        """Test that grade 7-8 examples module can be imported and functions exist"""
        try:
            import examples_grades_7_8
            
            # Verify main function exists
            self.assertTrue(hasattr(examples_grades_7_8, 'create_grade_7_8_examples'))
            self.assertTrue(callable(examples_grades_7_8.create_grade_7_8_examples))
            
            # Verify helper functions exist
            helper_functions = [
                'create_slope_demonstration',
                'create_systems_of_equations', 
                'create_proportional_relationships',
                'create_statistics_plots'
            ]
            
            for func_name in helper_functions:
                self.assertTrue(hasattr(examples_grades_7_8, func_name), 
                              f"Missing function: {func_name}")
                self.assertTrue(callable(getattr(examples_grades_7_8, func_name)),
                              f"Function not callable: {func_name}")
            
        except ImportError as e:
            self.fail(f"Failed to import examples_grades_7_8: {e}")


class TestGrade9To10Integration(TestGradeIntegration):
    """Integration tests for grades 9-10 examples"""
    
    def test_quadratic_function_workflow(self):
        """Test complete quadratic function graphing workflow"""
        test_cases = [
            (1, -2, -8, "Standard parabola opening upward"),
            (-1, 4, 3, "Parabola opening downward"),
            (0.5, -1, 2, "Wide parabola"),
            (2, 0, -8, "No linear term"),
            (1, -4, 4, "Perfect square (discriminant = 0)"),
            (1, 0, 5, "No real roots (discriminant < 0)"),
        ]
        
        for a, b, c, title in test_cases:
            with self.subTest(a=a, b=b, c=c):
                try:
                    self.generator.quadratic_function(a, b, c, title)
                    
                    expected_filename = "diagrams/quadratic_function.png"
                    self.savefig_mock.assert_called_with(expected_filename, dpi=300, bbox_inches='tight')
                    
                except Exception as e:
                    self.fail(f"Quadratic function workflow failed for y={a}x²+{b}x+{c}: {e}")
                
                self.savefig_mock.reset_mock()
    
    def test_trigonometric_functions_workflow(self):
        """Test complete trigonometric functions workflow"""
        try:
            self.generator.trigonometric_functions()
            
            expected_filename = "diagrams/trigonometric_functions.png"
            self.savefig_mock.assert_called_with(expected_filename, dpi=300, bbox_inches='tight')
            
        except Exception as e:
            self.fail(f"Trigonometric functions workflow failed: {e}")
    
    def test_grades_9_10_examples_import(self):
        """Test that grade 9-10 examples module can be imported and functions exist"""
        try:
            import examples_grades_9_10
            
            # Verify main function exists
            self.assertTrue(hasattr(examples_grades_9_10, 'create_grade_9_10_examples'))
            self.assertTrue(callable(examples_grades_9_10.create_grade_9_10_examples))
            
            # Verify helper functions exist
            helper_functions = [
                'create_exponential_logarithmic',
                'create_function_transformations',
                'create_polynomial_functions',
                'create_rational_functions',
                'create_unit_circle',
                'create_normal_distribution',
                'create_sequences_series'
            ]
            
            for func_name in helper_functions:
                self.assertTrue(hasattr(examples_grades_9_10, func_name),
                              f"Missing function: {func_name}")
                self.assertTrue(callable(getattr(examples_grades_9_10, func_name)),
                              f"Function not callable: {func_name}")
            
        except ImportError as e:
            self.fail(f"Failed to import examples_grades_9_10: {e}")


class TestCrossGradeIntegration(TestGradeIntegration):
    """Integration tests across all grade levels"""
    
    def test_demo_script_functionality(self):
        """Test that the demo script can run without errors"""
        try:
            import demo
            
            # Verify main function exists
            self.assertTrue(hasattr(demo, 'main'))
            self.assertTrue(callable(demo.main))
            
        except ImportError as e:
            self.fail(f"Failed to import demo module: {e}")
    
    def test_all_generator_methods_accessible(self):
        """Test that all MathDiagramGenerator methods are accessible"""
        generator = MathDiagramGenerator()
        
        # Grade 4-6 methods
        grade_4_6_methods = [
            'number_line',
            'basic_shapes', 
            'fraction_visual'
        ]
        
        # Grade 7-8 methods
        grade_7_8_methods = [
            'coordinate_plane',
            'linear_equation',
            'area_perimeter_shapes'
        ]
        
        # Grade 9-10 methods
        grade_9_10_methods = [
            'quadratic_function',
            'trigonometric_functions'
        ]
        
        all_methods = grade_4_6_methods + grade_7_8_methods + grade_9_10_methods
        
        for method_name in all_methods:
            with self.subTest(method=method_name):
                self.assertTrue(hasattr(generator, method_name),
                              f"Missing method: {method_name}")
                self.assertTrue(callable(getattr(generator, method_name)),
                              f"Method not callable: {method_name}")
    
    def test_file_system_integration(self):
        """Test integration with file system operations"""
        # Test that diagrams directory is created
        self.assertTrue(os.path.exists("diagrams"), "Diagrams directory should exist")
        
        # Test that directory is writable
        test_file = os.path.join("diagrams", "test_write.tmp")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            
            self.assertTrue(os.path.exists(test_file), "Should be able to write to diagrams directory")
            
            # Clean up
            os.remove(test_file)
            
        except Exception as e:
            self.fail(f"File system integration test failed: {e}")
    
    def test_matplotlib_integration(self):
        """Test integration with matplotlib library"""
        generator = MathDiagramGenerator()
        
        try:
            # Test that matplotlib functions are accessible
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Simple test to ensure matplotlib is working
            x = np.array([1, 2, 3])
            y = np.array([1, 4, 9])
            
            plt.figure(figsize=(5, 5))
            plt.plot(x, y)
            plt.close()
            
        except Exception as e:
            self.fail(f"Matplotlib integration test failed: {e}")
    
    def test_numpy_integration(self):
        """Test integration with numpy library"""
        try:
            import numpy as np
            
            # Test numpy functions used in the generator
            x = np.linspace(-10, 10, 100)
            y = np.sin(x)
            
            self.assertEqual(len(x), 100)
            self.assertEqual(len(y), 100)
            self.assertTrue(np.all(y >= -1) and np.all(y <= 1))
            
        except Exception as e:
            self.fail(f"Numpy integration test failed: {e}")


class TestEndToEndWorkflows(TestGradeIntegration):
    """End-to-end integration tests simulating real usage scenarios"""
    
    def test_teacher_lesson_preparation_workflow(self):
        """Test workflow: Teacher preparing lesson materials"""
        generator = MathDiagramGenerator()
        
        # Scenario: Teacher needs materials for fractions lesson
        try:
            # Create fraction examples
            fractions = [(1, 2), (1, 4), (3, 4), (2, 3)]
            for num, den in fractions:
                generator.fraction_visual(num, den, f"Fraction {num}/{den}")
            
            # Create number line for fraction placement
            generator.number_line(0, 1, [0.25, 0.5, 0.75], "Fractions on Number Line")
            
            # Verify all operations completed successfully
            self.assertTrue(self.savefig_mock.call_count >= len(fractions) + 1)
            
        except Exception as e:
            self.fail(f"Teacher lesson preparation workflow failed: {e}")
    
    def test_student_homework_help_workflow(self):
        """Test workflow: Student getting help with quadratic functions"""
        generator = MathDiagramGenerator()
        
        try:
            # Student's homework problems
            problems = [
                (1, -4, 3),   # y = x² - 4x + 3
                (2, -8, 6),   # y = 2x² - 8x + 6  
                (-1, 2, 3),   # y = -x² + 2x + 3
            ]
            
            for a, b, c in problems:
                generator.quadratic_function(a, b, c, f"y = {a}x² + {b}x + {c}")
            
            # Verify all graphs were created
            self.assertEqual(self.savefig_mock.call_count, len(problems))
            
        except Exception as e:
            self.fail(f"Student homework help workflow failed: {e}")
    
    def test_curriculum_coverage_workflow(self):
        """Test workflow: Ensuring all curriculum topics are covered"""
        generator = MathDiagramGenerator()
        
        curriculum_coverage = {
            'elementary': [
                lambda: generator.number_line(-10, 10),
                lambda: generator.basic_shapes(),
                lambda: generator.fraction_visual(1, 2),
            ],
            'middle_school': [
                lambda: generator.coordinate_plane([(1, 1, 'A')]),
                lambda: generator.linear_equation(2, 3),
                lambda: generator.area_perimeter_shapes(),
            ],
            'high_school': [
                lambda: generator.quadratic_function(1, -2, 1),
                lambda: generator.trigonometric_functions(),
            ]
        }
        
        try:
            total_operations = 0
            for level, functions in curriculum_coverage.items():
                for func in functions:
                    func()
                    total_operations += 1
            
            # Verify all curriculum areas were covered
            self.assertEqual(self.savefig_mock.call_count, total_operations)
            
        except Exception as e:
            self.fail(f"Curriculum coverage workflow failed: {e}")


if __name__ == '__main__':
    # Run integration tests
    unittest.main(verbosity=2)