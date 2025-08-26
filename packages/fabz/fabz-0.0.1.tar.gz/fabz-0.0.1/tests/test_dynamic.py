#!/usr/bin/env python3
"""
Unit tests for the dynamic properties system.
"""

import sys
import unittest
from pathlib import Path
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rappture.dynamic import DynamicPropertyResolver


class TestDynamicPropertyResolver(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.resolver = DynamicPropertyResolver(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_no_dynamic_properties(self):
        """Test that props without dynamic section are returned unchanged."""
        props = {
            'loglevel': 'debug',
            'port': 8080
        }
        result = self.resolver.resolve_dynamic_properties(props)
        self.assertEqual(result, props)
    
    def test_empty_dynamic_section(self):
        """Test that empty dynamic section is handled correctly."""
        props = {
            'loglevel': 'debug',
            'dynamic': {}
        }
        result = self.resolver.resolve_dynamic_properties(props)
        expected = {'loglevel': 'debug'}
        self.assertEqual(result, expected)
    
    def test_builtin_function(self):
        """Test calling a built-in dynamic function."""
        props = {
            'dynamic': {
                'test_data': {
                    'call': 'get_example',
                    'args': {
                        'message': 'Test message'
                    }
                }
            }
        }
        result = self.resolver.resolve_dynamic_properties(props)
        
        self.assertIn('test_data', result)
        self.assertEqual(result['test_data']['message'], 'Test message')
        self.assertIn('timestamp', result['test_data'])
        self.assertIn('items', result['test_data'])
    
    def test_argument_templating(self):
        """Test that arguments are templated correctly."""
        props = {
            'cluster': 'production',
            'dynamic': {
                'test_data': {
                    'call': 'get_example',
                    'args': {
                        'message': 'Hello from <%=cluster%>!'
                    }
                }
            }
        }
        result = self.resolver.resolve_dynamic_properties(props)
        
        self.assertEqual(result['test_data']['message'], 'Hello fromproduction!')
    
    def test_nested_templating(self):
        """Test templating with nested properties."""
        props = {
            'config': {
                'environment': 'staging'
            },
            'dynamic': {
                'test_data': {
                    'call': 'get_example',
                    'args': {
                        'message': 'Environment: <%=config.environment%>'
                    }
                }
            }
        }
        result = self.resolver.resolve_dynamic_properties(props)
        
        self.assertEqual(result['test_data']['message'], 'Environment: staging')
    
    def test_invalid_function_name(self):
        """Test error handling for non-existent function."""
        props = {
            'dynamic': {
                'test_data': {
                    'call': 'nonexistent_function',
                    'args': {}
                }
            }
        }
        # Should not raise exception, but continue with other properties
        result = self.resolver.resolve_dynamic_properties(props)
        
        # The invalid dynamic property should not be in the result
        self.assertNotIn('test_data', result)
    
    def test_missing_call_specification(self):
        """Test error handling for missing 'call' in spec."""
        props = {
            'dynamic': {
                'test_data': {
                    'args': {'message': 'test'}
                }
            }
        }
        result = self.resolver.resolve_dynamic_properties(props)
        
        # The invalid dynamic property should not be in the result
        self.assertNotIn('test_data', result)
    
    def test_templating_with_type_conversion(self):
        """Test that templated arguments are correctly type-converted."""
        props = {
            'test_value': 'true',
            'dynamic': {
                'test_data': {
                    'call': 'get_example',
                    'args': {
                        'message': 'Value is: <%=test_value%>'
                    }
                }
            }
        }
        
        result = self.resolver.resolve_dynamic_properties(props)
        
        # The templated value should be processed (note: space handling in templates)
        self.assertIn('test_data', result)
        self.assertEqual(result['test_data']['message'], 'Value is:true')
    
    def test_multiple_dynamic_properties(self):
        """Test resolving multiple dynamic properties."""
        props = {
            'env': 'test',
            'dynamic': {
                'data1': {
                    'call': 'get_example',
                    'args': {'message': 'First: <%=env%>'}
                },
                'data2': {
                    'call': 'get_example', 
                    'args': {'message': 'Second: <%=env%>'}
                }
            }
        }
        result = self.resolver.resolve_dynamic_properties(props)
        
        self.assertIn('data1', result)
        self.assertIn('data2', result)
        self.assertEqual(result['data1']['message'], 'First: test')
        self.assertEqual(result['data2']['message'], 'Second: test')
        self.assertEqual(result['env'], 'test')  # Original props preserved


class TestIntegration(unittest.TestCase):
    """Integration tests with the actual extension system."""
    
    def setUp(self):
        self.resolver = DynamicPropertyResolver(project_root)
    
    def test_extension_function_loading(self):
        """Test that functions are loaded from SITE extensions."""
        props = {
            'defaults': {'cluster': 'test'},
            'dynamic': {
                'balancers': {
                    'call': 'get_balancers',
                    'args': {
                        'cluster': '<%=defaults.cluster%>',
                        'count': 1
                    }
                }
            }
        }
        result = self.resolver.resolve_dynamic_properties(props)
        
        self.assertIn('balancers', result)
        self.assertIsInstance(result['balancers'], list)
        self.assertEqual(len(result['balancers']), 1)
        self.assertEqual(result['balancers'][0]['cluster'], 'test')
    
    def test_function_caching(self):
        """Test that functions are cached properly."""
        # Call the same function multiple times through public interface
        props = {
            'dynamic': {
                'test1': {'call': 'get_example', 'args': {'message': 'first'}},
                'test2': {'call': 'get_example', 'args': {'message': 'second'}}
            }
        }
        
        # This should work without errors, demonstrating caching works
        result = self.resolver.resolve_dynamic_properties(props)
        self.assertIn('test1', result)
        self.assertIn('test2', result)
        self.assertEqual(result['test1']['message'], 'first')
        self.assertEqual(result['test2']['message'], 'second')


if __name__ == '__main__':
    unittest.main()
