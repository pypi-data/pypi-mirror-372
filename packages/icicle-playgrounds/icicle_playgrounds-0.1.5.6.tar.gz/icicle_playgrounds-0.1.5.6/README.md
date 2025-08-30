# ICICLE Playgrounds

**SDK to interact with the ICICLE Model & Data Playgrounds**

ICICLE Playgrounds is a Python SDK designed for working with AI plug-n-play frameworks powered by Tapis Workflows. This library provides standardized Pydantic models and tools for seamless integration with the ICICLE (Intelligent CyberInfrastructure with Computational Learning in the Environment) ecosystem.

## Features

- 🔧 **Plug-n-Play Framework**: Built for easy integration with Tapis Workflows
- 📊 **Pydantic Models**: Type-safe data structures for AI workflows
- 🖼️ **Image Processing**: Support for image data handling and tensor operations
- 🎯 **Detection Results**: Standardized formats for AI model outputs
- 📋 **Model Cards**: PATRA (Partnership for Advanced Trusted Research in AI) model card support
- 🔍 **Bias & XAI Analysis**: Tools for bias analysis and explainable AI

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. Make sure you have Python 3.12+ installed.

```bash
# Install using uv
uv add icicle-playgrounds

# Or install from source
git clone <repository-url>
cd icicle-playgrounds
uv sync
```

## Quick Start

```python
from icicle_playgrounds.pydantic.plug_n_play import Image, Tensor, DetectionResults
from icicle_playgrounds.pydantic.patra_model_cards import PatraModelCard

# Work with images and tensors
image = Image(...)
tensor = Tensor(...)

# Handle detection results
results = DetectionResults(...)

# Create model cards
model_card = PatraModelCard(...)
```

## Project Structure

```
icicle_playgrounds/
├── pydantic/
│   ├── plug_n_play/          # Core plug-n-play data models
│   │   ├── Image.py          # Image handling
│   │   ├── Tensor.py         # Tensor operations
│   │   └── DetectionResults.py  # AI model output formats
│   └── patra_model_cards/    # PATRA model card implementations
```

## Development

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd icicle-playgrounds

# Install dependencies
uv sync

# Install development dependencies
uv sync --group dev
```

### Running Tests

```bash
# Run tests using pytest
uv run pytest

# Or using just (if available)
just test
```

### Documentation Generation

This project includes a script to generate MDX documentation:

```bash
uv run python generate-mdx.py
```

## Dependencies

- **httpx** - HTTP client for API interactions
- **pillow** - Image processing capabilities
- **pydantic** - Data validation and serialization
- **torchvision** - Computer vision utilities

## Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the terms specified in the LICENSE file.

## About ICICLE

ICICLE (Intelligent CyberInfrastructure with Computational Learning in the Environment) is focused on developing AI-driven cyberinfrastructure solutions. This SDK facilitates integration with ICICLE's model and data playgrounds through standardized interfaces and workflows.

## Support

For questions, issues, or support, please refer to the project's issue tracker or contact the ICICLE team.

---

**Version**: 0.1.5.4