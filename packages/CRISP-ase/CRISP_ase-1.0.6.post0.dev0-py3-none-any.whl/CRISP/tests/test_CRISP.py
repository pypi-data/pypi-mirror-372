"""Basic CRISP package tests."""

import pytest
import CRISP


def test_crisp_import():
    """Test that CRISP can be imported."""
    assert CRISP is not None


def test_crisp_version():
    """Test that CRISP has a version."""
    try:
        version = CRISP.__version__
        assert isinstance(version, str)
    except AttributeError:
        pass


def test_crisp_modules():
    """Test that main modules can be imported."""
    try:
        from CRISP.simulation_utility import atomic_indices
        from CRISP.data_analysis import msd
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import CRISP modules: {e}")