"""Test data models and database operations."""

from unittest.mock import MagicMock, patch

import pytest

from rori.models import PofDbEntry, Status


def test_status_enum():
    """Test Status enumeration values."""
    assert Status.ACTIVE == "active"
    assert Status.INACTIVE == "inactive"
    assert Status.ERROR == "error"


def test_pof_db_entry_creation():
    """Test PofDbEntry dataclass creation."""
    entry = PofDbEntry(
        hid=1, port_from=8080, port_to=80, type_="manual", metadata={"test": "value"}
    )

    assert entry.hid == 1
    assert entry.port_from == 8080
    assert entry.port_to == 80
    assert entry.type_ == "manual"
    assert entry.metadata == {"test": "value"}
    assert entry.created_at is not None


def test_pof_db_entry_defaults():
    """Test PofDbEntry default values."""
    entry = PofDbEntry(hid=1, port_from=8080, port_to=80)

    assert entry.type_ is None
    assert entry.metadata == {}


def test_pof_initialization():
    """Test Pof class initialization."""
    from rori.models import Pof

    pof = Pof()
    assert rori._hap is None
    assert rori._db_entry is None


def test_pof_requires_initialization():
    """Test that Pof properties require initialization."""
    from rori.models import Pof, RoriError

    pof = Pof()

    with pytest.raises(RoriError, match="Pof not initialized"):
        _ = rori.hid

    with pytest.raises(RoriError, match="Pof not initialized"):
        _ = rori.name

    with pytest.raises(RoriError, match="Pof not initialized"):
        _ = rori.status


@patch("rori.models.Hap")
def test_pof_with_hap(mock_hap_class):
    """Test Pof with initialized hap."""
    from rori.models import Pof

    # Setup mock hap
    mock_hap = MagicMock()
    mock_hap.hid = "test-hap"
    mock_hap.name = "test-forward"
    mock_hap.status = "running"
    mock_hap.runtime = "5m 30s"
    mock_hap.active = True

    # Initialize Pof with hap
    pof = Pof()
    rori._hap = mock_hap

    # Test properties
    assert rori.hid == "test-hap"
    assert rori.name == "test-forward"
    assert rori.uptime == "5m 30s"


@patch("rori.models.Hap")
def test_pof_inactive_uptime(mock_hap_class):
    """Test Pof uptime when inactive."""
    from rori.models import Pof

    # Setup mock hap
    mock_hap = MagicMock()
    mock_hap.active = False

    # Initialize Pof with hap
    pof = Pof()
    rori._hap = mock_hap

    # Mock status property to return INACTIVE
    with patch.object(pof, "status", Status.INACTIVE):
        assert rori.uptime == ""


def test_check_initialized_decorator():
    """Test the check_initialized decorator."""
    from rori.models import RoriError, check_initialized

    class TestClass:
        def __init__(self):
            self._hap = None

        @check_initialized
        def test_method(self):
            return "success"

    obj = TestClass()

    # Should raise error when _hap is None
    with pytest.raises(RoriError, match="Pof not initialized"):
        obj.test_method()

    # Should work when _hap is set
    obj._hap = MagicMock()
    result = obj.test_method()
    assert result == "success"


def test_pof_db_entry_serialization():
    """Test PofDbEntry can be used with JSON serialization."""
    import json

    entry = PofDbEntry(
        hid=1,
        port_from=8080,
        port_to=80,
        type_="manual",
        metadata={"namespace": "default", "service": "test-service"},
    )

    # Test that metadata can be serialized
    serialized = json.dumps(entry.metadata)
    deserialized = json.loads(serialized)

    assert deserialized == {"namespace": "default", "service": "test-service"}


def test_pof_error_inheritance():
    """Test that RoriError inherits from ValueError."""
    from rori.models import RoriError

    error = RoriError("Test error")
    assert isinstance(error, ValueError)
    assert str(error) == "Test error"
