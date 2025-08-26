"""Utility functions for proper subprocess management and cleanup."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


async def run_command_with_cleanup(
    command: List[str],
    cwd: Path,
    logger: Optional[logging.Logger] = None,
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Runs a command with proper cleanup to prevent asyncio transport warnings.

    Args:
        command: The command to run as a list of strings
        cwd: Working directory for the command
        logger: Optional logger for debug messages

    Returns:
        Tuple of (results, error_message)
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    logger.info(f"Running command: {' '.join(command)} in {cwd}")
    process = None

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            logger.warning(f"Command failed with exit code {process.returncode}")
            logger.warning(f"Stderr: {stderr.decode(errors='ignore')}")

        results = []
        if stdout:
            for line in stdout.decode(errors="ignore").splitlines():
                if line.strip():
                    try:
                        import json

                        results.append(json.loads(line))
                    except json.JSONDecodeError:
                        logger.warning(f"Could not parse JSON line: {line}")
        return results, None

    except Exception as e:
        logger.error(f"Error running command: {e}")
        return None, str(e)

    finally:
        await cleanup_subprocess(process, logger)


async def cleanup_subprocess(
    process: Optional[asyncio.subprocess.Process],
    logger: Optional[logging.Logger] = None,
) -> None:
    """
    Properly cleans up a subprocess to prevent asyncio transport warnings.

    Args:
        process: The subprocess to cleanup
        logger: Optional logger for debug messages
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if process is None:
        return

    try:
        # Check if process is still running
        if process.returncode is None:
            # Try to terminate gracefully first
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                # Force kill if termination doesn't work
                process.kill()
                await process.wait()

        # Explicitly close transport to prevent ResourceWarning
        if hasattr(process, "_transport") and process._transport:
            try:
                process._transport.close()
            except Exception:
                # Ignore errors during transport cleanup
                pass

    except (ProcessLookupError, asyncio.TimeoutError) as cleanup_error:
        logger.debug(f"Process cleanup warning: {cleanup_error}")
    except Exception as cleanup_error:
        logger.debug(f"Unexpected error during process cleanup: {cleanup_error}")


def setup_asyncio_windows_fixes() -> None:
    """
    Apply Windows-specific fixes for asyncio subprocess issues.

    This function should be called early in the application startup
    to prevent asyncio transport warnings on Windows.
    """
    if sys.platform == "win32":
        # Set up proper event loop policy for Windows
        if hasattr(asyncio, "WindowsProactorEventLoopPolicy"):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        # Suppress ResourceWarning for unclosed transports
        import warnings

        warnings.filterwarnings(
            "ignore",
            message="unclosed transport",
            category=ResourceWarning,
        )
