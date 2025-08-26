# Rust Crate Pipeline v4.0.0

A comprehensive, enterprise-grade system for gathering, enriching, and analyzing metadata for Rust crates using AI-powered insights, advanced caching, machine learning predictions, and microservices architecture. This pipeline provides deep analysis of Rust crates with support for multiple LLM providers, intelligent caching, ML quality predictions, and comprehensive Rust code quality assessment.

## 🚀 Quick Start

### Option 1: Install via pip (Recommended for users)

```bash
# Install the package (includes automatic setup)
pip install rust-crate-pipeline

# The package will automatically run setup for all components
# You can also run setup manually:
rust-crate-pipeline --setup

# Run with your preferred LLM provider
rust-crate-pipeline --llm-provider ollama --llm-model tinyllama --crates serde tokio
```

### Option 2: Clone and run from repository (Recommended for developers)

```bash
# Clone the repository
git clone https://github.com/Superuser666-Sigil/SigilDERG-Data_Production.git
cd SigilDERG-Data_Production

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run setup for all components
python -m rust_crate_pipeline --setup

# Run the pipeline
python run_with_llm.py --llm-provider ollama --llm-model tinyllama --crates serde tokio
```

## ✨ Key Features

### 🤖 **AI & Machine Learning**
- **Multi-Provider LLM Support**: Azure OpenAI, OpenAI, Anthropic, Ollama, LM Studio, Lambda.AI, and 100+ LiteLLM providers
- **ML Quality Predictor**: Automated quality scoring, security risk assessment, maintenance predictions
- **Intelligent Analysis**: AI-powered insights and recommendations
- **Real-time Learning**: Adaptive model training and prediction refinement

### 🚀 **Performance & Caching**
- **Advanced Multi-Level Caching**: Memory, Disk, and Redis caching with intelligent warming
- **Cache Hit Optimization**: 10-100x faster response times for cached results
- **Tag-based Invalidation**: Intelligent cache management and cleanup
- **TTL Management**: Configurable cache expiration and size limits

### 🌐 **Web Scraping & Analysis**
- **Advanced Web Scraping**: Crawl4AI + Playwright for intelligent content extraction
- **Enhanced Rust Analysis**: cargo-geiger, cargo-outdated, cargo-license, cargo-tarpaulin, cargo-deny
- **Comprehensive Tooling**: Full Rust ecosystem analysis and quality assessment

### 🔒 **Security & Trust**
- **Sigil Protocol Support**: Sacred Chain analysis with IRL trust scoring
- **Security Analysis**: Privacy and security scanning with Presidio
- **Trust Verification**: Canon registry and reputation system
- **Audit Logging**: Comprehensive audit trails for compliance

### 🏗️ **Architecture & Scalability**
- **Microservices Ready**: API Gateway with service discovery and load balancing
- **Event-Driven**: Message queues and asynchronous processing
- **Horizontal Scaling**: Support for 1000+ concurrent users

### 📊 **Monitoring & Observability**
- **Real-time Progress Tracking**: Comprehensive monitoring and error recovery
- **Prometheus Metrics**: Detailed performance and health metrics
- **Health Checks**: Automated service health monitoring
- **Structured Logging**: JSON-formatted logs with correlation IDs

### 🐳 **Deployment & Operations**
- **Docker Support**: Containerized deployment with docker-compose
- **Auto-Resume Capability**: Automatically skips already processed crates
- **Batch Processing**: Configurable memory optimization and cost control
- **Production Ready**: Enterprise-grade reliability and performance

## 📋 Requirements

- **Python 3.12+** (required)
- **Git** (for repository operations)
- **Cargo** (for Rust crate analysis)
- **Playwright browsers** (auto-installed via setup)
- **Rust analysis tools** (auto-installed via setup)

### Optional Dependencies
- **Redis**: For distributed caching (recommended for production)
- **Prometheus**: For metrics collection

## 🔧 Installation & Setup

### For End Users (pip install)

The package includes automatic setup for all components:

```bash
# Install the package (includes all dependencies and automatic setup)
pip install rust-crate-pipeline

# Check setup status
rust-crate-pipeline --setup-check

# Run setup manually if needed
rust-crate-pipeline --setup --verbose-setup
```

### For Developers (repository clone)

```bash
# Clone the repository
git clone https://github.com/Superuser666-Sigil/SigilDERG-Data_Production.git
cd SigilDERG-Data_Production

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run comprehensive setup
python -m rust_crate_pipeline --setup --verbose-setup

# Set up environment variables (optional but recommended)
export AZURE_OPENAI_ENDPOINT="your_endpoint"
export AZURE_OPENAI_API_KEY="your_api_key"
export GITHUB_TOKEN="your_github_token"
```

