"""Integration tests using the example project structure."""
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rappture.assemble import assemble
from rappture.template import Templater


def test_example_project_integration():
    """Test the complete workflow using the example project."""
    # Get the example directory
    example_dir = Path(__file__).parent.parent / "example"
    
    if not example_dir.exists():
        # Skip if example doesn't exist
        return
    
    # Test base model
    result = assemble(example_dir, example_dir / "nxcortex.yaml")
    assert isinstance(result, dict)
    assert "deploy" in result
    assert result["deploy"]["name"] == "nxcortex"
    assert result["deploy"]["image"] == "nxcortex:latest"
    
    # Test dev model 
    result = assemble(example_dir, example_dir / "dev" / "nxcortex.yaml")
    assert isinstance(result, dict)
    assert "deploy" in result
    # Should have properties merged from dev model
    assert result["deploy"]["env"]["DB_HOST"] == "127.0.0.1"  # from dev props
    
    # Test live model
    result = assemble(example_dir, example_dir / "live" / "nxcortex.yaml")
    assert isinstance(result, dict)
    assert "deploy" in result
    # Should have live model properties
    
    print("✅ Integration tests passed!")


def test_templater_with_example_data():
    """Test the Templater with realistic data from the example."""
    template = """deploy:
  name: <%=service_name%>
  image: <%=services.nxcortex.image%>
  env:
    HOST: <%=machine.host%>
<%if secure == 1%>
    SSL_ENABLED: true
<%end%>
    PORTS: <%=ports%>"""
    
    data: Dict[str, Any] = {
        "service_name": "test-service",
        "services": {
            "nxcortex": {
                "image": "nxcortex:v1.2.3"
            }
        },
        "machine": {
            "host": "production.example.com"
        },
        "secure": 1,
        "ports": [8080, 8443]
    }
    
    templater = Templater(template)
    result = templater.render(data)
    
    # Verify the output
    assert "test-service" in result  # Check for the value, not exact format
    assert "nxcortex:v1.2.3" in result
    assert "production.example.com" in result
    assert "SSL_ENABLED: true" in result
    assert "- 8080" in result
    assert "- 8443" in result
    
    print("✅ Templater integration test passed!")


if __name__ == "__main__":
    test_example_project_integration()
    test_templater_with_example_data()
    print("🎉 All integration tests completed successfully!")
