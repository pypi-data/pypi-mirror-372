# llm_factory.py
import logging
import os
from typing import Optional

from .config import PipelineConfig
from .llm_client import LLMClient, LLMConfig

logger = logging.getLogger(__name__)


def create_llm_client_from_config(config: PipelineConfig) -> LLMClient:
    """Create LLM client from existing pipeline configuration."""

    # Determine provider from config with safe attribute checking
    if hasattr(config, "use_azure_openai") and config.use_azure_openai:
        provider = "azure"
        model = getattr(config, "azure_openai_deployment_name", "gpt-4")
        api_base = getattr(config, "azure_openai_endpoint", None)
        api_key = getattr(config, "azure_openai_api_key", None)
    else:
        # Check environment for provider preference
        provider = os.getenv("LLM_PROVIDER", "ollama")
        model = os.getenv("LLM_MODEL", "tinyllama")  # Changed default to tinyllama
        api_base = os.getenv("LLM_API_BASE", "http://localhost:11434")
        api_key = os.getenv("LLM_API_KEY", "ollama")

    # Create LLM config with provider-specific settings
    llm_config = LLMConfig(
        provider=provider,
        model=model,
        api_base=api_base,
        api_key=api_key,
        request_timeout=120.0,
        max_retries=getattr(config, "max_retries", 6),
        num_ctx=getattr(config, "model_token_limit", 4096),
    )

    # Add provider-specific configurations
    if provider == "llama-cpp":
        llm_config.model_path = os.getenv("LLAMA_CPP_MODEL_PATH", model)
        llm_config.n_gpu_layers = int(os.getenv("LLAMA_CPP_GPU_LAYERS", "-1"))
        llm_config.n_ctx = int(
            os.getenv(
                "LLAMA_CPP_N_CTX", str(getattr(config, "model_token_limit", 8192))
            )
        )
    elif provider == "litellm":
        llm_config.litellm_model_name = os.getenv("LITELLM_MODEL_NAME", model)

    logger.info(f"Created LLM client: {provider}/{model}")
    return LLMClient(llm_config)


def create_llm_client_from_env() -> LLMClient:
    """Create LLM client from environment variables."""

    # Check environment variables for provider choice
    provider = os.getenv("LLM_PROVIDER", "ollama")
    model = os.getenv("LLM_MODEL", "gpt-oss-120b")
    api_base = os.getenv("LLM_API_BASE")
    api_key = os.getenv("LLM_API_KEY", "ollama")

    llm_config = LLMConfig(
        provider=provider,
        model=model,
        api_base=api_base,
        api_key=api_key,
        request_timeout=float(os.getenv("LLM_TIMEOUT", "120.0")),
        max_retries=int(os.getenv("LLM_MAX_RETRIES", "6")),
        num_ctx=int(os.getenv("LLM_NUM_CTX", "8192")),
    )

    # Add provider-specific configurations
    if provider == "llama-cpp":
        llm_config.model_path = os.getenv("LLAMA_CPP_MODEL_PATH", model)
        llm_config.n_gpu_layers = int(os.getenv("LLAMA_CPP_GPU_LAYERS", "-1"))
        llm_config.n_ctx = int(os.getenv("LLAMA_CPP_N_CTX", "8192"))
    elif provider == "litellm":
        llm_config.litellm_model_name = os.getenv("LITELLM_MODEL_NAME", model)

    logger.info(f"Created LLM client from env: {provider}/{model}")
    return LLMClient(llm_config)


def create_ollama_client(
    model: str = "gpt-oss-120b",
    host: str = "localhost",
    port: int = 11434,
    *,
    request_timeout: float | None = None,
    max_retries: int | None = None,
) -> LLMClient:
    """Create Ollama client with specific model and host."""
    api_base = host if host.startswith("http") else f"http://{host}:{port}"

    llm_config = LLMConfig(
        provider="ollama",
        model=model,
        api_base=api_base,
        api_key="ollama",
        num_ctx=8192,
        keep_alive="1h",
        request_timeout=request_timeout or 120.0,
        max_retries=max_retries or 6,
    )

    logger.info(f"Created Ollama client: {model}@{host}:{port}")
    return LLMClient(llm_config)


def create_llama_cpp_client(
    model_path: str,
    n_gpu_layers: int = -1,
    n_ctx: int = 8192,
    *,
    request_timeout: float | None = None,
    max_retries: int | None = None,
) -> LLMClient:
    """Create llama-cpp-python client with specific model."""
    llm_config = LLMConfig(
        provider="llama-cpp",
        model=model_path,
        model_path=model_path,
        n_gpu_layers=n_gpu_layers,
        n_ctx=n_ctx,
        request_timeout=request_timeout or 120.0,
        max_retries=max_retries or 6,
    )

    logger.info(f"Created llama-cpp client: {model_path}")
    return LLMClient(llm_config)


def create_litellm_client(
    model: str,
    *,
    api_key: Optional[str] = None,
    request_timeout: float | None = None,
    max_retries: int | None = None,
) -> LLMClient:
    """Create LiteLLM client with specific model."""
    llm_config = LLMConfig(
        provider="litellm",
        model=model,
        api_key=api_key,
        litellm_model_name=model,
        request_timeout=request_timeout or 120.0,
        max_retries=max_retries or 6,
    )

    logger.info(f"Created LiteLLM client: {model}")
    return LLMClient(llm_config)


def create_azure_client(
    *,
    model: str,
    api_base: str,
    api_key: str,
    request_timeout: float | None = None,
    max_retries: int | None = None,
) -> LLMClient:
    """Create Azure OpenAI client."""
    llm_config = LLMConfig(
        provider="azure",
        model=model,
        api_base=api_base,
        api_key=api_key,
        request_timeout=request_timeout or 120.0,
        max_retries=max_retries or 6,
    )

    logger.info(f"Created Azure client: {model}")
    return LLMClient(llm_config)


def create_openai_client(
    *,
    model: str,
    api_key: str,
    api_base: Optional[str] = None,
    request_timeout: float | None = None,
    max_retries: int | None = None,
) -> LLMClient:
    """Create OpenAI client."""
    llm_config = LLMConfig(
        provider="openai",
        model=model,
        api_base=api_base,
        api_key=api_key,
        request_timeout=request_timeout or 120.0,
        max_retries=max_retries or 6,
    )

    logger.info(f"Created OpenAI client: {model}")
    return LLMClient(llm_config)