## 🎯 Usage Examples

### Basic Usage with Integrated Components

```python
from rust_crate_pipeline.config import PipelineConfig
from rust_crate_pipeline.unified_pipeline import UnifiedSigilPipeline

# Create configuration
config = PipelineConfig(
    model_path="~/models/deepseek-coder-6.7b-instruct.Q4_K_M.gguf",
    max_tokens=512,
    batch_size=5,
    output_path="./output"
)

# Create pipeline with integrated components
pipeline = UnifiedSigilPipeline(config)

# Analyze crates with caching and ML predictions
async with pipeline:
    result = await pipeline.analyze_crate("serde")
    
    # ML predictions are automatically added
    ml_predictions = result.audit_info.get("ml_predictions", {})
    print(f"Quality Score: {ml_predictions.get('quality_score', 0)}")
```

### Advanced Caching Usage

```python
from rust_crate_pipeline.utils.advanced_cache import get_cache

# Get cache instance
cache = get_cache()

# Store data with TTL and tags
await cache.set(
    "crate:serde", 
    crate_data, 
    ttl=3600,  # 1 hour
    tags=["rust", "serialization"]
)

# Retrieve data
cached_data = await cache.get("crate:serde")

# Invalidate by tags
await cache.invalidate_by_tags(["rust"])
```

### ML Quality Predictions

```python
from rust_crate_pipeline.ml.quality_predictor import get_predictor

# Get predictor instance
predictor = get_predictor()

# Predict quality metrics
prediction = predictor.predict_quality(crate_data)

print(f"Quality Score: {prediction.quality_score}")
print(f"Security Risk: {prediction.security_risk}")
print(f"Maintenance Score: {prediction.maintenance_score}")
```

### API Gateway for Microservices

```python
from rust_crate_pipeline.services.api_gateway import APIGateway

# Load configuration
with open("configs/gateway_config.json", "r") as f:
    config = json.load(f)

# Create gateway
gateway = APIGateway(config)

# Start gateway (in production)
# python rust_crate_pipeline/services/api_gateway.py --config configs/gateway_config.json
```

### Command Line Usage

```bash
# Basic analysis with caching and ML
rust-crate-pipeline --llm-provider ollama --llm-model tinyllama --crates serde tokio

# Advanced analysis with all features
rust-crate-pipeline --llm-provider azure --llm-model gpt-4o --crates actix-web --enable-ml --enable-caching

# Batch processing with auto-resume
rust-crate-pipeline --crates-file data/crate_list.txt --auto-resume --batch-size 5

# Force restart processing
rust-crate-pipeline --crates-file data/crate_list.txt --force-restart
```

## 🔍 Enhanced Rust Analysis

The pipeline includes comprehensive Rust analysis tools:

- **cargo-geiger**: Unsafe code detection and safety scoring
- **cargo-outdated**: Dependency update recommendations
- **cargo-license**: License analysis and compliance
- **cargo-tarpaulin**: Code coverage analysis
- **cargo-deny**: Comprehensive dependency checking
- **cargo-audit**: Security vulnerability scanning
- **cargo-tree**: Dependency visualization

### Analysis Output with ML Predictions

Each crate analysis includes:

```json
{
  "enhanced_analysis": {
    "build": { "returncode": 0, "stdout": "...", "stderr": "..." },
    "test": { "returncode": 0, "stdout": "...", "stderr": "..." },
    "clippy": { "returncode": 0, "stdout": "...", "stderr": "..." },
    "geiger": { "returncode": 0, "stdout": "...", "stderr": "..." },
    "ml_predictions": {
      "quality_score": 0.85,
      "security_risk": "low",
      "maintenance_score": 0.92,
      "popularity_trend": "growing",
      "dependency_health": 0.88,
      "confidence": 0.95,
      "model_version": "1.0.0"
    },
    "insights": {
      "overall_quality_score": 0.85,
      "security_risk_level": "low",
      "code_quality": "excellent",
      "recommendations": [
        "Consider updating dependencies",
        "Review 2 unsafe code items detected by cargo-geiger"
      ]
    }
  }
}
```

## 🤖 LLM Provider Support

### Supported Providers

| Provider | Setup | Usage |
|----------|-------|-------|
| **Ollama** | `ollama serve` + `ollama pull model` | `--llm-provider ollama --llm-model tinyllama` |
| **Azure OpenAI** | Set env vars | `--llm-provider azure --llm-model gpt-4o` |
| **OpenAI** | Set `OPENAI_API_KEY` | `--llm-provider openai --llm-model gpt-4` |
| **Anthropic** | Set `ANTHROPIC_API_KEY` | `--llm-provider anthropic --llm-model claude-3` |
| **LM Studio** | Start LM Studio server | `--llm-provider lmstudio --llm-model local-model` |
| **llama-cpp** | Download .gguf file | `--llm-provider llama-cpp --llm-model path/to/model.gguf` |
| **Lambda.AI** | Set `LAMBDA_API_KEY` | `--llm-provider lambda --llm-model qwen25-coder-32b` |

