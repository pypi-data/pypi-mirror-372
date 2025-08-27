# Echo SDK

A bridge library for developing plugins for the Echo multi-agent system.

## 🎯 Purpose

- **Clean Interfaces**: Well-defined contracts for plugin development
- **Zero Core Dependencies**: Plugins only depend on the SDK, not the core system
- **Independent Distribution**: Plugins can be distributed as standalone packages
- **Version Management**: Dynamic SDK versioning with compatibility checks
- **Testing Isolation**: Test plugins without running the core system
- **Auto-Registration**: Automatic plugin discovery through global registry
- **Hybrid Discovery**: Support for both pip-installable and directory-based plugins
- **Runtime Dependency Installation**: Automatic installation of plugin dependencies

## 📚 Core Concepts

### Plugin Interface (`BasePlugin`)

Every plugin must implement the `BasePlugin` interface:

- `get_metadata()`: Returns `PluginMetadata` with name, version, capabilities, and LLM requirements
- `create_agent()`: Factory method for creating agent instances
- `validate_dependencies()`: Optional dependency validation
- `health_check()`: Optional health check implementation

### Agent Interface (`BasePluginAgent`)

Every agent must implement the `BasePluginAgent` interface:

- `get_tools()`: Returns list of LangChain tools
- `get_system_prompt()`: Returns the system prompt for the agent
- `bind_model()`: Binds tools to an LLM model (inherited from base class)
- `initialize()`: Initializes the agent
- `cleanup()`: Cleans up agent resources
- `create_agent_node()`: Creates LangGraph node function (inherited from base class)
- `should_continue()`: Decides whether to call tools or return to coordinator (inherited from base class)

### Plugin Registry

The SDK provides a global registry for plugin discovery:

- `register_plugin(plugin_class)`: Register a plugin class with the global registry
- `discover_plugins()`: Discover all registered plugins (used by core system)
- `get_plugin_registry()`: Access the global registry instance

### Plugin Contracts (`PluginContract`)

The bridge between core system and plugins:

- Wraps plugin classes for standardized interaction
- Provides validation and health check interfaces
- Enables communication without direct imports

## 🔧 Advanced Features

### Plugin Discovery

The SDK provides comprehensive plugin discovery capabilities:

```python
from echo_sdk import import_plugins_from_environment, import_plugins_from_directories

# Discover pip-installable plugins only
pip_count = import_plugins_from_environment()

# Discover directory-based plugins
dir_count = import_plugins_from_directories(["./plugins", "./custom_plugins"])
```

### Discovery Functions

```python
from echo_sdk.utils import (
    # Environment discovery
    import_plugins_from_environment,
    get_environment_discovery_summary,
    list_installed_environment_packages,
    list_imported_environment_packages,
    reset_environment_discovery,

    # Directory discovery
    import_plugins_from_directories,
    get_directory_discovery_summary,
    list_loaded_directories,
    list_imported_directory_modules,
    reset_directory_discovery,
)
```

### Directory-Based Plugin Discovery

Enable directory-based plugin loading via environment variables:

```bash
# Enable directory discovery
export ECHO_ENABLE_DIRECTORY_PLUGINS=true

# Configure plugin directories
export ECHO_PLUGIN_DIRS="/path/to/plugins,/another/path"
export ECHO_PLUGIN_DIR="./plugins"
```

### Plugin Validation

The SDK includes comprehensive validation:

```python
from echo_sdk.utils import validate_plugin_structure

errors = validate_plugin_structure(MyPlugin)
if errors:
    print("Plugin validation failed:", errors)
```

### Model Configuration

The SDK provides flexible model configuration through `ModelConfig`:

```python
from echo_sdk.base.metadata import ModelConfig

config = ModelConfig(
    provider="openai",
    model_name="gpt-4o",
    temperature=0.1,
    max_tokens=1024,
    additional_params={"top_p": 0.9}
)
```

### Version Compatibility

Check SDK compatibility:

```python
from echo_sdk.utils import check_compatibility, get_sdk_version

is_compatible = check_compatibility(">=0.1.0,<0.2.0", get_sdk_version())
```

### Health Checks

Implement custom health checks:

```python
class MyPlugin(BasePlugin):
    @staticmethod
    def health_check():
        return {
            "healthy": True,
            "details": "All systems operational"
        }
```

### Runtime Dependency Installation

The SDK supports automatic installation of plugin dependencies:

```python
from echo_sdk.utils import install_packages

# Install dependencies declared in plugin metadata
success, log = install_packages(["requests", "numpy"], prefer_poetry=True)
```

## 📦 Package Structure

```
sdk/
├── src/echo_sdk/           # SDK source code
│   ├── __init__.py         # Main SDK exports with dynamic versioning
│   ├── base/               # Core interfaces
│   │   ├── __init__.py
│   │   ├── agent.py        # BasePluginAgent interface
│   │   ├── plugin.py       # BasePlugin interface
│   │   ├── metadata.py     # PluginMetadata, ModelConfig
│   │   └── loggable.py     # Loggable base class
│   ├── tools/              # Tool utilities
│   │   ├── __init__.py
│   │   ├── decorators.py   # @tool decorator (LangChain tool wrapper)
│   │   └── registry.py     # Tool registry
│   ├── registry/           # Plugin registry system
│   │   ├── __init__.py
│   │   ├── contracts.py    # PluginContract wrapper
│   │   └── plugin_registry.py # Global registry
│   ├── types/              # Type definitions
│   │   ├── __init__.py
│   │   ├── state.py        # AgentState TypedDict
│   │   └── messages.py     # LangChain message types
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   ├── validation.py   # Plugin validation
│   │   ├── helpers.py      # Version compatibility
│   │   ├── environment_discovery.py # Pip plugin discovery
│   │   ├── directory_discovery.py # Directory-based discovery
│   │   └── installers.py   # Runtime dependency installation
│   └── examples/           # Template examples
│       ├── __init__.py
│       └── template_plugin/ # Complete plugin template
├── pyproject.toml          # Package configuration
├── deploy.sh               # Deployment script with dynamic versioning
├── README.md               # This documentation
└── LICENSE                 # MIT license
```

## 🔧 Key Features

### Core Dependencies

- **LangChain Core**: For tool definitions and model binding
- **LangGraph**: For multi-agent orchestration
- **Pydantic**: For data validation and serialization
- **Python 3.13+**: Modern Python features and type hints

### Version Information

- **Current Version**: 0.1.2 (dynamic from pyproject.toml)
- **Python Support**: 3.13+
- **LangChain Core**: >=0.3.74,<0.4.0
- **LangGraph**: >=0.6.5,<0.7.0
- **Pydantic**: >=2.11.7,<3.0.0

### Dynamic Versioning

The SDK uses dynamic versioning that reads from the installed package:

```python
import echo_sdk
print(echo_sdk.__version__)  # Shows actual installed version
```

### Agent State Management

The SDK provides comprehensive state management for multi-agent workflows:

```python
from echo_sdk.types.state import AgentState

# State includes:
# - messages: LangChain message sequence
# - current_agent: Active agent identifier
# - agent_hops: Agent transition counter
# - tool_hops: Tool call counter
# - plugin_context: Plugin-specific context
# - routing_history: Agent routing history
```

## 🔍 Plugin Discovery System

### Automatic Discovery

The SDK automatically discovers plugins through multiple mechanisms:

1. **Environment Discovery**: Automatically detects and imports plugins installed via pip
2. **Directory Discovery**: Scans configured directories for plugin modules
3. **Hybrid Discovery**: Combines both methods for comprehensive plugin coverage

### Discovery Functions

```python
from echo_sdk.utils import (
    # Environment discovery
    import_plugins_from_environment,
    get_environment_discovery_summary,
    list_installed_environment_packages,
    list_imported_environment_packages,
    reset_environment_discovery,

    # Directory discovery
    import_plugins_from_directories,
    get_directory_discovery_summary,
    list_loaded_directories,
    list_imported_directory_modules,
    reset_directory_discovery,
)
```

