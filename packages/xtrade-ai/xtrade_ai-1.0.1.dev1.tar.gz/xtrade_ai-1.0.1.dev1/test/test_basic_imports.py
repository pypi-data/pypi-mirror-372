"""
Basic import tests for XTrade-AI Framework
"""

import pytest


def test_xtrade_ai_import():
    """Test that the main package can be imported"""
    import xtrade_ai

    assert xtrade_ai is not None


def test_core_modules_import():
    """Test that core modules can be imported"""
    from xtrade_ai import base_environment, config, data_structures, xtrade_ai_framework

    assert config is not None
    assert data_structures is not None
    assert base_environment is not None
    assert xtrade_ai_framework is not None


def test_utils_import():
    """Test that utility modules can be imported"""
    from xtrade_ai.utils import error_handler, logger, memory_manager

    assert logger is not None
    assert error_handler is not None
    assert memory_manager is not None


def test_modules_import():
    """Test that module components can be imported"""
    from xtrade_ai.modules import monitoring, risk_management, technical_analysis

    assert technical_analysis is not None
    assert risk_management is not None
    assert monitoring is not None


def test_version():
    """Test that version information is available"""
    from xtrade_ai import __version__

    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_cli_import():
    """Test that CLI module can be imported"""
    from xtrade_ai import cli

    assert cli is not None


if __name__ == "__main__":
    pytest.main([__file__])
