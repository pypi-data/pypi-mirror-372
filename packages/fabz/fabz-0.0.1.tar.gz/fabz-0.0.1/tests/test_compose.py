"""Tests for the compose functionality."""
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import tempfile
import shutil
import yaml
from rappture.assemble import assemble, get_parents


class TestCompose:
    """Test cases for the compose function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create base props.yaml
        self.base_props: Dict[str, Any] = {
            "app_name": "test-app",
            "port": 8080,
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "testdb"
            },
            "features": {
                "auth": True,
                "cache": False
            }
        }
        
        # Create base template
        self.base_template = """deploy:
  name: <%=app_name%>
  port: <%=port%>
  database:
    host: <%=database.host%>
    port: <%=database.port%>
    name: <%=database.name%>
<%if features.auth == true%>
  auth_enabled: true
<%end%>
<%if features.cache == true%>
  cache_enabled: true
<%end%>"""
        
        # Write base files
        (self.temp_dir / "props.yaml").write_text(yaml.dump(self.base_props))
        (self.temp_dir / "app.yaml").write_text(self.base_template)
        
        # Create dev model
        dev_dir = self.temp_dir / "dev"
        dev_dir.mkdir()
        dev_props: Dict[str, Any] = {
            "database": {
                "host": "dev-db.local"
            },
            "features": {
                "cache": True
            },
            "debug": True
        }
        (dev_dir / "props.yaml").write_text(yaml.dump(dev_props))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_compose_base_model(self):
        """Test composing from base model (root level)."""
        result = assemble(self.temp_dir, self.temp_dir / "app.yaml")
        
        assert isinstance(result, dict)
        assert result["deploy"]["name"] == "test-app"
        assert result["deploy"]["port"] == 8080
        assert result["deploy"]["database"]["host"] == "localhost"
        assert "auth_enabled" in result["deploy"]
        # cache_enabled should not be present since cache is False
    
    def test_compose_dev_model(self):
        """Test composing with dev model overrides."""
        result = assemble(self.temp_dir, self.temp_dir / "dev" / "app.yaml")
        
        assert result["deploy"]["name"] == "test-app"  # from base
        assert result["deploy"]["port"] == 8080  # from base
        assert result["deploy"]["database"]["host"] == "dev-db.local"  # overridden
        assert result["deploy"]["database"]["port"] == 5432  # from base (merged)
        assert "auth_enabled" in result["deploy"]  # auth still True
        assert "cache_enabled" in result["deploy"]  # cache now True


class TestGetParents:
    """Test cases for get_parents utility function."""
    
    def test_get_parents_simple_path(self):
        """Test getting parents for simple path."""
        top = Path("/project")
        target = Path("/project/dev/staging")
        
        result = get_parents(top, target)
        
        # Should return paths from root to target
        expected = [
            Path("/project"),
            Path("/project/dev"),
            Path("/project/dev/staging")
        ]
        assert result == expected
    
    def test_get_parents_same_path(self):
        """Test getting parents when top and target are the same."""
        top = Path("/project")
        target = Path("/project")
        
        result = get_parents(top, target)
        assert result == [Path("/project")]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
