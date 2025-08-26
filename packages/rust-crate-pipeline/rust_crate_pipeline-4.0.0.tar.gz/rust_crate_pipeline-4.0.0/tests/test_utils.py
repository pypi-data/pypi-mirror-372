"""Test utilities for rust_crate_pipeline tests."""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import subprocess utilities
from rust_crate_pipeline.utils.subprocess_utils import (
    cleanup_subprocess, run_command_with_cleanup, setup_asyncio_windows_fixes)

# Set up Windows-specific fixes for tests
setup_asyncio_windows_fixes()


async def run_command_for_tests(
    command: List[str],
    cwd: Optional[Path] = None,
    logger: Optional[logging.Logger] = None,
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Test version of run_command_with_cleanup that can be used in tests.

    Args:
        command: The command to run as a list of strings
        cwd: Working directory for the command (defaults to current directory)
        logger: Optional logger for debug messages

    Returns:
        Tuple of (results, error_message)
    """
    if cwd is None:
        cwd = Path.cwd()

    if logger is None:
        logger = logging.getLogger(__name__)

    return await run_command_with_cleanup(command, cwd, logger)


async def cleanup_subprocess_for_tests(
    process: Optional[asyncio.subprocess.Process],
    logger: Optional[logging.Logger] = None,
) -> None:
    """
    Test version of cleanup_subprocess that can be used in tests.

    Args:
        process: The subprocess to cleanup
        logger: Optional logger for debug messages
    """
    await cleanup_subprocess(process, logger)


def get_test_logger(name: str = "test") -> logging.Logger:
    """
    Get a test logger configured for testing.

    Args:
        name: Logger name

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger
