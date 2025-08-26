"""Tests for the Templater class."""
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pytest
except ImportError:
    pytest = None

from rappture.template import Templater


class TestTemplater:
    """Test cases for the Templater class."""
    
    def test_simple_variable_substitution(self):
        """Test basic variable substitution."""
        template = "name: <%=service.name%>\nport: <%=service.port%>"
        data: Dict[str, Any] = {
            "service": {
                "name": "web-app",
                "port": 8080
            }
        }
        templater = Templater(template)
        result = templater.render(data)
        
        assert "name: web-app" in result
        assert "port: 8080" in result
    
    def test_nested_property_access(self):
        """Test accessing deeply nested properties."""
        template = "image: <%=services.nxcortex.image%>"
        data: Dict[str, Any] = {
            "services": {
                "nxcortex": {
                    "image": "nxcortex:latest"
                }
            }
        }
        templater = Templater(template)
        result = templater.render(data)
        
        assert result.strip() == "image: nxcortex:latest"
    
    def test_list_substitution_with_proper_indentation(self):
        """Test that lists are properly indented in YAML."""
        template = """env:
  SENTINELS: <%=sentinels%>"""
        data: Dict[str, Any] = {
            "sentinels": ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
        }
        templater = Templater(template)
        result = templater.render(data)
        
        # Check that list items are properly indented
        lines = result.split('\n')
        assert "SENTINELS:" in lines[1]
        assert "    - 10.0.0.1" in result
        assert "    - 10.0.0.2" in result
        assert "    - 10.0.0.3" in result
    
    def test_conditional_if_true(self):
        """Test conditional rendering when condition is true."""
        template = """<%if secure == 1%>
ssl_enabled: true
<%else%>
ssl_enabled: false
<%end%>"""
        data: Dict[str, Any] = {"secure": 1}
        templater = Templater(template)
        result = templater.render(data)
        
        assert "ssl_enabled: true" in result
        assert "ssl_enabled: false" not in result
    
    def test_conditional_if_false(self):
        """Test conditional rendering when condition is false."""
        template = """<%if secure == 1%>
ssl_enabled: true
<%else%>
ssl_enabled: false
<%end%>"""
        data: Dict[str, Any] = {"secure": 0}
        templater = Templater(template)
        result = templater.render(data)
        
        assert "ssl_enabled: false" in result
        assert "ssl_enabled: true" not in result
    
    def test_conditional_without_else(self):
        """Test conditional without else clause."""
        template = """base_config: true
<%if debug == 1%>
debug_mode: enabled
<%end%>
production: false"""
        data: Dict[str, Any] = {"debug": 1}
        templater = Templater(template)
        result = templater.render(data)
        
        assert "base_config: true" in result
        assert "debug_mode: enabled" in result
        assert "production: false" in result
    
    def test_conditional_skipped_when_false(self):
        """Test that conditional content is skipped when false."""
        template = """base_config: true
<%if debug == 1%>
debug_mode: enabled
<%end%>
production: false"""
        data: Dict[str, Any] = {"debug": 0}
        templater = Templater(template)
        result = templater.render(data)
        
        assert "base_config: true" in result
        assert "debug_mode: enabled" not in result
        assert "production: false" in result
    
    def test_nested_conditionals(self):
        """Test nested conditional statements."""
        template = """<%if env == 'prod'%>
production: true
<%if secure == 1%>
ssl: required
<%end%>
<%else%>
production: false
<%end%>"""
        data: Dict[str, Any] = {"env": "prod", "secure": 1}
        templater = Templater(template)
        result = templater.render(data)
        
        assert "production: true" in result
        assert "ssl: required" in result
        assert "production: false" not in result
    
    def test_string_condition_evaluation(self):
        """Test string-based condition evaluation."""
        template = """<%if environment == 'development'%>
debug: true
<%end%>"""
        data: Dict[str, Any] = {"environment": "development"}
        templater = Templater(template)
        result = templater.render(data)
        
        assert "debug: true" in result
    
    def test_null_value_handling(self):
        """Test handling of null/None values."""
        template = """cluster: <%=cluster%>
host: <%=host%>"""
        data: Dict[str, Any] = {"cluster": None, "host": "localhost"}
        templater = Templater(template)
        result = templater.render(data)
        
        assert "cluster: null" in result
        assert "host: localhost" in result
    
    def test_missing_property_returns_none(self):
        """Test that missing properties return None."""
        template = "missing: <%=does.not.exist%>"
        data: Dict[str, Any] = {"other": "value"}
        templater = Templater(template)
        result = templater.render(data)
        
        assert "missing: null" in result
    
    def test_dict_substitution_with_proper_indentation(self):
        """Test that dictionaries are properly indented."""
        template = """service:
  config: <%=config%>"""
        data: Dict[str, Any] = {
            "config": {
                "timeout": 30,
                "retries": 3,
                "hosts": ["host1", "host2"]
            }
        }
        templater = Templater(template)
        result = templater.render(data)
        
        # Should contain properly indented YAML
        assert "timeout: 30" in result
        assert "retries: 3" in result
        assert "- host1" in result
    
    def test_boolean_conditions(self):
        """Test boolean value conditions."""
        template = """<%if enabled == true%>
status: active
<%else%>
status: inactive
<%end%>"""
        data: Dict[str, Any] = {"enabled": True}
        templater = Templater(template)
        result = templater.render(data)
        
        assert "status: active" in result
        assert "status: inactive" not in result
    
    def test_number_parsing_in_conditions(self):
        """Test numeric value parsing in conditions."""
        template = """<%if port == 8080%>
service: web
<%end%>
<%if timeout == 30.5%>
type: slow
<%end%>"""
        data: Dict[str, Any] = {"port": 8080, "timeout": 30.5}
        templater = Templater(template)
        result = templater.render(data)
        
        assert "service: web" in result
        assert "type: slow" in result


class TestTemplaterEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_template(self):
        """Test rendering empty template."""
        templater = Templater("")
        result = templater.render({})
        assert result == ""
    
    def test_template_without_variables(self):
        """Test template with no variables."""
        template = "static: content\nno_variables: here"
        templater = Templater(template)
        result = templater.render({})
        assert result == template
    
    def test_malformed_conditional(self):
        """Test handling of malformed conditionals."""
        template = "<%if invalid condition%>\ncontent\n<%end%>"
        templater = Templater(template)
        result = templater.render({"test": "value"})
        
        # Should not include the content since condition is malformed
        assert "content" not in result
    
    def test_unmatched_conditional_tags(self):
        """Test handling of unmatched conditional tags."""
        template = "<%if test == 1%>\ncontent without end tag"
        templater = Templater(template)
        result = templater.render({"test": 1})
        
        # Should include the original tags when malformed
        assert "<%if test == 1%>" in result


if __name__ == "__main__":
    try:
        import pytest
        pytest.main([__file__])
    except ImportError:
        print("pytest not available, please install: pip install pytest")
        import sys
        sys.exit(1)
