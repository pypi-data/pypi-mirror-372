# config.py
"""Configuration module for the Rust Crate Pipeline.

This module provides configuration classes and utilities for managing
pipeline settings, credentials, and runtime parameters.

All configuration follows PEP 8 style guidelines and enterprise security
best practices.
"""
import os
import warnings
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any, Union

from .exceptions import ConfigurationError

if TYPE_CHECKING:
    from typing import Dict, List

# Import the robust serialization utility
try:
    from utils.serialization_utils import to_serializable
except ImportError:
    try:
        # Fallback for when utils is not available as a top-level module
        from rust_crate_pipeline.utils.serialization_utils import \
            to_serializable
    except ImportError:
        # Fallback if import fails
        def to_serializable(obj: Any) -> Any:
            """Fallback serialization function when utils module is not available."""
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            elif hasattr(obj, "__dict__"):
                return obj.__dict__
            else:
                return str(obj)


# Filter Pydantic deprecation warnings from dependencies
# Rule Zero Compliance: Suppress third-party warnings while maintaining
# awareness
warnings.filterwarnings(
    "ignore",
    message=".*Support for class-based `config` is deprecated.*",
    category=DeprecationWarning,
    module="pydantic._internal._config",
)


@dataclass
class PipelineConfig:
    # Model configuration
    model_path: str = os.path.expanduser(
        "~/models/deepseek/deepseek-coder-6.7b-instruct.Q4_K_M.gguf"
    )
    max_tokens: int = 256
    model_token_limit: int = 4096
    prompt_token_margin: int = 3000

    # LLM Configuration (for JSON config compatibility)
    llm_provider: str = "llama-cpp-python"
    llm_model: str = ""
    llm_api_base: str = ""
    llm_api_key: str = ""
    llm_request_timeout: float = 120.0
    llm_max_retries: int = 3
    llm_num_ctx: int = 4096
    llm_keep_alive: str = "1h"

    # Generation parameters
    temperature: float = 0.3
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    # Local model optimization settings
    local_model_mode: bool = field(
        default_factory=lambda: os.getenv("LOCAL_MODEL_MODE", "false").lower() == "true"
    )
    local_model_token_limit: int = 2048  # Conservative for local models
    local_model_prompt_margin: int = 1500  # More room for responses
    local_model_max_tokens: int = 512  # Allow longer responses
    local_model_temperature: float = 0.1  # Lower temperature for consistency
    local_model_chunk_size: int = 800  # Smaller chunks for local models

    # Pipeline configuration
    checkpoint_interval: int = 10
    max_retries: int = 3
    cache_ttl: int = 3600  # 1 hour
    batch_size: int = 10
    n_workers: int = 4
    skip_source_analysis: bool = False

    # GitHub configuration
    github_token: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))

    # Enhanced scraping configuration
    enable_crawl4ai: bool = True
    crawl4ai_model: str = os.path.expanduser(
        "~/models/deepseek/deepseek-coder-6.7b-instruct.Q4_K_M.gguf"
    )
    crawl4ai_timeout: int = 30

    # Output configuration
    output_path: str = "output"
    output_dir: str = "output"
    verbose: bool = False
    llm_max_retries: int = 3

    # Azure OpenAI Configuration - NO DEFAULTS FOR SENSITIVE DATA
    use_azure_openai: bool = field(
        default_factory=lambda: os.getenv("USE_AZURE_OPENAI", "false").lower() == "true"
    )
    azure_openai_endpoint: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", "")
    )
    azure_openai_api_key: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", "")
    )
    azure_openai_deployment_name: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    )
    azure_openai_api_version: str = field(
        default_factory=lambda: os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
        )
    )

    # Environment configuration
    environment: str = field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )

    @classmethod
    def from_json_config(cls, json_config: dict) -> "PipelineConfig":
        """Create PipelineConfig from nested JSON configuration."""
        config_kwargs = {}

        # Handle LLM configuration section
        if "llm_config" in json_config:
            llm_config = json_config["llm_config"]
            config_kwargs.update(
                {
                    "llm_provider": llm_config.get("provider", "llama-cpp-python"),
                    "llm_model": llm_config.get("model", ""),
                    "llm_api_base": llm_config.get("api_base", ""),
                    "llm_api_key": llm_config.get("api_key", ""),
                    "llm_request_timeout": llm_config.get("request_timeout", 120.0),
                    "llm_max_retries": llm_config.get("max_retries", 3),
                    "llm_num_ctx": llm_config.get("num_ctx", 4096),
                    "llm_keep_alive": llm_config.get("keep_alive", "1h"),
                }
            )

        # Handle generation parameters
        if "generation_params" in json_config:
            gen_params = json_config["generation_params"]
            config_kwargs.update(
                {
                    "temperature": gen_params.get("temperature", 0.3),
                    "max_tokens": gen_params.get("max_tokens", 256),
                    "top_p": gen_params.get("top_p", 0.9),
                    "frequency_penalty": gen_params.get("frequency_penalty", 0.0),
                    "presence_penalty": gen_params.get("presence_penalty", 0.0),
                }
            )

        # Handle processing configuration
        if "processing_config" in json_config:
            proc_config = json_config["processing_config"]
            config_kwargs.update(
                {
                    "batch_size": proc_config.get("batch_size", 10),
                    "n_workers": proc_config.get("max_workers", 4),
                    "max_retries": proc_config.get("max_retries", 3),
                }
            )

        # Handle output configuration
        if "output_config" in json_config:
            output_config = json_config["output_config"]
            config_kwargs.update(
                {
                    "output_dir": output_config.get("output_dir", "./output"),
                    "output_path": output_config.get("output_dir", "./output"),
                }
            )

        # Handle logging configuration
        if "logging" in json_config:
            logging_config = json_config["logging"]
            config_kwargs.update(
                {
                    "verbose": logging_config.get("verbose", False),
                }
            )

        # Handle any top-level configurations
        for key, value in json_config.items():
            if key not in [
                "llm_config",
                "generation_params",
                "processing_config",
                "output_config",
                "logging",
                "crate_selection",
                "ollama_specific",
                "performance_tuning",
            ]:
                if hasattr(cls, key):
                    config_kwargs[key] = value

        return cls(**config_kwargs)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate configuration values."""
        # Validate Azure OpenAI configuration if enabled
        if self.use_azure_openai:
            if not self.azure_openai_endpoint:
                raise ConfigurationError(
                    "Azure OpenAI is enabled but AZURE_OPENAI_ENDPOINT is not set"
                )
            if not self.azure_openai_api_key:
                raise ConfigurationError(
                    "Azure OpenAI is enabled but AZURE_OPENAI_API_KEY is not set"
                )

        # Validate GitHub token if needed (can be optional for public repos)
        if not self.github_token and self.environment == "production":
            warnings.warn(
                "No GitHub token provided. API rate limits will be restricted.",
                RuntimeWarning,
            )

        # Validate numeric configurations
        if self.batch_size <= 0:
            raise ConfigurationError(
                f"batch_size must be positive, got {self.batch_size}"
            )
        if self.n_workers <= 0:
            raise ConfigurationError(
                f"n_workers must be positive, got {self.n_workers}"
            )
        if self.max_retries < 0:
            raise ConfigurationError(
                f"max_retries must be non-negative, got {self.max_retries}"
            )

    class Config:
        validate_assignment = True


@dataclass
class CrateMetadata:
    name: str
    version: str
    description: str
    repository: str
    keywords: "List[str]"
    categories: "List[str]"
    readme: str
    downloads: int
    github_stars: int = 0
    dependencies: "List[Dict[str, Any]]" = field(default_factory=list)
    features: "Dict[str, List[str]]" = field(default_factory=dict)
    code_snippets: "List[str]" = field(default_factory=list)
    readme_sections: "Dict[str, str]" = field(default_factory=dict)
    librs_downloads: Union[int, None] = None
    source: str = "crates.io"
    # Enhanced scraping fields
    enhanced_scraping: "Dict[str, Any]" = field(default_factory=dict)
    enhanced_features: "List[str]" = field(default_factory=list)
    enhanced_dependencies: "List[str]" = field(default_factory=list)

    def to_dict(self) -> "Dict[str, Any]":
        """Convert the object to a dictionary."""
        result = to_serializable(asdict(self))
        if isinstance(result, dict):
            return result
        else:
            return {"data": str(result)}


@dataclass
class EnrichedCrate(CrateMetadata):
    readme_summary: Union[str, None] = None
    feature_summary: Union[str, None] = None
    use_case: Union[str, None] = None
    score: Union[float, None] = None
    factual_counterfactual: Union[str, None] = None
    source_analysis: Union["Dict[str, Any]", None] = None
    user_behavior: Union["Dict[str, Any]", None] = None
    security: Union["Dict[str, Any]", None] = None
