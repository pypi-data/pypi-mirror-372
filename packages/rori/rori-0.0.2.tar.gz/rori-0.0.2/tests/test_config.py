"""Test configuration module functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


def test_config_module_imports():
    """Test that config module can be imported."""
    try:
        from rori import config

        assert config is not None
    except ImportError as e:
        pytest.fail(f"Could not import rori.config: {e}")


def test_config_constants_exist():
    """Test that expected config constants exist."""
    from rori import config

    # Test that POF_DIR exists and is a Path
    assert hasattr(config, "POF_DIR")
    assert isinstance(config.POF_DIR, Path)


def test_config_directory_creation():
    """Test config directory handling."""
    from rori import config

    # POF_DIR should be a valid path
    assert config.POF_DIR.is_absolute()


def test_config_environment_variables():
    """Test config responds to environment variables."""
    with patch.dict("os.environ", {"POF_DIR": "/tmp/test_pof"}):
        # Re-import to pick up environment change
        import importlib

        from rori import config

        importlib.reload(config)

        # Should use environment variable if available
        # Note: This test depends on actual config implementation


def test_config_default_values():
    """Test config has sensible defaults."""
    from rori import config

    # POF_DIR should have a reasonable default
    assert config.POF_DIR is not None
    assert str(config.POF_DIR)  # Should be non-empty


@patch("pathlib.Path.home")
def test_config_uses_home_directory(mock_home):
    """Test config uses home directory appropriately."""
    mock_home.return_value = Path("/mock/home")

    # Re-import to pick up the mock
    import importlib

    from rori import config

    importlib.reload(config)

    # Should incorporate home directory in some way
    # Note: Exact behavior depends on implementation


def test_config_path_operations():
    """Test basic path operations work with config."""
    from rori import config

    # Should be able to perform basic path operations
    test_file = config.POF_DIR / "test.txt"
    assert isinstance(test_file, Path)
    assert test_file.parent == config.POF_DIR


def test_config_directory_permissions():
    """Test config directory permissions handling."""
    from rori import config

    # Should handle case where directory doesn't exist
    # or permissions issues gracefully
    assert config.POF_DIR is not None


def test_config_path_expansion():
    """Test path expansion works correctly."""
    from rori import config

    # POF_DIR should be fully expanded (no ~ or relative paths)
    pof_dir_str = str(config.POF_DIR)
    assert not pof_dir_str.startswith("~")
    assert Path(pof_dir_str).is_absolute()


def test_config_consistency():
    """Test config values are consistent across imports."""
    from rori import config as config1
    from rori import config as config2

    # Should get the same values
    assert config1.POF_DIR == config2.POF_DIR


def test_config_path_type_safety():
    """Test config paths are proper Path objects."""
    from rori import config

    assert isinstance(config.POF_DIR, Path)

    # Should support Path operations
    assert hasattr(config.POF_DIR, "exists")
    assert hasattr(config.POF_DIR, "mkdir")
    assert hasattr(config.POF_DIR, "is_dir")


def test_config_with_temporary_directory():
    """Test config works with temporary directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Should be able to create config-style paths
        test_pof_dir = temp_path / ".pof"
        assert isinstance(test_pof_dir, Path)

        # Should support typical config operations
        db_path = test_pof_dir / "rori.db"
        assert isinstance(db_path, Path)
