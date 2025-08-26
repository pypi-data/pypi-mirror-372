from __future__ import annotations

import argparse
import asyncio
import gzip
import json
import logging
import os
import tarfile
import tempfile
import time
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

# Suppress Windows-specific asyncio resource warnings
if os.name == "nt":  # Windows
    warnings.filterwarnings("ignore", category=ResourceWarning, module="asyncio")

import aiohttp

from rust_crate_pipeline.utils.sanitization import Sanitizer
from rust_crate_pipeline.version import __version__

try:
    from utils.serialization_utils import to_serializable
except ImportError:
    # Fallback for when utils is not available as a top-level module
    from rust_crate_pipeline.utils.serialization_utils import to_serializable

from pydantic import ValidationError

from .config import CrateMetadata, PipelineConfig
from .core import CanonRegistry, IRLEngine, SacredChainTrace, TrustVerdict
from .crate_analysis import CrateAnalyzer
from .exceptions import PipelineError, SecurityException
from .schemas import DocumentationResults
from .scraping import ScrapingResult, UnifiedScraper
from .utils.subprocess_utils import (run_command_with_cleanup,
                                     setup_asyncio_windows_fixes)

# Import Azure OpenAI enricher if available
# Azure OpenAI support is now handled through UnifiedLLMProcessor
AZURE_OPENAI_AVAILABLE = True

# Set up Windows-specific asyncio fixes
setup_asyncio_windows_fixes()

# Import unified LLM processor
try:
    from .llm_client import LLMConfig
    from .llm_factory import create_llm_client_from_config
    from .unified_llm_processor import UnifiedLLMProcessor

    UNIFIED_LLM_AVAILABLE = True
except ImportError:
    UNIFIED_LLM_AVAILABLE = False
    UnifiedLLMProcessor = None
    create_llm_client_from_config = None
    LLMConfig = None

# Import advanced caching system
try:
    from .utils import advanced_cache

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    advanced_cache = None

# Import ML quality predictor
try:
    from .ml import quality_predictor

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    quality_predictor = None

if TYPE_CHECKING:
    # Azure OpenAI support is now handled through UnifiedLLMProcessor
    from .llm_client import LLMConfig
    from .unified_llm_processor import UnifiedLLMProcessor


