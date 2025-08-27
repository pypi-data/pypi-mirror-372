"""
Tox plugin to automatically configure chainctl authentication for test environments.

This plugin ensures that chainctl authentication is available when running tests
with tox, particularly useful for testing packages that depend on private
repositories hosted on *.cgr.dev domains.
"""

import os
import logging
from tox import hookimpl


logger = logging.getLogger(__name__)


@hookimpl
def tox_configure(config):
    """Configure tox to use chainctl authentication."""
    # Ensure CHAINCTL_PARENT is set in the environment
    parent = os.environ.get("CHAINCTL_PARENT")
    if not parent:
        logger.warning(
            "CHAINCTL_PARENT environment variable not set. "
            "Chainctl authentication may not work in tox environments."
        )
    
    # Log that the plugin is active
    logger.info("Chainctl auth tox plugin activated")


@hookimpl
def tox_testenv_install_deps(venv, action):
    """
    Hook called before installing dependencies in a test environment.
    
    Ensures chainctl authentication is available for pip installations.
    """
    # Set environment variables for the venv
    venv.set_env("CHAINCTL_PARENT", os.environ.get("CHAINCTL_PARENT", ""))
    
    # Ensure the keyring backend is available
    result = venv.run_install(
        ["keyrings-chainguard-libraries"],
        action=action,
    )
    
    if result:
        action.setactivity("chainctl-auth", "Installed chainctl keyring backend")
    
    return result


@hookimpl
def tox_runtest_pre(venv):
    """
    Hook called before running tests.
    
    Verifies that chainctl is available and properly configured.
    """
    # Check if chainctl is available
    try:
        result = venv.run(["chainctl", "version"], capture=True, check=False)
        if result.returncode != 0:
            logger.warning(
                "chainctl command not found or not working properly. "
                "Authentication to *.cgr.dev repositories may fail."
            )
    except Exception as e:
        logger.warning(f"Could not verify chainctl installation: {e}")


# Plugin metadata
plugin = "chainctl_auth_tox.bootstrap"