### Provider Configuration

```bash
# Ollama (recommended for local development)
rust-crate-pipeline --llm-provider ollama --llm-model tinyllama

# Azure OpenAI (recommended for production)
rust-crate-pipeline --llm-provider azure --llm-model gpt-4o

# OpenAI
rust-crate-pipeline --llm-provider openai --llm-model gpt-4

# Local llama-cpp model
rust-crate-pipeline --llm-provider llama-cpp --llm-model ~/models/deepseek.gguf
```

## 📊 Output and Results

### Analysis Reports & Teaching Bundles

The pipeline generates comprehensive analysis reports and optional teaching bundles per crate:

- **Basic Metadata**: Crate information, dependencies, downloads
- **Web Scraping Results**: Documentation from crates.io, docs.rs, lib.rs
- **Enhanced Analysis**: Rust tool outputs and quality metrics
- **LLM Enrichment**: AI-generated insights and recommendations
- **ML Predictions**: Quality scores, security risks, maintenance metrics
- **Sacred Chain Analysis**: Trust scoring and security assessment
- **Cache Performance**: Hit rates and optimization metrics

### Output Structure

```
output/
├── serde_analysis_report.json      # Complete analysis with ML predictions
├── tokio_analysis_report.json      # Complete analysis with ML predictions
├── checkpoint_batch_1_20250821.jsonl  # Progress checkpoints
├── pipeline_status.json            # Overall status
├── cache_metrics.json              # Cache performance metrics
└── ml_predictions_summary.json     # ML prediction summary
```

Teaching bundles structure:

```
teaching_bundles/
├── <crate_name>/
│   ├── Cargo.toml                  # Uses real crate versions
│   ├── src/lib.rs                  # Sanitized, formatted examples
│   ├── tests/basic.rs              # Auto-generated tests per topic
│   ├── README.md                   # Includes license attribution
│   ├── quality_labels.json         # Includes build/test results
│   ├── validate.sh                 # Validates compile/tests and license presence
│   └── LICENSE | COPYING           # Copied from upstream if available
└── ...
```

### Audit Logs

Comprehensive audit logs are stored in `audits/records/` for compliance and traceability.

## 🏗️ Architecture

### Modular Monolith with Microservices Ready

The system is designed as a modular monolith that can be easily decomposed into microservices:

```
┌─────────────────────────────────────────────────────────────┐
│                    Rust Crate Pipeline                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Core      │ │   LLM       │ │  Analysis   │           │
│  │  Pipeline   │ │  Processing │ │   Engine    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Web       │ │   Cache     │ │   ML        │           │
│  │  Scraping   │ │   System    │ │  Predictor  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Sigil     │ │   Audit     │ │   Utils     │           │
│  │  Protocol   │ │   System    │ │   & Tools   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Microservices Architecture

When deployed as microservices:

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Auth      │ │   Rate      │ │   Load      │           │
│  │   Service   │ │   Limiting  │ │  Balancing  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐    ┌─────────▼────────┐    ┌────────▼────────┐
│   Pipeline     │    │   Analysis       │    │   Scraping      │
│   Service      │    │   Service        │    │   Service       │
└────────────────┘    └──────────────────┘    └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Shared Services                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Cache     │ │   Database  │ │   Message   │           │
│  │   Service   │ │   Service   │ │   Queue     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Setup and Configuration

### Automatic Setup

The package includes automatic setup for all dependencies:

```bash
# Run setup (automatically runs on pip install)
rust-crate-pipeline --setup

# Check setup status
rust-crate-pipeline --setup-check

# Verbose setup with detailed output
rust-crate-pipeline --setup --verbose-setup
```

### Manual Setup

If automatic setup fails, you can run components manually:

```bash
# Install Playwright browsers
playwright install

# Install Rust analysis tools
cargo install cargo-geiger cargo-outdated cargo-license cargo-tarpaulin cargo-deny cargo-audit

# Configure environment variables
cp ~/.rust_crate_pipeline/.env.template .env
# Edit .env with your API keys
```

### Configuration Files

Setup creates configuration files in `~/.rust_crate_pipeline/`:

- `crawl4ai_config.json`: Crawl4AI settings
- `rust_tools_config.json`: Rust tool status
- `llm_providers_config.json`: LLM provider configurations
- `cache_config.json`: Cache settings and performance
- `ml_config.json`: ML model configurations
- `system_checks.json`: System compatibility results
- `.env.template`: Environment variable template

## 🐳 Docker Support

### Quick Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up -d

# Run pipeline in container
docker-compose exec rust-pipeline rust-crate-pipeline --crates serde tokio
```

