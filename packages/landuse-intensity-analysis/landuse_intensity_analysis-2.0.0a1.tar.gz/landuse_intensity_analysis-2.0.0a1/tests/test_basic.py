"""
Basic tests for the landuse_intensity package.
"""
import pytest
import sys
from pathlib import Path

def test_package_import():
    """Test that the package can be imported successfully."""
    try:
        import landuse_intensity
        assert landuse_intensity is not None
    except ImportError as e:
        pytest.fail(f"Failed to import landuse_intensity: {e}")

def test_core_module_import():
    """Test that the core module can be imported."""
    try:
        from landuse_intensity import core
        assert core is not None
    except ImportError as e:
        pytest.fail(f"Failed to import landuse_intensity.core: {e}")

def test_utils_module_import():
    """Test that the utils module can be imported."""
    try:
        from landuse_intensity import utils
        assert utils is not None
    except ImportError as e:
        pytest.fail(f"Failed to import landuse_intensity.utils: {e}")

def test_visualization_module_import():
    """Test that the visualization module can be imported."""
    try:
        from landuse_intensity import visualization
        assert visualization is not None
    except ImportError as e:
        pytest.fail(f"Failed to import landuse_intensity.visualization: {e}")

def test_python_version():
    """Test that we're running on a supported Python version."""
    assert sys.version_info >= (3, 8), "Python 3.8+ is required"

def test_package_structure():
    """Test that the package has the expected structure."""
    try:
        import landuse_intensity
        package_path = Path(landuse_intensity.__file__).parent
        
        # Check for core files
        assert (package_path / "core.py").exists(), "core.py should exist"
        assert (package_path / "utils.py").exists(), "utils.py should exist"
        assert (package_path / "visualization.py").exists(), "visualization.py should exist"
        
    except Exception as e:
        pytest.fail(f"Package structure test failed: {e}")
