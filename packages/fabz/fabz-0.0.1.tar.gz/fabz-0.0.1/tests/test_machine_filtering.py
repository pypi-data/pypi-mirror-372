#!/usr/bin/env python3
"""
Test cases for machine filtering functionality
"""
import sys
from pathlib import Path
from typing import Dict, Any

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rappture.machines.machines import get_machine_source
from rappture.protocols import Machine

def test_sqlite_machine_filtering():
    """Test filtering functionality with SQLite source"""
    print("Testing SQLite machine filtering...")
    
    project_path = Path("./example")
    sqlite_config: Dict[str, Any] = {
        "source": "Sqlite",
        "file": "machines.db"
    }
    
    machine_source = get_machine_source(project_path, sqlite_config)
    
    # Test no filters - should return all machines
    all_machines = list(machine_source.machines())
    assert len(all_machines) > 0, "Should return machines when no filters applied"
    
    # Test cluster filter
    data_machines = list(machine_source.machines(cluster="data"))
    assert len(data_machines) == 3, f"Expected 3 data cluster machines, got {len(data_machines)}"
    assert all(m.cluster == "data" for m in data_machines), "All machines should be in data cluster"
    
    # Test app filter
    cortex_machines = list(machine_source.machines(app="cortex"))
    assert len(cortex_machines) == 3, f"Expected 3 cortex machines, got {len(cortex_machines)}"
    assert all("cortex" in m.apps for m in cortex_machines), "All machines should have cortex app"
    
    # Test combined filters
    us_turn_machines = list(machine_source.machines(cluster="us", app="turn"))
    assert len(us_turn_machines) == 10, f"Expected 10 US turn machines, got {len(us_turn_machines)}"
    assert all(m.cluster == "us" and "turn" in m.apps for m in us_turn_machines), "All machines should be US turn servers"
    
    # Test non-existent filter
    nonexistent = list(machine_source.machines(cluster="nonexistent"))
    assert len(nonexistent) == 0, "Should return empty list for non-existent cluster"
    
    print("✅ SQLite machine filtering tests passed!")

def test_list_machine_filtering():
    """Test filtering functionality with in-memory list source"""
    print("Testing list machine filtering...")
    
    # Create test machines
    machines = [
        Machine(IP="1.2.3.4", host="test1", cluster="us", name="test1", apps=["api", "turn"]),
        Machine(IP="1.2.3.5", host="test2", cluster="us", name="test2", apps=["data"]),
        Machine(IP="1.2.3.6", host="test3", cluster="eu", name="test3", apps=["api"]),
    ]
    
    list_config: Dict[str, Any] = {
        "source": "List",
        "machines": [m.model_dump() for m in machines]
    }
    
    machine_source = get_machine_source(Path("."), list_config)
    
    # Test no filters
    all_machines = list(machine_source.machines())
    assert len(all_machines) == 3, f"Expected 3 machines, got {len(all_machines)}"
    
    # Test cluster filter
    us_machines = list(machine_source.machines(cluster="us"))
    assert len(us_machines) == 2, f"Expected 2 US machines, got {len(us_machines)}"
    assert all(m.cluster == "us" for m in us_machines), "All machines should be in US cluster"
    
    # Test app filter
    api_machines = list(machine_source.machines(app="api"))
    assert len(api_machines) == 2, f"Expected 2 API machines, got {len(api_machines)}"
    assert all("api" in m.apps for m in api_machines), "All machines should have API app"
    
    # Test combined filters
    us_api_machines = list(machine_source.machines(cluster="us", app="api"))
    assert len(us_api_machines) == 1, f"Expected 1 US API machine, got {len(us_api_machines)}"
    assert us_api_machines[0].name == "test1", "Should return test1 machine"
    
    print("✅ List machine filtering tests passed!")

def test_machines_md_syntax():
    """Test the exact syntax described in MACHINES.md"""
    print("Testing MACHINES.md syntax...")
    
    project_path = Path("./example")
    sqlite_config: Dict[str, Any] = {
        "source": "Sqlite", 
        "file": "machines.db"
    }

    machine_source = get_machine_source(project_path, sqlite_config)

    # This is the exact syntax from MACHINES.md
    machines = machine_source.machines(cluster="us", app="turn")
    machine_list = list(machines)
    
    assert len(machine_list) == 10, f"Expected 10 machines, got {len(machine_list)}"
    assert all(m.cluster == "us" and "turn" in m.apps for m in machine_list), "All should be US turn servers"
    
    print("✅ MACHINES.md syntax test passed!")

if __name__ == "__main__":
    test_sqlite_machine_filtering()
    test_list_machine_filtering()
    test_machines_md_syntax()
    print("\n🎉 All machine filtering tests passed!")
