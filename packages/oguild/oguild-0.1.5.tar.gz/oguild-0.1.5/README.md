██████╗ ██╗ ██╗██╗██╗ ██████╗ ██████╗ ██████╗ ██╗ ██╗██████╗
██╔════╝ ██║ ██║██║██║ ██╔═══██╗██╔══██╗██╔═══██╗██║ ██╔╝██╔══██╗
██║ ███╗██║ ██║██║██║ ██║ ██║██║ ██║██║ ██║█████╔╝ ██████╔╝
██║ ██║██║ ██║██║██║ ██║ ██║██║ ██║██║ ██║██╔═██╗ ██╔═══╝
╚██████╔╝╚██████╔╝██║███████╗ ╚██████╔╝██████╔╝╚██████╔╝██║ ██╗██║  
 ╚═════╝ ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚═╝ ╚═╝╚═╝

                    🚀 Multi-Language Utilities Pack 🚀
                    🐍 Python • 🔷 Node.js • 🦀 Rust • 🐹 Go
                    ☕ Java • 🔵 C# • 🐘 PHP • 🦎 Python
                    📦 Configuration • 🔍 Monitoring • 🛠️ Operations

# OpsGuild Utilities Pack

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/Poetry-1.0+-blue.svg)](https://python-poetry.org/)

A comprehensive multi-language utilities pack providing essential tools and helper functions for modern software development. Currently featuring Python utilities with plans to expand to multiple programming languages.

## 🚀 What is OpsGuild Pack?

OpsGuild Pack is a collection of utility libraries designed to solve common development challenges across different programming languages and platforms. Think of it as your Swiss Army knife for software development operations.

### Current Components

- **🐍 [Python Logger Package](python/oguild/logs/README.md)** - Enhanced logging, helpers, and utilities
- **🔮 More Coming Soon** - Go, Rust, and other language support planned

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- Poetry (recommended) or pip

### Using Poetry (Recommended)

```bash
poetry add oguild
```

### Using pip

```bash
pip install oguild
```

## 🎯 Quick Start

### Python Logger (Current Package)

```python
from oguild.logs import logger

# Simple logging
logger.info("Hello, World!")
logger.debug("Debug information")

# The logger automatically detects the module name
# Output: INFO: (your_module_name) == Hello, World! [timestamp]
```

**📖 [Full Python Logger Documentation](python/oguild/logs/README.md)**

## 🤝 Contributing

We welcome contributions across all planned languages! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone and setup
git clone https://github.com/OpsGuild/guildpack.git
cd guildpack

# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest
```

### Contributing to New Languages

When contributing utilities for new languages:

1. Create a new directory for the language (e.g., `javascript/`, `go/`, `rust/`)
2. Follow the established project structure
3. Include comprehensive tests
4. Create a dedicated README.md for the package
5. Update this main README with links to the new package
6. Ensure consistent API design across languages

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/OpsGuild/guildpack/issues)
- **Documentation**: [GitHub README](https://github.com/OpsGuild/guildpack#readme)
- **Team**: OpsGuild <Hordunlarmy@gmail.com>

## 🔄 Changelog

### Version 0.1.4

- Initial release with Python logging utilities
- Smart logger with automatic formatting
- Logstash integration support
- Multi-output logging (console, file, logstash)
- Automatic module detection
- Foundation for multi-language utilities pack

## 🌟 Why OpsGuild Pack?

OpsGuild Pack is designed to solve common development challenges across multiple programming languages:

- **Multi-Language Support** - Consistent utilities across different tech stacks
- **Production Ready** - Built with enterprise needs in mind
- **Developer Friendly** - Automatic configuration and intelligent defaults
- **Extensible** - Easy to customize and extend for specific use cases
- **Performance** - Efficient utilities with minimal overhead
- **Standards Compliant** - Follows best practices for each language
- **Unified Experience** - Consistent API design across all supported languages

## 🎯 Use Cases

- **Microservices Architecture** - Consistent logging and monitoring across services
- **Polyglot Teams** - Unified utilities regardless of language choice
- **DevOps & SRE** - Standardized operational tools across infrastructure
- **Enterprise Development** - Consistent patterns for large-scale applications
- **Open Source Projects** - Reusable utilities for community projects

---

**Made with ❤️ by the OpsGuild team**