class UnifiedSigilPipeline:
    def __init__(
        self, config: PipelineConfig, llm_config: Optional[Any] = None
    ) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.irl_engine: Optional[IRLEngine] = None
        self.scraper: Optional[UnifiedScraper] = None
        self.canon_registry: CanonRegistry = CanonRegistry()
        self.sanitizer = Sanitizer(enabled=False)

        # Initialize AI components
        self.ai_enricher: Optional[Any] = None
        self.unified_llm_processor: Optional[Any] = None
        self.crate_analyzer: Optional[CrateAnalyzer] = None

        # Initialize advanced components
        self.cache: Optional[Any] = None
        self.ml_predictor: Optional[Any] = None

        # Store LLM config for later use
        self.llm_config = llm_config

        self._initialize_components()

    def _initialize_components(self) -> None:
        try:
            self.irl_engine = IRLEngine(self.config, self.canon_registry)
            self.logger.info("✅ IRL Engine initialized successfully")

            # Initialize scraper
            try:
                self.scraper = UnifiedScraper()
                self.logger.info("✅ Unified Scraper initialized successfully")
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to initialize scraper: {e}")

            # Initialize unified LLM processor if available
            if UNIFIED_LLM_AVAILABLE:
                try:
                    if self.llm_config:
                        self.unified_llm_processor = UnifiedLLMProcessor(
                            self.llm_config
                        )
                        self.logger.info(
                            "✅ Unified LLM Processor initialized successfully"
                        )
                    else:
                        self.logger.warning(
                            "⚠️  UnifiedLLMProcessor is None at runtime; "
                            "skipping initialization."
                        )
                except Exception as e:
                    self.logger.warning(
                        f"⚠️  Failed to initialize Unified LLM Processor: {e}"
                    )

            # Initialize Azure OpenAI enricher if available and configured
            # (fallback)
            elif AZURE_OPENAI_AVAILABLE and self.config.use_azure_openai:
                try:
                    # Initialize unified LLM enricher (handles all providers)
                    from .ai_processing import LLMEnricher

                    self.ai_enricher = LLMEnricher(self.config)
                    self.logger.info("✅ Unified LLM enricher initialized successfully")
                except Exception as e:
                    self.logger.warning(
                        f"⚠️  Failed to initialize Azure OpenAI Enricher: {e}"
                    )

            # Initialize advanced caching system
            if CACHE_AVAILABLE and advanced_cache is not None:
                try:
                    self.cache = advanced_cache.get_cache()
                    self.logger.info("✅ Advanced caching system initialized")
                except Exception as e:
                    self.logger.warning(f"⚠️  Failed to initialize cache: {e}")

            # Initialize ML quality predictor
            if ML_AVAILABLE and quality_predictor is not None:
                try:
                    self.ml_predictor = quality_predictor.get_predictor()
                    self.logger.info("✅ ML quality predictor initialized")
                except Exception as e:
                    self.logger.warning(f"⚠️  Failed to initialize ML predictor: {e}")

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize pipeline components: {e}")
            raise

    async def __aenter__(self) -> "UnifiedSigilPipeline":
        if self.irl_engine:
            await self.irl_engine.__aenter__()
        # Don't start scraper here - will be created per task
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        if self.irl_engine:
            await self.irl_engine.__aexit__(exc_type, exc_val, exc_tb)
        # Scraper cleanup is handled per task

    async def analyze_crate(
        self, crate_name: str, crate_version: Optional[str] = None
    ) -> SacredChainTrace:
        if not crate_name or not isinstance(crate_name, str):
            raise ValueError("crate_name must be a non-empty string")

        self.logger.info(f"🔍 Starting analysis of crate: {crate_name}")

        try:
            if crate_version is None:
                crate_version = await self._get_latest_crate_version(crate_name)
                if not crate_version:
                    raise RuntimeError(
                        f"Could not determine latest version for {crate_name}"
                    )

            # Create a new scraper instance for this task to avoid browser context conflicts
            scraper_config = {
                "verbose": False,
                "word_count_threshold": 10,
                "crawl_config": {},
            }

            # Check cache first
            cache_key = f"crate_analysis:{crate_name}:{crate_version}"
            if self.cache:
                cached_result = self.cache.get(cache_key)
                if asyncio.iscoroutine(cached_result):
                    cached_result = await cached_result
                if cached_result:
                    self.logger.info(f"📦 Using cached analysis for {crate_name}")
                    return cached_result

            async with UnifiedScraper(scraper_config) as scraper:
                # Fetch crate metadata to get repository URL
                crate_metadata = await self._fetch_crate_metadata(crate_name)

                documentation_results = await self._gather_documentation(
                    crate_name, scraper, crate_metadata
                )

                sacred_chain_trace = await self._perform_sacred_chain_analysis(
                    crate_name, crate_version, documentation_results
                )

                # Add ML predictions if available
                if self.ml_predictor:
                    ml_predictions = await self._add_ml_predictions(
                        crate_name, sacred_chain_trace
                    )
                    sacred_chain_trace.audit_info["ml_predictions"] = ml_predictions

                # Cache the result
                if self.cache:
                    result = self.cache.set(
                        cache_key,
                        sacred_chain_trace,
                        ttl=3600,
                        tags=["crate_analysis", crate_name],
                    )
                    if asyncio.iscoroutine(result):
                        await result

                await self._generate_analysis_report(crate_name, sacred_chain_trace)

                self.logger.info(f"✅ Analysis completed for {crate_name}")
                return sacred_chain_trace

        except Exception as e:
            self.logger.error(f"❌ Analysis failed for {crate_name}: {e}")
            raise RuntimeError(f"Analysis failed for {crate_name}: {str(e)}")

    async def _add_ml_predictions(
        self, crate_name: str, sacred_chain_trace: SacredChainTrace
    ) -> Dict[str, Any]:
        """Add ML predictions to the analysis."""
        if not self.ml_predictor:
            return {}

        try:
            # Extract crate data from sacred chain trace
            crate_data = {
                "name": crate_name,
                "description": sacred_chain_trace.suggestion,
                "context_sources": sacred_chain_trace.context_sources,
                "reasoning_steps": sacred_chain_trace.reasoning_steps,
                "irl_score": sacred_chain_trace.irl_score,
                "audit_info": sacred_chain_trace.audit_info,
            }

            # Get ML predictions
            prediction = self.ml_predictor.predict_quality(crate_data)

            return {
                "quality_score": prediction.quality_score,
                "security_risk": prediction.security_risk,
                "maintenance_score": prediction.maintenance_score,
                "popularity_trend": prediction.popularity_trend,
                "dependency_health": prediction.dependency_health,
                "confidence": prediction.confidence,
                "model_version": prediction.model_version,
            }

        except Exception as e:
            self.logger.warning(f"⚠️  ML prediction failed for {crate_name}: {e}")
            return {}

    async def _fetch_crate_metadata(self, crate_name: str) -> Optional[Dict[str, Any]]:
        """Fetch crate metadata from crates.io API to get repository URL"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                url = f"https://crates.io/api/v1/crates/{crate_name}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        crate_info = data.get("crate", {})
                        return {
                            "name": crate_info.get("name"),
                            "repository": crate_info.get("repository"),
                            "description": crate_info.get("description"),
                            "homepage": crate_info.get("homepage"),
                            "documentation": crate_info.get("documentation"),
                            "keywords": crate_info.get("keywords", []),
                            "categories": crate_info.get("categories", []),
                            "max_version": crate_info.get("max_version"),
                            "created_at": crate_info.get("created_at"),
                            "updated_at": crate_info.get("updated_at"),
                        }
                    else:
                        self.logger.warning(
                            f"Failed to fetch crate metadata for {crate_name}: HTTP {response.status}"
                        )
                        return None
        except Exception as e:
            self.logger.error(f"Error fetching crate metadata for {crate_name}: {e}")
            return None

    async def _gather_documentation(
        self,
        crate_name: str,
        scraper: UnifiedScraper,
        crate_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, ScrapingResult]:
        if not scraper:
            raise RuntimeError("Scraper not initialized")

        self.logger.info(f"📚 Gathering documentation for {crate_name}")

        try:
            # Get repository URL from crate metadata if available
            repository_url = None
            if crate_metadata:
                repository_url = crate_metadata.get("repository")
                if repository_url:
                    self.logger.info(
                        f"🔗 Found repository URL for {crate_name}: {repository_url}"
                    )
                else:
                    self.logger.info(f"ℹ️  No repository URL found for {crate_name}")

            # Call scraper with repository URL for GitHub integration
            results = await scraper.scrape_crate_documentation(
                crate_name, repository_url
            )

            successful_sources = [
                source
                for source, result in results.items()
                if result is not None and result.error is None
            ]
            failed_sources = [
                source
                for source, result in results.items()
                if result is None or result.error is not None
            ]

            self.logger.info(
                f"✅ Successfully scraped {len(successful_sources)} sources: {successful_sources}"
            )
            if failed_sources:
                self.logger.warning(
                    f"⚠️  Failed to scrape {len(failed_sources)} sources: {failed_sources}"
                )

            return results

        except Exception as e:
            self.logger.error(f"❌ Documentation gathering failed: {e}")
            raise

    async def _perform_sacred_chain_analysis(
        self,
        crate_name: str,
        crate_version: str,
        documentation_results: Dict[str, ScrapingResult],
    ) -> SacredChainTrace:
        if not self.irl_engine:
            raise RuntimeError("IRL Engine not initialized")

        self.logger.info(f"🔗 Performing Sacred Chain analysis for {crate_name}")

        try:
            # Convert dataclass ScrapingResult objects to dictionaries for validation
            # The DocumentationResults model expects Pydantic ScrapingResult objects
            converted_results = {}
            for source, result in documentation_results.items():
                if result is None:
                    converted_results[source] = None
                else:
                    # Convert dataclass to dict format expected by Pydantic model
                    converted_results[source] = {
                        "url": result.url,
                        "content": result.content,
                        "error": result.error,
                        "status_code": None,  # Not available in dataclass version
                    }

            # Validate the documentation results
            try:
                validated_docs = DocumentationResults.model_validate(converted_results)
            except ValidationError as e:
                # Provide specific error context about which fields failed validation
                error_details = []
                for error in e.errors():
                    field_path = " -> ".join(str(loc) for loc in error["loc"])
                    error_type = error["type"]
                    error_msg = error["msg"]
                    error_details.append(
                        f"Field '{field_path}': {error_type} - {error_msg}"
                    )

                error_summary = "; ".join(error_details)
                self.logger.error(
                    f"Documentation results validation failed: {error_summary}"
                )
                raise PipelineError(
                    f"Documentation results validation failed: {error_summary}"
                )

            sanitized_docs = self.sanitizer.sanitize_data(validated_docs.model_dump())

            async with self.irl_engine as irl_engine:
                trace = await irl_engine.analyze_with_sacred_chain(crate_name)

            # Storing sanitized docs in the trace for later use by enrichment
            # functions
            trace.audit_info["sanitized_documentation"] = sanitized_docs

            await self._add_crate_analysis_results(crate_name, crate_version, trace)

            if self.unified_llm_processor:
                await self._add_unified_llm_enrichment(crate_name, crate_version, trace)
            elif self.ai_enricher:
                await self._add_ai_enrichment(crate_name, crate_version, trace)

            return trace

        except Exception as e:
            self.logger.error(f"❌ Sacred Chain analysis failed: {e}")
            raise

    async def _handle_toolchain_override(
        self, crate_source_path: Path
    ) -> Optional[Path]:
        """
        Handle rust-toolchain files that might override to incompatible versions.
        Returns the path of the backed up file if one was found, None otherwise.
        """
        toolchain_files = [
            crate_source_path / "rust-toolchain.toml",
            crate_source_path / "rust-toolchain",
        ]

        for toolchain_file in toolchain_files:
            if toolchain_file.exists():
                self.logger.info(f"Found toolchain override file: {toolchain_file}")
                # Backup the file by renaming it
                backup_path = toolchain_file.with_suffix(
                    toolchain_file.suffix + ".backup"
                )
                try:
                    toolchain_file.rename(backup_path)
                    self.logger.info(
                        f"Temporarily disabled toolchain override: "
                        f"{toolchain_file} -> {backup_path}"
                    )
                    return backup_path
                except Exception as e:
                    self.logger.warning(
                        f"Failed to backup toolchain file {toolchain_file}: {e}"
                    )

        return None

    async def _restore_toolchain_override(self, backup_path: Optional[Path]) -> None:
        """Restore a backed up rust-toolchain file."""
        if backup_path and backup_path.exists():
            try:
                original_path = backup_path.with_suffix(
                    backup_path.suffix.replace(".backup", "")
                )
                backup_path.rename(original_path)
                self.logger.info(
                    f"Restored toolchain override: {backup_path} -> {original_path}"
                )
            except Exception as e:
                self.logger.warning(
                    f"Failed to restore toolchain file {backup_path}: {e}"
                )

    async def _add_crate_analysis_results(
        self, crate_name: str, crate_version: str, trace: SacredChainTrace
    ) -> None:
        """Add crate analysis results to the sacred chain trace"""
        try:
            if trace.audit_info.get("should_analyze_source_code", True):
                self.logger.info(
                    f"🔍 Adding crate analysis results for {crate_name} v{crate_version}"
                )

                crate_source_path = await self._download_and_extract_crate(
                    crate_name, crate_version, Path(tempfile.mkdtemp())
                )

                if not crate_source_path:
                    trace.audit_info["crate_analysis"] = {
                        "status": "error",
                        "note": "Failed to download or extract crate.",
                    }
                    return

                # Handle toolchain overrides that might cause compatibility issues
                backup_path = await self._handle_toolchain_override(crate_source_path)

                try:
                    # Use enhanced crate analysis with additional tools and insights
                    from .crate_analysis import CrateAnalyzer

                    analyzer = CrateAnalyzer(str(crate_source_path))
                    analysis_results = analyzer.analyze()

                    # Also run individual commands for backward compatibility
                    check_results, check_error = await self._run_command(
                        ["cargo", "+stable", "check", "--message-format=json"],
                        cwd=crate_source_path,
                    )
                    clippy_results, clippy_error = await self._run_command(
                        ["cargo", "+stable", "clippy", "--message-format=json"],
                        cwd=crate_source_path,
                    )
                    audit_results, audit_error = await self._run_command(
                        ["cargo", "+stable", "audit", "--json"], cwd=crate_source_path
                    )

                    trace.audit_info["crate_analysis"] = self.sanitizer.sanitize_data(
                        {
                            "status": "completed",
                            "enhanced_analysis": analysis_results,
                            "check": check_results,
                            "check_error": check_error,
                            "clippy": clippy_results,
                            "clippy_error": clippy_error,
                            "audit": audit_results,
                            "audit_error": audit_error,
                            "note": "Enhanced crate analysis performed with additional tools and insights.",
                        }
                    )

                finally:
                    # Restore any backed up toolchain file
                    await self._restore_toolchain_override(backup_path)

        except Exception as e:
            self.logger.warning(f"⚠️  Failed to add crate analysis results: {e}")
            trace.audit_info["crate_analysis"] = {"status": "error", "note": str(e)}

    async def _download_and_extract_crate(
        self, crate_name: str, crate_version: str, target_dir: Path
    ) -> Optional[Path]:
        """Downloads and extracts a crate from crates.io."""
        crate_url = (
            f"https://static.crates.io/crates/{crate_name}/"
            f"{crate_name}-{crate_version}.crate"
        )
        try:
            # Create SSL context that works with Windows
            import ssl

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            connector = aiohttp.TCPConnector(ssl=ssl_context)
            timeout = aiohttp.ClientTimeout(total=60)  # Longer timeout for downloads

            async with aiohttp.ClientSession(
                connector=connector, timeout=timeout
            ) as session:
                async with session.get(crate_url) as response:
                    if response.status != 200:
                        self.logger.error(
                            f"Failed to download {crate_url}: HTTP {response.status}"
                        )
                        return None

                    # Save the .crate file
                    crate_file_path = target_dir / f"{crate_name}-{crate_version}.crate"
                    with open(crate_file_path, "wb") as f:
                        f.write(await response.read())

                    # Extract the tarball
                    with gzip.open(crate_file_path, "rb") as gz_file:
                        with tarfile.open(fileobj=gz_file, mode="r") as tar_file:
                            for member in tar_file.getmembers():
                                member_path = os.path.join(target_dir, member.name)
                                if not os.path.abspath(member_path).startswith(
                                    os.path.abspath(target_dir)
                                ):
                                    raise SecurityException(
                                        f"Attempted path traversal in tar file: "
                                        f"{member.name}"
                                    )
                            tar_file.extractall(path=target_dir)

                    # The crate is usually extracted into a directory named
                    # `{crate_name}-{crate_version}`
                    crate_source_dir = target_dir / f"{crate_name}-{crate_version}"
                    if crate_source_dir.is_dir():
                        return crate_source_dir
                    else:
                        self.logger.error(
                            f"Could not find extracted directory: {crate_source_dir}"
                        )
                        return None

        except Exception as e:
            self.logger.warning(
                f"Could not download crate source for {crate_name}: {e}"
            )
            self.logger.info(
                "This is optional - web scraping analysis will continue without source code"
            )
            return None

    async def _get_latest_crate_version(self, crate_name: str) -> Optional[str]:
        """Fetches the latest version of a crate from crates.io API."""
        api_url = f"https://crates.io/api/v1/crates/{crate_name}"
        try:
            # Use requests instead of aiohttp since it works on this system
            import requests

            response = requests.get(api_url, timeout=30)
            if response.status_code != 200:
                self.logger.error(
                    f"Failed to fetch crate info from {api_url}: HTTP {response.status_code}"
                )
                return None
            data = response.json()
            return data.get("crate", {}).get("max_version")
        except Exception as e:
            self.logger.error(
                f"Error fetching latest crate version for {crate_name}: {e}"
            )
            return None

    async def _run_command(
        self, command: List[str], cwd: Path
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """Runs a command and returns the parsed JSON output and any errors."""
        return await run_command_with_cleanup(command, cwd, self.logger)

    async def _add_ai_enrichment(
        self, crate_name: str, crate_version: str, trace: SacredChainTrace
    ) -> None:
        """Add AI enrichment results to the sacred chain trace"""
        # Use unified LLM processor if available, otherwise fall back to Azure
        # OpenAI
        if self.unified_llm_processor:
            await self._add_unified_llm_enrichment(crate_name, crate_version, trace)
        elif self.ai_enricher:
            await self._add_azure_openai_enrichment(crate_name, trace)
        else:
            self.logger.info("ℹ️  No AI enricher available, skipping AI enrichment")

    async def _add_unified_llm_enrichment(
        self, crate_name: str, crate_version: str, trace: SacredChainTrace
    ) -> None:
        """Add enrichment using unified LLM processor"""
        if not self.unified_llm_processor:
            return

        try:
            self.logger.info(f"🤖 Adding unified LLM enrichment for {crate_name}")

            # Get scraped data from trace
            scraped_data = trace.audit_info.get("sanitized_documentation", {})
            crates_io_data = scraped_data.get("crates.io", {}).get("data", {})

            # Extract README content from multiple sources
            readme_content = self._extract_readme_content(scraped_data)

            crate_metadata = CrateMetadata(
                name=crate_name,
                version=crate_version,
                description=crates_io_data.get(
                    "description", trace.suggestion or "No description available"
                ),
                repository=crates_io_data.get("repository", ""),
                keywords=crates_io_data.get("keywords", []),
                categories=crates_io_data.get("categories", []),
                readme=readme_content,  # ✅ Fixed: now uses extracted content
                downloads=crates_io_data.get("downloads", 0),
                github_stars=0,  # This would ideally come from a GitHub specific scrape
                dependencies=crates_io_data.get("dependencies", []),
                features=crates_io_data.get("features", {}),
                code_snippets=[],
                readme_sections={},
                librs_downloads=scraped_data.get("librs.org", {})
                .get("data", {})
                .get("downloads_total", None),
                source="crates.io",
                enhanced_scraping={},
                enhanced_features=[],
                enhanced_dependencies=[],
            )

            # Store the metadata used for enrichment
            trace.audit_info["crate_metadata"] = crate_metadata.to_dict()

            # Enrich the crate using unified LLM processor
            enriched_crate = await self.unified_llm_processor.process_crate(
                crate_metadata
            )

            # Add enrichment results to trace - handle different return types safely
            if hasattr(enriched_crate, "to_dict"):
                trace.audit_info["enriched_crate"] = self.sanitizer.sanitize_data(
                    enriched_crate.to_dict()
                )
            elif isinstance(enriched_crate, dict):
                trace.audit_info["enriched_crate"] = self.sanitizer.sanitize_data(
                    enriched_crate
                )
            else:
                # Convert object to dict using vars() or dataclass fields
                try:
                    if hasattr(enriched_crate, "__dict__"):
                        trace.audit_info[
                            "enriched_crate"
                        ] = self.sanitizer.sanitize_data(vars(enriched_crate))
                    else:
                        trace.audit_info["enriched_crate"] = {
                            "enrichment_status": "completed",
                            "type": str(type(enriched_crate)),
                        }
                except Exception as serialization_error:
                    self.logger.warning(
                        f"Could not serialize enriched crate: {serialization_error}"
                    )
                    trace.audit_info["enriched_crate"] = {
                        "enrichment_status": "completed_but_not_serializable"
                    }

            self.logger.info(f"✅ Enriched data for {crate_name} using Unified LLM")

        except Exception as e:
            self.logger.warning(f"⚠️  Failed to add unified LLM enrichment: {e}")

    def _extract_readme_content(self, scraped_data: Dict[str, Any]) -> str:
        """Extract the best available README content from scraped data"""
        # Priority order: docs.rs (most comprehensive) > lib.rs > crates.io
        sources_priority = ["docs_rs", "lib_rs", "crates_io"]

        for source in sources_priority:
            source_result = scraped_data.get(source)
            if not source_result or source_result.error:
                continue

            # Access content directly from ScrapingResult object
            readme_text = source_result.content
            if (
                readme_text
                and isinstance(readme_text, str)
                and len(readme_text.strip()) > 100
            ):
                self.logger.info(
                    f"📖 Using README content from {source} ({len(readme_text)} chars)"
                )
                return readme_text

        # Fallback: concatenate all available content
        combined_content = ""
        for source in sources_priority:
            source_result = scraped_data.get(source)
            if source_result and not source_result.error:
                content = source_result.content
                if content:
                    combined_content += f"\n\n## From {source}\n{content}"

        if combined_content.strip():
            self.logger.info(
                f"📖 Using combined README content ({len(combined_content)} chars)"
            )
            return combined_content.strip()

        self.logger.warning("📖 No README content found in scraped data")
        return ""

    async def _add_azure_openai_enrichment(
        self, crate_name: str, trace: SacredChainTrace
    ) -> None:
        """Add enrichment using Azure OpenAI"""
        if not self.ai_enricher:
            return

        try:
            self.logger.info(f"🤖 Adding Azure OpenAI enrichment for {crate_name}")

            # Get scraped data from trace
            scraped_data = trace.audit_info.get("sanitized_documentation", {})
            crates_io_data = scraped_data.get("crates.io", {}).get("data", {})

            # Extract README content from multiple sources
            readme_content = self._extract_readme_content(scraped_data)

            crate_metadata = CrateMetadata(
                name=crate_name,
                version="unknown",
                description=crates_io_data.get(
                    "description", trace.suggestion or "No description available"
                ),
                repository=crates_io_data.get("repository", ""),
                keywords=crates_io_data.get("keywords", []),
                categories=crates_io_data.get("categories", []),
                readme=readme_content,  # ✅ Fixed: now uses extracted content
                downloads=crates_io_data.get("downloads", 0),
                github_stars=0,  # This would ideally come from a GitHub specific scrape
                dependencies=crates_io_data.get("dependencies", []),
                features=crates_io_data.get("features", {}),
                code_snippets=[],
                readme_sections={},
                librs_downloads=scraped_data.get("librs.org", {})
                .get("data", {})
                .get("downloads_total", None),
                source="crates.io",
                enhanced_scraping={},
                enhanced_features=[],
                enhanced_dependencies=[],
            )

            # Store the metadata used for enrichment
            trace.audit_info["crate_metadata"] = crate_metadata.to_dict()

            # Enrich the crate using Azure OpenAI
            enriched_crate = self.ai_enricher.enrich_crate(crate_metadata)

            # Add enrichment results to trace
            trace.audit_info["enriched_crate"] = self.sanitizer.sanitize_data(
                enriched_crate.to_dict()
            )
            self.logger.info(f"✅ Enriched data for {crate_name} using Azure OpenAI")

        except Exception as e:
            self.logger.warning(f"⚠️  Failed to add Azure OpenAI enrichment: {e}")

    async def _generate_analysis_report(
        self, crate_name: str, trace: SacredChainTrace
    ) -> None:
        """Generate analysis report and save to file"""
        try:
            self.logger.info(f"📊 Generating analysis report for {crate_name}")

            # Ensure the output directory exists
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)

            report_path = output_dir / f"{crate_name}_analysis_report.json"

            report_data = to_serializable(trace.to_dict())

            # Manually handle MarkdownGenerationResult
            enrichment_path = report_data.get("audit_info", {}).get("llm_enrichment")
            if enrichment_path is not None and not isinstance(
                enrichment_path, (dict, list, str, int, float, bool, type(None))
            ):
                # Fallback: convert to string to guarantee JSON serialization
                report_data["audit_info"]["llm_enrichment"] = str(enrichment_path)

            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=4, default=str)

            self.logger.info(f"📊 Analysis report generated at {report_path}")

        except Exception as e:
            self.logger.error(
                f"❌ Failed to generate analysis report for {crate_name}: {e}"
            )

    async def analyze_multiple_crates(
        self, crate_names: List[str]
    ) -> Dict[str, SacredChainTrace]:
        if not crate_names:
            return {}

        self.logger.info(f"🚀 Starting concurrent analysis of {len(crate_names)} crates")

        semaphore = asyncio.Semaphore(self.config.n_workers)

        async def analyze_single_crate(
            crate_name: str,
        ) -> "tuple[str, SacredChainTrace]":
            async with semaphore:
                try:
                    trace = await self.analyze_crate(crate_name)
                    return crate_name, trace
                except Exception as e:
                    self.logger.error(f"❌ Analysis failed for {crate_name}: {e}")
                    error_trace = SacredChainTrace(
                        input_data=crate_name,
                        context_sources=[],
                        reasoning_steps=[f"Analysis failed: {str(e)}"],
                        suggestion="DEFER: Analysis failed",
                        verdict=TrustVerdict.DEFER,
                        audit_info={"error": str(e)},
                        irl_score=0.0,
                        execution_id=f"error-{int(time.time())}",
                        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        canon_version=__version__,
                    )
                    return crate_name, error_trace

        tasks = [analyze_single_crate(name) for name in crate_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        analysis_results: Dict[str, SacredChainTrace] = {}
        for result in results:
            if isinstance(result, tuple):
                crate_name, trace = result
                analysis_results[crate_name] = trace
            else:
                self.logger.error(f"❌ Unexpected result type: {type(result)}")

        self.logger.info(f"✅ Completed analysis of {len(analysis_results)} crates")
        return analysis_results

    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get a summary of the pipeline configuration and status"""
        summary = {
            "pipeline_version": __version__,
            "components": {
                "irl_engine": self.irl_engine is not None,
                "scraper": "per_task",  # Scrapers are created per task now
                "canon_registry": self.canon_registry is not None,
            },
            "ai_components": {
                "unified_llm_processor": self.unified_llm_processor is not None,
                "azure_openai_enricher": self.ai_enricher is not None,
                "crate_analyzer": self.crate_analyzer is not None,
            },
            "configuration": {
                "max_tokens": self.config.max_tokens,
                "checkpoint_interval": self.config.checkpoint_interval,
                "batch_size": self.config.batch_size,
                "enable_crawl4ai": self.config.enable_crawl4ai,
            },
        }

        # Add LLM configuration if available
        if self.llm_config:
            summary["llm_configuration"] = {
                "provider": self.llm_config.provider,
                "model": self.llm_config.model,
                "temperature": self.llm_config.temperature,
                "max_tokens": self.llm_config.max_tokens,
                "timeout": self.llm_config.timeout,
                "max_retries": self.llm_config.max_retries,
            }
        elif self.config.use_azure_openai:
            summary["llm_configuration"] = {
                "provider": "azure_openai",
                "model": self.config.azure_openai_deployment_name,
                "endpoint": self.config.azure_openai_endpoint,
                "max_tokens": self.config.max_tokens,
            }

        return summary


