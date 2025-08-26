from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from rust_crate_pipeline.crate_analysis import CrateAnalyzer
# Import test utilities for subprocess cleanup
from tests.test_utils import get_test_logger, run_command_for_tests


@pytest.fixture
def crate_analyzer(tmpdir):
    """Provides a CrateAnalyzer instance for the tests."""
    return CrateAnalyzer(str(tmpdir))


class TestCrateAnalyzer:
    """Test CrateAnalyzer class."""

    def test_initialization(self, crate_analyzer):
        """Test CrateAnalyzer initialization."""
        assert crate_analyzer.crate_source_path is not None

    @patch("subprocess.run")
    def test_run_cargo_cmd(self, mock_run, crate_analyzer):
        """Test run_cargo_cmd method."""
        mock_run.return_value = Mock(
            stdout='{"reason": "compiler-message"}', stderr="", returncode=0
        )
        result = crate_analyzer.run_cargo_cmd(["test", "command"])
        assert "cmd" in result
        assert "returncode" in result
        assert "stdout" in result
        assert "stderr" in result

    @patch("rust_crate_pipeline.crate_analysis.CrateAnalyzer.run_cargo_cmd")
    def test_analyze(self, mock_run_cargo_cmd, crate_analyzer):
        """Test analyze method."""
        mock_run_cargo_cmd.return_value = {}
        results = crate_analyzer.analyze()
        assert "build" in results
        assert "test" in results
        assert "clippy" in results
        assert "fmt" in results
        assert "audit" in results
        assert "tree" in results
        assert "doc" in results

    @pytest.mark.asyncio
    async def test_subprocess_cleanup_integration(self, crate_analyzer):
        """Test that subprocess cleanup works with CrateAnalyzer."""
        # Mock the subprocess creation to simulate cargo commands
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(
            return_value=(b'{"reason": "compiler-message"}', b"")
        )
        mock_process._transport = Mock()

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            # Test the subprocess utility directly
            results, error = await run_command_for_tests(
                ["cargo", "check"], Path(crate_analyzer.crate_source_path)
            )

            assert error is None
            assert results == [{"reason": "compiler-message"}]

            # Verify cleanup was called
            mock_process._transport.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_subprocess_cleanup_with_logger(self, crate_analyzer):
        """Test subprocess cleanup with custom logger."""
        logger = get_test_logger("test_crate_analysis")

        # Mock the subprocess creation
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(b"", b"cargo not found"))
        mock_process._transport = Mock()

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            results, error = await run_command_for_tests(
                ["cargo", "build"], Path(crate_analyzer.crate_source_path), logger
            )

            assert error is None  # Error is logged but not returned
            assert results == []

            # Verify cleanup was called
            mock_process._transport.close.assert_called_once()
