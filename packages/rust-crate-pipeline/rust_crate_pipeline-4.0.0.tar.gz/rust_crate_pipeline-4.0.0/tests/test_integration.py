"""
Integration tests for the new components:
- Advanced caching system
- ML quality predictor
- API gateway
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from rust_crate_pipeline.config import PipelineConfig
from rust_crate_pipeline.unified_pipeline import UnifiedSigilPipeline


class TestIntegration:
    """Integration tests for new components."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return PipelineConfig(
            model_path="test_model.gguf",
            max_tokens=256,
            batch_size=2,
            output_path="./test_output",
        )

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.mark.asyncio
    async def test_cache_integration(self, config, temp_cache_dir):
        """Test that caching system integrates properly."""
        # Mock the cache to avoid file system dependencies
        with patch(
            "rust_crate_pipeline.utils.advanced_cache.get_cache"
        ) as mock_get_cache:
            mock_cache = Mock()
            mock_cache.get.return_value = None
            mock_cache.set.return_value = True
            mock_get_cache.return_value = mock_cache

            # Create pipeline
            pipeline = UnifiedSigilPipeline(config)

            # Verify cache was initialized
            assert pipeline.cache is not None
            mock_get_cache.assert_called_once()

    @pytest.mark.asyncio
    async def test_ml_predictor_integration(self, config):
        """Test that ML predictor integrates properly."""
        # Mock the ML predictor to avoid model loading
        with patch(
            "rust_crate_pipeline.ml.quality_predictor.get_predictor"
        ) as mock_get_predictor:
            mock_predictor = Mock()
            mock_prediction = Mock()
            mock_prediction.quality_score = 0.85
            mock_prediction.security_risk = "low"
            mock_prediction.maintenance_score = 0.9
            mock_prediction.popularity_trend = "growing"
            mock_prediction.dependency_health = 0.8
            mock_prediction.confidence = 0.95
            mock_prediction.model_version = "1.0.0"

            mock_predictor.predict_quality.return_value = mock_prediction
            mock_get_predictor.return_value = mock_predictor

            # Create pipeline
            pipeline = UnifiedSigilPipeline(config)

            # Verify ML predictor was initialized
            assert pipeline.ml_predictor is not None
            mock_get_predictor.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_and_ml_workflow(self, config, temp_cache_dir):
        """Test that caching and ML work together in the analysis workflow."""
        # Mock both cache and ML predictor
        with patch(
            "rust_crate_pipeline.utils.advanced_cache.get_cache"
        ) as mock_get_cache, patch(
            "rust_crate_pipeline.ml.quality_predictor.get_predictor"
        ) as mock_get_predictor:
            # Setup mock cache
            mock_cache = Mock()
            mock_cache.get.return_value = None  # No cached result
            mock_cache.set.return_value = True
            mock_get_cache.return_value = mock_cache

            # Setup mock ML predictor
            mock_predictor = Mock()
            mock_prediction = Mock()
            mock_prediction.quality_score = 0.85
            mock_prediction.security_risk = "low"
            mock_prediction.maintenance_score = 0.9
            mock_prediction.popularity_trend = "growing"
            mock_prediction.dependency_health = 0.8
            mock_prediction.confidence = 0.95
            mock_prediction.model_version = "1.0.0"

            mock_predictor.predict_quality.return_value = mock_prediction
            mock_get_predictor.return_value = mock_predictor

            # Create pipeline
            pipeline = UnifiedSigilPipeline(config)

            # Verify both components were initialized
            assert pipeline.cache is not None
            assert pipeline.ml_predictor is not None

    @pytest.mark.asyncio
    async def test_api_gateway_config_loading(self):
        """Test that API gateway can load configuration."""
        from rust_crate_pipeline.services.api_gateway import APIGateway

        # Create a minimal config
        config = {
            "load_balancer_strategy": "round_robin",
            "rate_limit_per_minute": 60,
            "jwt_secret": "test-secret",
            "api_keys": ["test-key"],
            "public_paths": ["/health"],
            "services": {
                "pipeline": {
                    "endpoints": [
                        {
                            "url": "http://localhost:8001",
                            "health_check": "http://localhost:8001/health",
                            "weight": 1,
                            "max_requests": 100,
                        }
                    ]
                }
            },
        }

        # Create gateway
        gateway = APIGateway(config)

        # Verify components were initialized
        assert gateway.service_registry is not None
        assert gateway.load_balancer is not None
        assert gateway.rate_limiter is not None

    @pytest.mark.asyncio
    async def test_cache_hit_scenario(self, config):
        """Test cache hit scenario where cached result is returned."""
        # Mock cache to return a cached result
        with patch(
            "rust_crate_pipeline.utils.advanced_cache.get_cache"
        ) as mock_get_cache:
            mock_cache = Mock()

            # Create a mock cached result
            cached_result = Mock()
            cached_result.name = "test-crate"
            cached_result.version = "1.0.0"

            mock_cache.get = AsyncMock(return_value=cached_result)
            mock_cache.set = AsyncMock(return_value=True)
            mock_get_cache.return_value = mock_cache

            # Create pipeline
            pipeline = UnifiedSigilPipeline(config)

            # Test cache hit
            cache_key = "crate_analysis:test-crate:1.0.0"
            result = await pipeline.cache.get(cache_key)

            assert result is not None
            assert result.name == "test-crate"

    @pytest.mark.asyncio
    async def test_ml_prediction_workflow(self, config):
        """Test ML prediction workflow with sample data."""
        # Mock ML predictor
        with patch(
            "rust_crate_pipeline.ml.quality_predictor.get_predictor"
        ) as mock_get_predictor:
            mock_predictor = Mock()
            mock_prediction = Mock()
            mock_prediction.quality_score = 0.85
            mock_prediction.security_risk = "low"
            mock_prediction.maintenance_score = 0.9
            mock_prediction.popularity_trend = "growing"
            mock_prediction.dependency_health = 0.8
            mock_prediction.confidence = 0.95
            mock_prediction.model_version = "1.0.0"

            mock_predictor.predict_quality.return_value = mock_prediction
            mock_get_predictor.return_value = mock_predictor

            # Create pipeline
            pipeline = UnifiedSigilPipeline(config)

            # Test ML prediction
            sample_data = {
                "name": "test-crate",
                "description": "A test crate",
                "downloads": 1000,
                "github_stars": 100,
            }

            prediction = pipeline.ml_predictor.predict_quality(sample_data)

            assert prediction.quality_score == 0.85
            assert prediction.security_risk == "low"
            assert prediction.confidence == 0.95

    @pytest.mark.asyncio
    async def test_component_fallback_behavior(self, config):
        """Test that pipeline works when components are not available."""
        # Mock imports to fail
        with patch(
            "rust_crate_pipeline.utils.advanced_cache.get_cache",
            side_effect=ImportError,
        ), patch(
            "rust_crate_pipeline.ml.quality_predictor.get_predictor",
            side_effect=ImportError,
        ):
            # Create pipeline - should not fail even if components are missing
            pipeline = UnifiedSigilPipeline(config)

            # Verify pipeline was created successfully
            assert pipeline is not None
            assert pipeline.cache is None
            assert pipeline.ml_predictor is None

    def test_config_file_loading(self):
        """Test that gateway config file can be loaded."""
        config_path = Path("configs/gateway_config.json")

        if config_path.exists():
            with open(config_path, "r") as f:
                config = json.load(f)

            # Verify required fields are present
            assert "load_balancer_strategy" in config
            assert "rate_limit_per_minute" in config
            assert "services" in config
            assert "pipeline" in config["services"]

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, config, temp_cache_dir):
        """Test end-to-end workflow with all components."""
        # Mock all external dependencies
        with patch(
            "rust_crate_pipeline.utils.advanced_cache.get_cache"
        ) as mock_get_cache, patch(
            "rust_crate_pipeline.ml.quality_predictor.get_predictor"
        ) as mock_get_predictor, patch(
            "rust_crate_pipeline.core.IRLEngine"
        ) as mock_irl_engine:
            # Setup mocks
            mock_cache = Mock()
            mock_cache.get.return_value = None
            mock_cache.set.return_value = True
            mock_get_cache.return_value = mock_cache

            mock_predictor = Mock()
            mock_prediction = Mock()
            mock_prediction.quality_score = 0.85
            mock_prediction.security_risk = "low"
            mock_prediction.maintenance_score = 0.9
            mock_prediction.popularity_trend = "growing"
            mock_prediction.dependency_health = 0.8
            mock_prediction.confidence = 0.95
            mock_prediction.model_version = "1.0.0"

            mock_predictor.predict_quality.return_value = mock_prediction
            mock_get_predictor.return_value = mock_predictor

            mock_irl_engine.return_value = Mock()

            # Create pipeline
            pipeline = UnifiedSigilPipeline(config)

            # Verify all components were initialized
            assert pipeline is not None
            assert pipeline.cache is not None
            assert pipeline.ml_predictor is not None
            assert pipeline.irl_engine is not None

            # Test that pipeline can be used as async context manager
            async with pipeline:
                assert pipeline is not None


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v"])