def create_pipeline_from_args(args: argparse.Namespace) -> UnifiedSigilPipeline:
    """Create pipeline from command line arguments"""
    # Create base config
    config = PipelineConfig()

    # Create LLM config if LLM arguments are provided
    llm_config = None
    if hasattr(args, "llm_provider") and args.llm_provider:
        if UNIFIED_LLM_AVAILABLE and LLMConfig is not None:
            llm_config_params = {
                "provider": args.llm_provider,
                "model": args.llm_model or "gpt-4o",
                "api_base": getattr(args, "llm_api_base", None),
                "api_key": getattr(args, "llm_api_key", None),
                "temperature": getattr(args, "llm_temperature", 0.2),
                "max_tokens": getattr(args, "llm_max_tokens", 256),
                "timeout": getattr(args, "llm_timeout", 30),
                "max_retries": getattr(args, "llm_max_retries", 3),
                "azure_deployment": getattr(args, "azure_deployment", None),
                "azure_api_version": getattr(args, "azure_api_version", None),
                "ollama_host": getattr(args, "ollama_host", None),
                "lmstudio_host": getattr(args, "lmstudio_host", None),
            }
            # Filter out None values so that default values in LLMConfig are
            # used
            llm_config_params = {
                k: v for k, v in llm_config_params.items() if v is not None
            }
            llm_config = LLMConfig(**llm_config_params)
        else:
            logging.warning(
                "Unified LLM processor not available, falling back to Azure OpenAI"
            )

    return UnifiedSigilPipeline(config, llm_config)


