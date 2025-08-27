"""Tests for the tox plugin."""

import os
from unittest.mock import Mock, patch

from chainctl_auth_tox.bootstrap import tox_configure, tox_testenv_install_deps, tox_runtest_pre


def test_tox_configure_with_parent():
    """Test tox_configure when CHAINCTL_PARENT is set."""
    mock_config = Mock()
    
    with patch.dict(os.environ, {"CHAINCTL_PARENT": "test-parent"}):
        with patch("chainctl_auth_tox.bootstrap.logger") as mock_logger:
            tox_configure(mock_config)
            # Should log that plugin is active
            mock_logger.info.assert_called_with("Chainctl auth tox plugin activated")
            # Should not warn about missing parent
            mock_logger.warning.assert_not_called()


def test_tox_configure_without_parent():
    """Test tox_configure when CHAINCTL_PARENT is not set."""
    mock_config = Mock()
    
    with patch.dict(os.environ, {}, clear=True):
        with patch("chainctl_auth_tox.bootstrap.logger") as mock_logger:
            tox_configure(mock_config)
            # Should log that plugin is active
            mock_logger.info.assert_called_with("Chainctl auth tox plugin activated")
            # Should warn about missing parent
            mock_logger.warning.assert_called_once()


def test_tox_testenv_install_deps():
    """Test tox_testenv_install_deps hook."""
    mock_venv = Mock()
    mock_action = Mock()
    mock_venv.run_install.return_value = True
    
    with patch.dict(os.environ, {"CHAINCTL_PARENT": "test-parent"}):
        result = tox_testenv_install_deps(mock_venv, mock_action)
    
    # Should set environment variable
    mock_venv.set_env.assert_called_with("CHAINCTL_PARENT", "test-parent")
    # Should install the keyring package
    mock_venv.run_install.assert_called_with(
        ["keyrings-chainguard-libraries"],
        action=mock_action,
    )
    # Should set activity
    mock_action.setactivity.assert_called_with(
        "chainctl-auth", "Installed chainctl keyring backend"
    )
    assert result is True


def test_tox_runtest_pre_chainctl_available():
    """Test tox_runtest_pre when chainctl is available."""
    mock_venv = Mock()
    mock_result = Mock(returncode=0)
    mock_venv.run.return_value = mock_result
    
    with patch("chainctl_auth_tox.bootstrap.logger") as mock_logger:
        tox_runtest_pre(mock_venv)
    
    # Should check chainctl version
    mock_venv.run.assert_called_with(
        ["chainctl", "version"], capture=True, check=False
    )
    # Should not log warning
    mock_logger.warning.assert_not_called()


def test_tox_runtest_pre_chainctl_not_available():
    """Test tox_runtest_pre when chainctl is not available."""
    mock_venv = Mock()
    mock_result = Mock(returncode=1)
    mock_venv.run.return_value = mock_result
    
    with patch("chainctl_auth_tox.bootstrap.logger") as mock_logger:
        tox_runtest_pre(mock_venv)
    
    # Should check chainctl version
    mock_venv.run.assert_called_with(
        ["chainctl", "version"], capture=True, check=False
    )
    # Should log warning
    mock_logger.warning.assert_called_once()


def test_tox_runtest_pre_exception():
    """Test tox_runtest_pre when checking chainctl raises exception."""
    mock_venv = Mock()
    mock_venv.run.side_effect = Exception("Command failed")
    
    with patch("chainctl_auth_tox.bootstrap.logger") as mock_logger:
        tox_runtest_pre(mock_venv)
    
    # Should log warning about the exception
    mock_logger.warning.assert_called_once()
    assert "Could not verify chainctl installation" in str(mock_logger.warning.call_args)