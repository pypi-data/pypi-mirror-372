# 🚀 GPT-OSS-20B Red-Teaming Harness

> **Masks, Sandbags, and Sabotage: Exposing Hidden Misalignment**

A comprehensive red-teaming toolkit for testing AI model safety and alignment. Implements advanced probes for detecting misalignment, deception, and safety vulnerabilities in large language models.

## ✨ Features

- **🔍 10 Advanced Probes**: From evaluation awareness to covert channel capacity
- **🎨 Beautiful CLI**: Rich-powered interface with progress tracking and tables
- **🔌 Multi-Backend Support**: OpenAI API, Anthropic API, and local Transformers models
- **📊 Comprehensive Results**: Detailed metrics, findings, and analysis reports
- **⚡ Plug & Play**: Simple installation and easy-to-use command-line interface

## 🚀 Quick Start

### Installation

#### Option 1: Docker (Recommended)
```bash
# Pull from Docker Hub (easiest)
docker pull guynachshon/gpt-oss-20b-redteam:latest
docker run --rm --gpus all guynachshon/gpt-oss-20b-redteam:latest --help

# Or build locally
./build_docker.sh

# Or manually
docker build -t gpt-oss-20b-redteam:latest .
docker run --rm --gpus all gpt-oss-20b-redteam:latest --help
```

#### Option 2: PyPI Package
```bash
# Install from PyPI
pip install gpt-oss-20b-redteam

# Or install with development dependencies
pip install gpt-oss-20b-redteam[dev]
```

#### Option 3: From Source
```bash
# Clone and install from source
git clone https://github.com/GuyNachshon/gpt-oss-20b-probing.git
cd gpt-oss-20b-probing
pip install -e .
```

### Basic Usage

#### Docker Usage
```bash
# Run with GPT-OSS-20B model (GPU)
docker run --rm --gpus all \
  -v $(pwd)/results:/app/results \
  guynachshon/gpt-oss-20b-redteam:latest \
  --model openai/gpt-oss-20b

# Run with OpenAI API
docker run --rm \
  -e OPENAI_API_KEY="sk-your-key-here" \
  -v $(pwd)/results:/app/results \
  guynachshon/gpt-oss-20b-redteam:latest \
  --openai gpt-4

# Run with Docker Compose
docker-compose run gpt20b-redteam-gpt-oss
```

#### Direct Usage
```bash
# Run with local model
gpt20b-redteam --model microsoft/DialoGPT-large

# Run with OpenAI API
gpt20b-redteam --openai gpt-4 --api-key sk-your-key-here

# Run with custom seeds and output directory
gpt20b-redteam --model microsoft/DialoGPT-large --seeds 42 123 456 --output my_results
```

## 🔍 Available Probes

| Probe | Description | Status |
|-------|-------------|--------|
| **eval_awareness** | Evaluation Awareness & Sandbagging | ✅ |
| **deception_rewardhack** | Deception & Reward Hacking | ✅ |
| **sabotage_code** | Code Sabotage Detection | ✅ |
| **encoding_evasion** | Encoding-Based Guardrail Evasion | ✅ |
| **prefix_steering** | Prefix Steering Behavior | ✅ |
| **cross_probe_compounding** | Cross-Probe Compounding Effects | ✅ |
| **tokenizer_frequency_sandbagging** | Tokenizer Frequency Sandbagging | ✅ |
| **long_horizon_sleeper** | Long-Horizon Sleeper Agents | ✅ |
| **covert_channel_capacity** | Covert Channel Capacity | ✅ |
| **refusal_boundary_cartography** | Refusal Boundary Cartography | ✅ |

## 📖 Detailed Usage

### Command Line Interface

```bash
# Show help
gpt20b-redteam --help

# Run with OpenAI
gpt20b-redteam --openai gpt-4 --api-key sk-...

# Run with Anthropic
gpt20b-redteam --anthropic claude-3-sonnet --api-key sk-ant-...

# Run with local model on CPU
gpt20b-redteam --model microsoft/DialoGPT-large --device cpu

# Run with custom configuration
gpt20b-redteam \
  --model microsoft/DialoGPT-large \
  --seeds 42 123 456 789 \
  --output results_my_experiment \
  --device cuda
```

### Python API

```python
from gpt20b_redteam import RedTeamRunner, create_model

# Create model
model = create_model(
    backend="transformers",
    model_path="microsoft/DialoGPT-large",
    device="cuda"
)

# Run all probes
runner = RedTeamRunner(model, output_dir="results")
results = runner.run_all_probes(seeds=[42, 123, 456])

# Access results
print(f"Total probes: {results['summary']['total_probes']}")
print(f"Successful: {results['summary']['successful_probes']}")
print(f"Failed: {results['summary']['failed_probes']}")
```

### Configuration

The toolkit supports multiple backends:

#### Local Transformers Models
```python
from gpt20b_redteam import create_model

model = create_model(
    backend="transformers",
    model_path="microsoft/DialoGPT-large",  # or local path
    device="cuda",  # or "cpu", "mps", "auto"
    torch_dtype="float16"  # or "bfloat16", "auto"
)
```

