# FilerX

**Universal Config Loader for Python (JSON/YAML/TOML) with Nested Keys, Merge, and File Watcher)**

---

## Overview

FilerX is a professional Python library designed for developers and DevOps engineers who need a **robust, flexible, and easy-to-use configuration management tool**. It supports multiple config formats (JSON, YAML, TOML), automatic format detection, nested key access, file merging, and real-time file watching.

### Key Features

- **Universal Config Loader**: Load JSON, YAML, or TOML files without worrying about file extensions.
- **Nested Keys & Dot Notation**: Access or modify deeply nested keys easily (`database.connections.0.host`).
- **Merge Multiple Files**: Combine multiple config files while preserving structure.
- **Auto-Detect & Auto-Fix**: Automatically detect file formats and fix minor syntax issues.
- **File Watcher**: Monitor files for changes and reload automatically.
- **Extensible**: Add support for custom config formats.
- **Python 3.8+** compatible.

---

## Installation

Install FilerX using pip:

```bash
pip install filerx
```

Or clone the repository and install locally:

```bash
git clone https://github.com/iTs-GoJo/FilerX.git
cd FilerX
pip install .
```

Optional extras:
```bash
pip install .[dev]
pip install .[watch]
```

- `dev`: For development tools (pytest, black, mypy)
- `watch`: Enhances file watcher capabilities with `watchdog`

---

## Usage

### Basic Usage

```python
from filerx import FilerX

# Load a config file (any extension)
config = FilerX("settings.data")

# Access nested key
host = config.get("database.connections.0.host", default="localhost")
print(host)

# Set nested key
config.set("api.tokens.google", "ABC123")

# Merge another config
config.merge("extra_settings.yml")

# Save the updated config
config.save("settings_fixed.data")
```

### Watcher Example

```python
config = FilerX("settings.data", watch=True)
# The config will auto-reload when the file changes
```

### Accessing Nested Arrays

```python
servers = config.get("servers")
first_ip = config.get("servers.0.ip")
config.set("servers.1.ip", "192.168.1.2")
```

### Dynamic Format Extension

```python
from filerx.parser import register_format

# Example: Custom parser for a new config format
register_format("custom", lambda content: my_custom_parser(content))
```

---

## Keywords

`config, loader, json, yaml, toml, nested keys, merge, watcher, settings, file manager, auto-detect, auto-fix, config parser, configuration, devops, python config, config utils, dynamic config, data loader, config merger, json yaml toml, config handler, nested config, file watcher, configuration manager, python library, config editor, config automation, file parser, config toolkit`

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please submit issues or pull requests via GitHub.

- Use `dev` extras for running tests and formatting: `pip install .[dev]`
- Ensure all code is formatted with `black` and type-checked with `mypy` before submitting.

---

## Contact

For questions or support, contact **Ali Jafari** at `thealiapi@gmail.com`.

GitHub: [https://github.com/iTs-GoJo/FilerX](https://github.com/iTs-GoJo/FilerX)