def add_llm_arguments(parser: argparse.ArgumentParser) -> None:
    """Add LLM-related command line arguments to the parser"""
    llm_group = parser.add_argument_group("LLM Configuration")

    llm_group.add_argument(
        "--llm-provider",
        choices=[
            "azure",
            "ollama",
            "lmstudio",
            "openai",
            "anthropic",
            "google",
            "cohere",
            "huggingface",
            "lambda",  # Add Lambda.AI support
        ],
        help="LLM provider to use (default: azure)",
    )

    llm_group.add_argument(
        "--llm-model",
        default="gpt-4o",
        help="Model name/identifier (e.g., gpt-4, llama2, claude-3, "
        "qwen25-coder-32b-instruct)",
    )

    llm_group.add_argument(
        "--llm-api-base", help="API base URL (for local providers or custom endpoints)"
    )

    llm_group.add_argument("--llm-api-key", help="API key (if required by provider)")

    llm_group.add_argument(
        "--llm-temperature",
        type=float,
        default=0.2,
        help="Temperature for LLM generation (default: 0.2)",
    )

    llm_group.add_argument(
        "--llm-max-tokens",
        type=int,
        default=256,
        help="Maximum tokens for LLM generation (default: 256)",
    )

    llm_group.add_argument(
        "--llm-timeout",
        type=int,
        default=30,
        help="Timeout for LLM API calls in seconds (default: 30)",
    )

    llm_group.add_argument(
        "--llm-max-retries",
        type=int,
        default=3,
        help="Maximum retries for LLM API calls (default: 3)",
    )

    # Provider-specific arguments
    azure_group = parser.add_argument_group("Azure OpenAI Configuration")
    azure_group.add_argument("--azure-deployment", help="Azure OpenAI deployment name")
    azure_group.add_argument("--azure-api-version", help="Azure OpenAI API version")

    ollama_group = parser.add_argument_group("Ollama Configuration")
    ollama_group.add_argument(
        "--ollama-host",
        default="http://localhost:11434",
        help="Ollama host URL (default: http://localhost:11434)",
    )

    lmstudio_group = parser.add_argument_group("LM Studio Configuration")
    lmstudio_group.add_argument(
        "--lmstudio-host",
        default="http://localhost:1234/v1",
        help="LM Studio host URL (default: http://localhost:1234/v1)",
    )

    # Add Lambda.AI configuration group
    lambda_group = parser.add_argument_group("Lambda.AI Configuration")
    lambda_group.add_argument(
        "--lambda-api-base",
        default="https://api.lambda.ai/v1",
        help="Lambda.AI API base URL (default: https://api.lambda.ai/v1)",
    )


async def quick_analyze_crate(
    crate_name: str,
    config: Optional[PipelineConfig] = None,
    llm_config: Optional[Any] = None,
) -> SacredChainTrace:
    """Quick analysis of a single crate"""
    if config is None:
        config = PipelineConfig()

    async with UnifiedSigilPipeline(config, llm_config) as pipeline:
        return await pipeline.analyze_crate(crate_name)


async def batch_analyze_crates(
    crate_names: List[str],
    config: Optional[PipelineConfig] = None,
    llm_config: Optional[Any] = None,
) -> Dict[str, SacredChainTrace]:
    """Batch analysis of multiple crates"""
    if config is None:
        config = PipelineConfig()

    async with UnifiedSigilPipeline(config, llm_config) as pipeline:
        return await pipeline.analyze_multiple_crates(crate_names)