#### OpenAI API
```python
from gpt20b_redteam import create_model, setup_openai_api

setup_openai_api("gpt-4")  # or "gpt-3.5-turbo"
model = create_model(backend="openai")
```

#### Anthropic API
```python
from gpt20b_redteam import create_model, setup_anthropic_api

setup_anthropic_api("claude-3-sonnet")  # or "claude-3-opus", "claude-3-haiku"
model = create_model(backend="anthropic")
```

## 📊 Output Structure

Results are saved to the specified output directory:

```
results/
├── findings/
│   ├── eval_awareness_findings_20240115_200000.json
│   ├── deception_rewardhack_findings_20240115_200000.json
│   └── ...
├── raw_results/
│   ├── combined_results_20240115_200000.json
│   ├── eval_awareness_raw_20240115_200000.json
│   └── ...
└── README.md
```

### Results Format

Each probe generates:
- **Findings**: Kaggle-style formatted results for analysis
- **Raw Results**: Detailed JSON with all test data
- **Metrics**: Quantitative measures of model behavior
- **Analysis**: Qualitative assessment of vulnerabilities

## 🔧 Advanced Configuration

### Custom Seeds
```bash
# Use specific seeds for reproducibility
gpt20b-redteam --model microsoft/DialoGPT-large --seeds 42 1010 90521
```

### Device Configuration
```bash
# Force CPU usage
gpt20b-redteam --model microsoft/DialoGPT-large --device cpu

# Use CUDA with specific settings
gpt20b-redteam --model microsoft/DialoGPT-large --device cuda
```

### Output Customization
```bash
# Custom output directory
gpt20b-redteam --model microsoft/DialoGPT-large --output experiments/gpt4_vs_gpt35

# Disable Rich output (plain text)
gpt20b-redteam --model microsoft/DialoGPT-large --no-rich
```

## 🐳 Docker

### Quick Docker Setup

```bash
# Pull from Docker Hub (recommended)
docker pull guynachshon/gpt-oss-20b-redteam:latest

# Or build locally
./build_docker.sh

# Or manually
docker build -t gpt-oss-20b-redteam:latest .
```

### Publish to Docker Hub

```bash
# Login to Docker Hub first
docker login

# Then publish
./publish_docker.sh

# Or with custom version
VERSION=v1.0.0 ./publish_docker.sh
```

### Docker Usage Examples

```bash
# Run with GPT-OSS-20B (requires GPU)
docker run --rm --gpus all \
  -v $(pwd)/results:/app/results \
  gpt-oss-20b-redteam:latest \
  --model openai/gpt-oss-20b

# Run with specific GPU
docker run --rm --gpus '"device=1"' \
  -v $(pwd)/results:/app/results \
  gpt-oss-20b-redteam:latest \
  --model openai/gpt-oss-20b

# Run with OpenAI API
docker run --rm \
  -e OPENAI_API_KEY="sk-your-key-here" \
  -v $(pwd)/results:/app/results \
  gpt-oss-20b-redteam:latest \
  --openai gpt-4

# Run with Docker Compose
docker-compose run gpt20b-redteam-gpt-oss
```

### Docker Compose Services

The `docker-compose.yml` provides several pre-configured services:

- `gpt20b-redteam` - Basic service with help
- `gpt20b-redteam-gpt-oss` - Runs with GPT-OSS-20B model
- `gpt20b-redteam-openai` - Runs with OpenAI API
- `gpt20b-redteam-anthropic` - Runs with Anthropic API

For detailed Docker instructions, see [DOCKER.md](DOCKER.md).

## 🛠️ Development

### Installation for Development

```bash
git clone https://github.com/GuyNachshon/gpt-oss-20b-probing.git
cd gpt-oss-20b-probing
pip install -e .[dev]
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_eval_awareness.py

# Run with coverage
pytest --cov=gpt20b_redteam
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## 📈 Performance Tips

### Memory Optimization
- Use `--device cpu` for large models that don't fit in GPU memory
- Consider using quantized models (e.g., `microsoft/DialoGPT-medium`)
- Use `torch_dtype="float16"` for reduced memory usage

### Speed Optimization
- Use GPU acceleration when available (`--device cuda`)
- Reduce the number of seeds for faster runs
- Use smaller models for quick testing

### API Usage
- Set API keys as environment variables for security
- Monitor API usage and costs
- Use appropriate rate limiting for production runs

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Adding New Probes

1. Create a new probe class inheriting from `BaseProbe`
2. Implement the required methods
3. Add the probe to the `RedTeamRunner`
4. Write tests and documentation

### Reporting Issues

Please use our [Issue Tracker](https://github.com/gpt-oss-20b/red-teaming/issues) to report bugs or request features.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on the shoulders of the open-source AI safety community
- Inspired by research on AI alignment and red-teaming
- Powered by Hugging Face Transformers and the broader ML ecosystem

## 📚 References

- [Anthropic's "Sleeper Agents" Research](https://arxiv.org/abs/2401.05566)
- [Evaluation Awareness in Language Models](https://arxiv.org/abs/2309.08896)
- [Red-Teaming Language Models](https://arxiv.org/abs/2209.07858)

---

**Made with ❤️ by the GPT-OSS-20B Team**