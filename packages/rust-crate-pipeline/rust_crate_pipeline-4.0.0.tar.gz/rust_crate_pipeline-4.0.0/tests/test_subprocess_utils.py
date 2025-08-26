"""Tests for subprocess utilities."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from rust_crate_pipeline.utils.subprocess_utils import (
    cleanup_subprocess, run_command_with_cleanup, setup_asyncio_windows_fixes)


class TestSubprocessUtils:
    """Test subprocess utility functions."""

    def test_setup_asyncio_windows_fixes(self):
        """Test that Windows-specific fixes can be applied."""
        # Should not raise any exceptions
        setup_asyncio_windows_fixes()

    @pytest.mark.asyncio
    async def test_run_command_with_cleanup_success(self):
        """Test successful command execution with cleanup."""
        # Mock the subprocess creation
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b'{"test": "data"}', b""))
        mock_process._transport = Mock()

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            results, error = await run_command_with_cleanup(
                ["echo", "test"], Path.cwd()
            )

            assert error is None
            assert results == [{"test": "data"}]

            # Verify cleanup was called
            mock_process._transport.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_command_with_cleanup_failure(self):
        """Test command execution failure with cleanup."""
        # Mock the subprocess creation
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(b"", b"error message"))
        mock_process._transport = Mock()

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            results, error = await run_command_with_cleanup(
                ["nonexistent", "command"], Path.cwd()
            )

            assert error is None  # Error is logged but not returned
            assert results == []

            # Verify cleanup was called
            mock_process._transport.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_command_with_cleanup_exception(self):
        """Test command execution with exception handling."""
        with patch(
            "asyncio.create_subprocess_exec", side_effect=OSError("Command not found")
        ):
            results, error = await run_command_with_cleanup(
                ["nonexistent", "command"], Path.cwd()
            )

            assert results is None
            assert error == "Command not found"

    @pytest.mark.asyncio
    async def test_cleanup_subprocess_none(self):
        """Test cleanup with None process."""
        # Should not raise any exceptions
        await cleanup_subprocess(None)

    @pytest.mark.asyncio
    async def test_cleanup_subprocess_running(self):
        """Test cleanup of a running process."""
        mock_process = Mock()
        mock_process.returncode = None
        mock_process.terminate = Mock()
        mock_process.kill = Mock()
        mock_process.wait = AsyncMock()
        mock_process._transport = Mock()

        await cleanup_subprocess(mock_process)

        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called()
        mock_process._transport.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_subprocess_timeout(self):
        """Test cleanup with timeout."""
        mock_process = Mock()
        mock_process.returncode = None
        mock_process.terminate = Mock()
        mock_process.kill = Mock()
        # First wait call times out, second succeeds
        mock_process.wait = AsyncMock(side_effect=[asyncio.TimeoutError(), None])
        mock_process._transport = Mock()

        await cleanup_subprocess(mock_process)

        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()
        assert mock_process.wait.call_count == 2  # Called twice
        mock_process._transport.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_subprocess_no_transport(self):
        """Test cleanup of process without transport."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process._transport = None

        # Should not raise any exceptions
        await cleanup_subprocess(mock_process)

    @pytest.mark.asyncio
    async def test_cleanup_subprocess_transport_error(self):
        """Test cleanup with transport error."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process._transport = Mock()
        mock_process._transport.close.side_effect = Exception("Transport error")

        # Should not raise any exceptions
        await cleanup_subprocess(mock_process)