### Discovery Statistics

Get comprehensive discovery information:

```python
from echo_sdk.utils import get_environment_discovery_summary, get_directory_discovery_summary

env_stats = get_environment_discovery_summary()
dir_stats = get_directory_discovery_summary()

print(f"Environment plugins: {env_stats['imported_count']}")
print(f"Directory plugins: {dir_stats['imported_count']}")
```

### Environment Configuration

The SDK supports environment-based configuration for plugin discovery:

```bash
# Enable directory-based plugin discovery
export ECHO_ENABLE_DIRECTORY_PLUGINS=true

# Configure plugin directories (comma-separated)
export ECHO_PLUGIN_DIRS="/path/to/plugins,/another/path"

# Set default plugin directory
export ECHO_PLUGIN_DIR="./plugins"

# Configure agent behavior
export ECHO_MAX_AGENT_HOPS=5
export ECHO_MAX_TOOL_HOPS=25
```

## 🧪 Testing

Test your plugins in isolation using SDK contracts:

```python
import pytest
from echo_sdk import PluginContract, discover_plugins
from echo_sdk.utils import validate_plugin_structure


def test_my_plugin():
    # Test plugin structure
    errors = validate_plugin_structure(MyPlugin)
    assert not errors, f"Plugin validation failed: {errors}"

    # Test plugin contract
    contract = PluginContract(MyPlugin)
    assert contract.is_valid()

    # Test metadata
    metadata = contract.get_metadata()
    assert metadata.name == "my_plugin"
    assert metadata.version

    # Test agent creation
    agent = contract.create_agent()
    tools = agent.get_tools()
    assert len(tools) > 0

    # Test health check
    health = contract.health_check()
    assert health.get("healthy", False)


def test_plugin_discovery():
    # Test that plugin is discoverable via SDK
    plugins = discover_plugins()
    plugin_names = [p.name for p in plugins]
    assert "my_plugin" in plugin_names


def test_discovery_reset():
    # Test discovery state management
    from echo_sdk.utils import reset_environment_discovery, reset_directory_discovery

    # Reset discovery state
    reset_environment_discovery()
    reset_directory_discovery()

    # Rediscover plugins
    env_count = import_plugins_from_environment()
    dir_count = import_plugins_from_directories(["./plugins"])
    assert env_count >= 0
    assert dir_count >= 0


def test_agent_interface():
    """Test that agent implements required interface."""
    agent = MyAgent(MyPlugin.get_metadata())
    
    # Test required methods
    assert hasattr(agent, 'get_tools')
    assert hasattr(agent, 'get_system_prompt')
    assert hasattr(agent, 'initialize')
    assert hasattr(agent, 'cleanup')
    
    # Test tool binding
    tools = agent.get_tools()
    assert isinstance(tools, list)
    assert all(hasattr(tool, 'name') for tool in tools)
```

## 📋 Plugin Template

The SDK includes a complete plugin template at `examples/template_plugin/` with:

- **Proper Project Structure**: Standard plugin package layout
- **Complete Implementation**: All required methods and interfaces
- **Documentation**: Comprehensive docstrings and examples
- **Validation Examples**: Dependency and health check implementations
- **Tool Examples**: Multiple tool types and patterns

### Template Features

The template plugin demonstrates:

```python
# Complete metadata with all fields
PluginMetadata(
    name="template_plugin",
    version="0.1.0",
    description="Template plugin demonstrating Echo SDK usage",
    capabilities=["example_capability", "template_operation", "sdk_demonstration"],
    llm_requirements={
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.1,
        "max_tokens": 1024,
    },
    agent_type="specialized",
    dependencies=["echo_sdk>=1.0.0,<2.0.0"],
)

# Dependency validation
@staticmethod
def validate_dependencies() -> list[str]:
    errors = []
    try:
        import echo_sdk
    except ImportError:
        errors.append("echo_sdk is required")
    return errors

# Health check implementation
@staticmethod
def health_check() -> dict:
    return {
        "healthy": True,
        "details": "Template plugin is operational",
        "checks": {"dependencies": "OK", "configuration": "OK"},
    }
```

