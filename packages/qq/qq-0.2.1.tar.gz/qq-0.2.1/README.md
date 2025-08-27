# Quick Question (qq)

A powerful, cross-platform CLI tool that generates and executes terminal commands using 100+ LLM providers through LiteLLM integration. It intelligently prioritizes local models for privacy and falls back to cloud providers when configured.

[![PyPI version](https://img.shields.io/pypi/v/qq)](https://pypi.org/project/qq/)
[![Python](https://img.shields.io/pypi/pyversions/qq)](https://pypi.org/project/qq/)
[![License](https://img.shields.io/badge/license-Proprietary-blue)](LICENSE)

## 🚀 Key Features

### Universal LLM Support (100+ Providers via LiteLLM)
- **Local Providers** (Privacy-first, no API keys):
  - Ollama (port 11434) - Run open-source models locally
  - LM Studio (port 1234) - GUI-based local model management
  
- **Major Cloud Providers**:
  - OpenAI (GPT-4o, GPT-5, ChatGPT models)
  - Anthropic (Claude 3.5 Sonnet/Haiku/Opus)
  - Google (Gemini, PaLM)
  - Amazon Bedrock
  - Azure OpenAI
  - Groq (Fast inference)
  - Grok (xAI)
  
- **Specialized Providers** (via LiteLLM):
  - Cohere, Replicate, Hugging Face
  - Together AI, Anyscale, Perplexity
  - DeepInfra, AI21, Voyage AI
  - And 80+ more providers!

### Intelligent Features
- ⚡ **Smart Provider Selection**: Automatically detects and uses available providers
- 🎯 **Model Optimization**: Selects best models based on availability and performance
- 📝 **Command History**: Track and replay previous commands
- 🎨 **Rich Interactive UI**: Beautiful terminal interface with Textual TUI
- 📋 **Clipboard Integration**: Copy or type commands directly
- 🔧 **Developer Mode**: Extensible framework for custom actions
- 🚄 **Simple Mode**: Streamlined one-shot command generation
- 💾 **Smart Caching**: 1-hour TTL for providers and models

## 📦 Installation

### From PyPI (Stable)
```bash
pip install qq
```

### From Test PyPI (Latest Features)
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ qq2
```

### From Source (Development)
```bash
git clone https://github.com/yourusername/quickquestion.git
cd quickquestion
pip install -e .
```

## 🎯 Quick Start

### Basic Usage
```bash
# Get a command suggestion
qq "find all large files over 100MB"

# Simple mode - instant command (no UI)
qq --simple "kill process on port 8080"

# Type command directly to terminal
qq --simple-type "list docker containers"
```

### Configuration
```bash
# Interactive settings (Rich UI)
qq --settings

# Advanced configuration (Textual TUI)
qq --config

# View command history
qq --history

# Developer mode
qq --dev
```

## ⚙️ Configuration Options

### Interactive Settings (`qq --settings`)
Navigate with arrow keys through:
1. **Default Provider** - Choose from available providers
2. **Default Model** - Select model for chosen provider  
3. **Command Action** - Run or Copy commands
4. **Simple Mode** - Enable/disable streamlined mode
5. **Simple Mode Action** - Copy or Type behavior

### Advanced Config (`qq --config`)
Beautiful Textual TUI with tabs:
- **Quick Setup** - Same as `--settings` but in modern UI
- **Providers** - Browse and configure 100+ providers
- **Settings** - General application settings
- **About** - Version and documentation

Settings are persisted in `~/.qq_settings.json`

## 🔌 Provider Setup

### Local Providers (No API Key Required)

#### Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2

# qq will auto-detect Ollama on port 11434
qq "your question"
```

#### LM Studio
1. Download from [lmstudio.ai](https://lmstudio.ai)
2. Load any GGUF model
3. Start local server (port 1234)
4. qq auto-detects LM Studio

### Cloud Providers

#### OpenAI
```bash
export OPENAI_API_KEY="sk-..."
qq "your question"
```

#### Anthropic
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
qq "your question"
```

#### Other Providers
qq supports 100+ providers through LiteLLM. Set the appropriate environment variable:
```bash
export GROQ_API_KEY="..."
export XAI_API_KEY="..."  # For Grok
export GEMINI_API_KEY="..."
export COHERE_API_KEY="..."
# etc.
```

## 🎨 Usage Examples

### Command Generation
```bash
# File operations
qq "find files modified today"
qq "compress all images in current directory"

# System management
qq "show memory usage by process"
qq "find what's using port 3000"

# Git operations
qq "undo last commit keeping changes"
qq "show commits by author in last week"

# Docker/Kubernetes
qq "remove all stopped containers"
qq "get pod logs from last hour"
```

### Simple Mode (No UI)
```bash
# Copy to clipboard
qq --simple-copy "create python virtual environment"
# ✓ Copied: python -m venv venv

# Type to terminal
qq --simple-type "activate virtual environment"
# source venv/bin/activate [appears in terminal]
```

### Developer Mode
```bash
qq --dev
# Access specialized developer actions and workflows
```

## 🛠️ Advanced Features

### Custom Developer Actions
Create `~/QuickQuestion/CustomDevActions/my_action.py`:
```python
from quickquestion.dev_actions.base import DevAction

class MyAction(DevAction):
    @property
    def name(self) -> str:
        return "My Custom Action"
    
    @property
    def description(self) -> str:
        return "Does something special"
    
    def execute(self) -> bool:
        self.console.print("[green]Executing...[/green]")
        # Your logic here
        return True
```

### Performance Optimizations
- **Async Provider Detection**: Parallel checking for fastest startup
- **Smart Caching**: 1-hour TTL for providers, 30-second for other data
- **Lazy Loading**: Deferred initialization in simple mode
- **Model Prioritization**: Automatic selection of optimal models

### Debugging
```bash
# Enable debug output
qq --debug "your question"

# Clear provider cache
qq --clear-cache
```

## 📁 File Locations

- `~/.qq_settings.json` - User preferences
- `~/.qq_history.json` - Command history (last 100)
- `~/.qq_cache.json` - Provider and model cache
- `~/QuickQuestion/CustomDevActions/` - Custom actions

## 🔧 Troubleshooting

### Provider Not Detected
```bash
# Clear cache and re-detect
qq --clear-cache
qq --settings  # Reconfigure
```

### API Key Issues
```bash
# Verify environment variable
echo $OPENAI_API_KEY

# Set in shell profile
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
```

### SSL Certificate Errors
```bash
# macOS-specific fix
export CERT_PATH=$(python -m certifi)
export SSL_CERT_FILE="$CERT_PATH"
```

## 🚢 CI/CD & Deployment

### GitHub Actions / Gitea Actions
The project includes automated workflows for:
- Testing on push/PR
- Publishing to PyPI on version tags
- Separate Test PyPI (qq2) and Production PyPI (qq) releases

### Manual Deployment
```bash
# Build
python -m build

# Test locally
pip install dist/qq-*.whl

# Upload to PyPI
twine upload dist/*
```

## 📊 Architecture

```
quickquestion/
├── qq.py              # Main entry point and CLI
├── llm_lite_provider.py  # LiteLLM integration (100+ providers)
├── settings_manager.py   # Configuration management
├── ui_library.py      # Rich terminal UI components  
├── cache.py           # TTL-based caching system
├── provider_registry.py  # Provider catalog and metadata
├── config_app.py      # Textual TUI for configuration
└── dev_actions/       # Developer mode actions
```

## 🌟 What's New in v0.2.0

- **LiteLLM Integration**: Support for 100+ LLM providers
- **Provider Registry**: Organized catalog of all providers
- **Textual TUI**: Modern configuration interface (`--config`)
- **GPT-5 Support**: Compatible with latest OpenAI models
- **Enhanced Caching**: Improved performance and reliability
- **CI/CD Pipeline**: Automated testing and deployment
- **Bug Fixes**: Provider persistence, model selection, and more

## 🗺️ Roadmap

- [ ] Web UI for configuration
- [ ] Plugin system for extensions
- [ ] Multi-command workflows
- [ ] Command explanation mode
- [ ] Integration with shell history
- [ ] Homebrew formula
- [ ] Docker image
- [ ] VSCode extension

## 📄 License

Proprietary - All rights reserved. See [LICENSE](LICENSE) file.

## 💬 Support & Contact

- **Bug Reports**: [GitHub Issues](https://github.com/yourusername/quickquestion/issues)
- **Feature Requests**: qq@southbrucke.com
- **General Support**: support@southbrucke.com
- **Author**: Cristian Vyhmeister (cv@southbrucke.com)

## 🙏 Acknowledgments

- Built with [LiteLLM](https://github.com/BerriAI/litellm) for universal LLM support
- UI powered by [Rich](https://github.com/Textualize/rich) and [Textual](https://github.com/Textualize/textual)
- Thanks to all contributors and users!

---

**Quick Question** - Your AI-powered command line companion 🚀

[southbrucke.com](https://southbrucke.com) | [Documentation](https://docs.southbrucke.com/qq) | [PyPI](https://pypi.org/project/qq/)