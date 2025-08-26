#!/usr/bin/env python3
"""
Tests for the @dynamic decorator and direct function call system.

This replaces the old dynamic: section tests with tests for the new
direct function call syntax in templates.
"""

import unittest
from pathlib import Path
import sys
import tempfile

# Add rappture to Python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from rappture.dynamic import DynamicPropertyResolver, get_registered_functions, clear_registry, dynamic
from rappture.template import Templater


class TestDirectFunctionCalls(unittest.TestCase):
    """Test the new direct function call system."""
    
    def setUp(self):
        """Set up test environment."""
        # Clear registry to avoid interference between tests
        clear_registry()
        
        # Create a temporary project directory
        self.temp_dir = Path(tempfile.mkdtemp())
        self.resolver = DynamicPropertyResolver(self.temp_dir)
        
    def tearDown(self):
        """Clean up after tests."""
        clear_registry()
        
        # Clean up temp directory
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_dynamic_decorator_registration(self):
        """Test that @dynamic decorator registers functions correctly."""
        @dynamic
        def test_function():
            return {"test": "value"}
            
        functions = get_registered_functions()
        self.assertIn("test_function", functions)
        self.assertEqual(functions["test_function"](), {"test": "value"})
        
    def test_direct_function_call_in_template(self):
        """Test calling a registered function directly in a template."""
        @dynamic
        def get_test_data(message: str = "default"):
            return {"message": message, "timestamp": "2025-08-24"}
            
        template = "data: <%=get_test_data()%>"
        templater = Templater(template)
        result = templater.render({})
        
        self.assertIn("message: default", result)
        self.assertIn("timestamp: '2025-08-24'", result)
        
    def test_function_call_with_parameters(self):
        """Test function calls with parameters."""
        @dynamic
        def get_config(env: str = "dev", count: int = 1):
            return {"environment": env, "replicas": count}
            
        template = 'config: <%=get_config(env="production", count=3)%>'
        templater = Templater(template)
        result = templater.render({})
        
        self.assertIn("environment: production", result)
        self.assertIn("replicas: 3", result)
        
    def test_array_parameters(self):
        """Test function calls with array parameters."""
        @dynamic
        def get_services(services: list = None):
            if services is None:
                services = ["default"]
            return {"services": services}
            
        template = 'config: <%=get_services(services=["web", "api", "db"])%>'
        templater = Templater(template)
        result = templater.render({})
        
        self.assertIn("- web", result)
        self.assertIn("- api", result)
        self.assertIn("- db", result)
        
    def test_mixed_template_syntax(self):
        """Test mixing function calls with regular property access."""
        @dynamic
        def get_database():
            return {"host": "db.example.com", "port": 5432}
            
        template = """
app: <%=app.name%>
version: <%=app.version%>
database: <%=get_database()%>
"""
        
        props = {"app": {"name": "testapp", "version": "1.0"}}
        templater = Templater(template)
        result = templater.render(props)
        
        self.assertIn("app: testapp", result)
        self.assertIn("version: 1.0", result)  # YAML doesn't always quote simple strings
        self.assertIn("host: db.example.com", result)
        self.assertIn("port: 5432", result)
        
    def test_nonexistent_function_returns_null(self):
        """Test that calling a non-existent function returns null gracefully."""
        template = "result: <%=nonexistent_function()%>"
        templater = Templater(template)
        result = templater.render({})
        
        self.assertIn("result: null", result)
        
    def test_function_error_handling(self):
        """Test error handling in function calls."""
        @dynamic
        def failing_function():
            raise ValueError("Test error")
            
        template = "result: <%=failing_function()%>"
        templater = Templater(template)
        result = templater.render({})
        
        # Should gracefully handle the error and return null
        self.assertIn("result: null", result)
        
    def test_complex_yaml_structure(self):
        """Test function calls in complex YAML structures."""
        @dynamic
        def get_replicas(env: str = "dev"):
            return 3 if env == "prod" else 1
            
        @dynamic
        def get_resources(env: str = "dev"):
            if env == "prod":
                return {"cpu": "1000m", "memory": "1Gi"}
            return {"cpu": "100m", "memory": "128Mi"}
            
        template = """
services:
  web:
    replicas: <%=get_replicas(env="prod")%>
    resources: <%=get_resources(env="prod")%>
  api:
    replicas: <%=get_replicas(env="dev")%>
    resources: <%=get_resources(env="dev")%>
"""
        
        templater = Templater(template)
        result = templater.render({})
        
        # Check production values
        self.assertIn("replicas: 3", result)
        self.assertIn("cpu: 1000m", result)
        self.assertIn("memory: 1Gi", result)
        
        # Check dev values  
        self.assertIn("replicas: 1", result)
        self.assertIn("cpu: 100m", result)
        self.assertIn("memory: 128Mi", result)
        
    def test_extension_loading(self):
        """Test that extensions are loaded from SITE directory."""
        # This test verifies that the system attempts to load extensions
        # The actual loading is tested through integration tests
        resolver = DynamicPropertyResolver(self.temp_dir)
        
        # Should complete without error even if no extensions exist
        self.assertIsInstance(resolver, DynamicPropertyResolver)
        
    def test_registry_persistence(self):
        """Test that registered functions persist across multiple calls."""
        @dynamic
        def persistent_function():
            return "persistent"
            
        # Call function multiple times
        template = "<%=persistent_function()%>"
        templater = Templater(template)
        
        result1 = templater.render({})
        result2 = templater.render({})
        
        self.assertEqual(result1, result2)
        self.assertIn("persistent", result1)


if __name__ == "__main__":
    unittest.main()