Study this template to understand best practices for SDK-based plugin development.

## 🚀 Deployment

The SDK includes a comprehensive deployment script with dynamic versioning:

```bash
cd /path/to/echo_ai/sdk
./deploy.sh
```

### Deployment Features

- **Dynamic Version Bumping**: Interactive patch/minor/major version selection
- **Pre-deployment Checks**: Git status, poetry installation, build verification
- **Colored Output**: Clear status indicators and progress feedback
- **Optional Git Tagging**: Automatic version tagging with push reminders
- **Build Verification**: Ensures successful package building before upload

### Version Management

The deployment script shows dynamic version progression:

```
Current version in pyproject.toml: 0.1.2
Currently installed version: 0.1.2

Select version bump type:
1) patch (0.1.2 -> 0.1.2)
2) minor (0.1.2 -> 0.2.0)
3) major (0.1.2 -> 1.0.0)
4) Skip version bump
```

## 🔒 Security Features

The SDK provides security boundaries and validation:

- **Plugin Structure Validation**: Comprehensive validation of plugin interfaces and implementations
- **Dependency Checking**: Validates plugin dependencies and SDK version compatibility
- **Safe Tool Execution**: Tool validation and type checking for safe execution
- **Version Compatibility**: Semantic version checking and compatibility enforcement
- **Health Monitoring**: Plugin health checks and failure detection
- **Contract Isolation**: Clean boundaries between core system and plugins
- **Discovery Isolation**: Separate discovery managers prevent cross-contamination

## 📈 Version Compatibility

The SDK uses semantic versioning and provides compatibility checking:

```python
from echo_sdk.utils import check_compatibility, get_sdk_version

# Check if plugin's SDK requirement is compatible
is_compatible = check_compatibility(">=0.1.0", get_sdk_version())

# Plugin metadata should specify SDK requirements
PluginMetadata(
    name="my_plugin",
    sdk_version=">=0.1.0",  # SDK version requirement
    # ...
)
```

## 🔗 Related Components

- **[Echo Core](https://github.com/jonaskahn/echo-ai)**: Core multi-agent orchestration system
- **[Echo Plugins](https://github.com/jonaskahn/echo-plugins)**: Example plugins and templates using this SDK

## 🚀 Code Quality

The SDK follows modern Python best practices:

- **KISS Principle**: Keep It Simple, Stupid - clean, focused methods
- **DRY Principle**: Don't Repeat Yourself - reusable components
- **Self-Documenting Code**: Meaningful names, no redundant comments
- **Consistent Formatting**: Black formatter for consistent style
- **Type Hints**: Full type annotations for better IDE support
- **Comprehensive Testing**: Thorough test coverage for all functionality

### Contribution Process

When contributing to the SDK:

1. **Fork and Branch**: Create a feature branch from main
2. **Setup Environment**: Use shared environment (recommended) or individual setup
3. **Follow Standards**: Use existing code style and patterns
4. **Add Tests**: Include tests for new features or bug fixes
5. **Quality Checks**: Run `pytest`, `black`, `mypy`, etc.
6. **Update Documentation**: Keep README and docstrings current
7. **Test Compatibility**: Ensure existing plugins still work
8. **Submit PR**: Create a pull request with clear description

### Development Commands

```bash
# With shared environment active
pytest              # Run tests
black src/          # Format code
mypy src/           # Type checking
ruff check src/     # Linting

# Test plugin compatibility
pytest examples/template_plugin/

# Test discovery functionality
python -c "from echo_sdk.utils import import_plugins_from_environment; print(import_plugins_from_environment())"
```

## 📄 License

MIT License - see main project LICENSE file for details.