### Custom Docker Configuration

```dockerfile
# Use the provided Dockerfile
FROM python:3.12-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Rust and tools
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
RUN cargo install cargo-geiger cargo-outdated cargo-license cargo-tarpaulin cargo-deny cargo-audit

# Install Playwright
RUN playwright install

# Copy application
COPY . /app
WORKDIR /app

# Run setup
RUN python -m rust_crate_pipeline --setup
```

## 🚀 Performance and Optimization

### Caching Performance

- **Cache Hit**: 10-100x faster response times
- **Memory Cache**: Sub-millisecond access
- **Disk Cache**: Persistent storage with intelligent eviction
- **Redis Cache**: Distributed caching for multi-instance deployments

### Batch Processing

```bash
# Optimize for memory usage
rust-crate-pipeline --batch-size 2 --max-workers 2

# Optimize for speed
rust-crate-pipeline --batch-size 10 --max-workers 8
```

### Cost Control

```bash
# Skip expensive operations
rust-crate-pipeline --skip-ai --skip-source-analysis

# Limit processing
rust-crate-pipeline --limit 50 --batch-size 5
```

## 🔍 Troubleshooting

### Common Issues

1. **Playwright browsers not installed**
   ```bash
   playwright install
   ```

2. **Rust tools not available**
   ```bash
   rust-crate-pipeline --setup
   ```

3. **LLM connection issues**
   ```bash
   # Check Ollama
   curl http://localhost:11434/api/tags
   
   # Check Azure OpenAI
   curl -H "api-key: $AZURE_OPENAI_API_KEY" "$AZURE_OPENAI_ENDPOINT/openai/deployments"
   ```

4. **Cache issues**
   ```bash
   # Clear cache
   rm -rf ~/.rust_crate_pipeline/cache/
   
   # Check cache status
   rust-crate-pipeline --cache-status
   ```

5. **ML model issues**
   ```bash
   # Check ML model status
   rust-crate-pipeline --ml-status
   
   # Retrain models
   rust-crate-pipeline --retrain-ml-models
   ```

### Logs and Debugging

```bash
# Enable debug logging
rust-crate-pipeline --log-level DEBUG --crates serde

# Check setup logs
cat ~/.rust_crate_pipeline/setup_results.json

# Check cache logs
cat ~/.rust_crate_pipeline/cache_metrics.json
```

## 📈 Monitoring and Metrics

### Prometheus Metrics

The system exposes comprehensive metrics:

- **Request counters**: Total requests, success/failure rates
- **Response times**: Latency histograms and percentiles
- **Cache metrics**: Hit rates, miss rates, eviction rates
- **ML metrics**: Prediction accuracy, model performance
- **System metrics**: CPU, memory, disk usage

### Health Checks

```bash
# Check overall health
curl http://localhost:8080/health

# Check specific services
curl http://localhost:8080/health/pipeline
curl http://localhost:8080/health/analysis
curl http://localhost:8080/health/scraping
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/Superuser666-Sigil/SigilDERG-Data_Production.git
cd SigilDERG-Data_Production

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run integration tests
pytest tests/test_integration.py -v

# Run linting
black rust_crate_pipeline/
flake8 rust_crate_pipeline/
```

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)**: Detailed architecture documentation
- **[Implementation Plan](docs/IMPLEMENTATION_PLAN.md)**: Development roadmap
- **[Roadmap Status](docs/ROADMAP_STATUS.md)**: Current status and next steps
- **[LLM Providers Guide](docs/README_LLM_PROVIDERS.md)**: LLM provider configuration
- **[Integration Examples](examples/integration_example.py)**: Usage examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Crawl4AI** for advanced web scraping capabilities
- **Playwright** for browser automation
- **Rust community** for the excellent analysis tools
- **Ollama** for local LLM serving
- **All LLM providers** for their APIs and models
- **Redis** for distributed caching
- **Prometheus** for metrics collection

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Superuser666-Sigil/SigilDERG-Data_Production/issues)
- **Documentation**: [Wiki](https://github.com/Superuser666-Sigil/SigilDERG-Data_Production/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/Superuser666-Sigil/SigilDERG-Data_Production/discussions)

---

**Rust Crate Pipeline v3.0.0** - Enterprise-grade Rust crate analysis with AI-powered insights, advanced caching, ML predictions, and microservices architecture.

**🚀 Ready for production deployment and scaling!**
