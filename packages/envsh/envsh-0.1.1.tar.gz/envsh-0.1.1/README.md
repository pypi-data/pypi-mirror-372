# Envsh

A Python library for loading environment variables from shell scripts with **variable interpolation** and type-safe reading capabilities.

## Key Advantage: Variable Interpolation

Unlike traditional `.env` files, **envsh uses shell scripts** which support full variable interpolation, calculations, and dynamic configurations:

```bash
# ❌ This WON'T work in .env files:
DATABASE_URL=postgresql://$HOST:5432/$DB_NAME
WORKER_PORTS=$BASE_PORT,$(($BASE_PORT + 1)),$(($BASE_PORT + 2))

# ✅ This WORKS with envsh (.sh files):
export HOST="localhost" 
export DB_NAME="myapp"
export BASE_PORT=8000

export DATABASE_URL="postgresql://$HOST:5432/$DB_NAME"
export WORKER_PORTS="$BASE_PORT,$(($BASE_PORT + 1)),$(($BASE_PORT + 2))"
export CONFIG_ARRAY="value1,$HOST,value3,port-$BASE_PORT"
```

## Features

- **Variable Interpolation**: Use `$VAR` and `${VAR}` syntax like in shell scripts
- **Shell Calculations**: Support for `$((...))` arithmetic and `$(command)` execution
- **Type-safe Reading**: Convert to `int`, `float`, `str`, `list[int]`, `list[str]` with validation
- **Smart Array Parsing**: Comma-separated values with automatic trimming
- **Multi-directory Search**: Load from multiple directories automatically
- **Error Handling**: Clear error messages for debugging

## Installation

```bash
pip install envsh
```

## Quick Start: Variable Interpolation

1. Create a shell script with interpolated variables:

```bash
# config.sh
export HOST="localhost"
export BASE_PORT=8000
export DB_NAME="myapp"

# Variable interpolation - the main advantage!
export DATABASE_URL="postgresql://$HOST:5432/$DB_NAME"
export API_ENDPOINT="http://$HOST:$BASE_PORT/api"
export WORKER_PORTS="$BASE_PORT,$(($BASE_PORT + 1)),$(($BASE_PORT + 2))"
export SERVICE_URLS="http://$HOST:$BASE_PORT,https://$HOST:8443"
```

2. Load and use with type safety:

```python
import envsh

# Load environment variables with interpolation
envsh.load()

# Read interpolated values
database_url = envsh.read_env('DATABASE_URL', str)
# Result: "postgresql://localhost:5432/myapp"

worker_ports = envsh.read_env('WORKER_PORTS', list[int])  
# Result: [8000, 8001, 8002] - calculated from BASE_PORT!

service_urls = envsh.read_env('SERVICE_URLS', list[str])
# Result: ["http://localhost:8000", "https://localhost:8443"]
```

## Comparison with .env Files

| Feature | `.env` files | `envsh` (shell scripts) |
|---------|-------------|-------------------------|
| Variable interpolation | ❌ No | ✅ Full support |
| Calculations | ❌ No | ✅ `$(($VAR + 1))` |
| Command execution | ❌ No | ✅ `$(date)`, `$(nproc)` |
| Dynamic arrays | ❌ No | ✅ `"$VAR1,$VAR2,suffix"` |
| Type safety | ❌ Strings only | ✅ int, float, str, list[int], list[str] |
| Array parsing | ❌ Manual | ✅ Automatic comma-split |

## API Reference

### `load(search_paths=None, verbose=False)`

Loads environment variables from `.sh` files in the specified directories.

**Parameters:**
- `search_paths` (list[str], optional): Directories to search for `.sh` files. Defaults to `['.', '..']`
- `verbose` (bool, optional): Print information about loaded files. Defaults to `False`

**Example:**
```python
# Load from current and parent directory
envsh.load()

# Load from specific directories
envsh.load(['./config', './env'], verbose=True)
```

### `read_env(name, return_type)`

Reads an environment variable with the specified type.

**Parameters:**
- `name` (str): Name of the environment variable
- `return_type` (Type): Expected return type (`int`, `float`, `str`, `list[int]`, or `list[str]`)

**Returns:**
- The environment variable value converted to the specified type

**Raises:**
- `EnvironmentError`: If the environment variable is not set
- `ValueError`: If the value cannot be converted to the specified type
- `TypeError`: If the return type is not supported

**Examples:**
```python
# Read as integer
port = envsh.read_env('PORT', int)

# Read as string
host = envsh.read_env('HOST', str)

# Read as integer array (comma-separated)
ports = envsh.read_env('PORTS', list[int])  # "8000,8001,8002" -> [8000, 8001, 8002]

# Read as string array (comma-separated)
hosts = envsh.read_env('HOSTS', list[str])  # "localhost,example.com" -> ["localhost", "example.com"]
```

## Variable Interpolation Examples

### Basic Interpolation
```bash
export HOST="localhost"
export PORT=8000
export API_URL="http://$HOST:$PORT/api"  # → "http://localhost:8000/api"
```

### Arrays with Interpolation
```bash
export BASE_PORT=8000
export SERVICES="web:$BASE_PORT,api:$(($BASE_PORT + 1)),ws:$(($BASE_PORT + 2))"
# → ["web:8000", "api:8001", "ws:8002"]
```

### Dynamic Configuration
```bash
export ENV="production"
export LOG_LEVEL="INFO"
export CONFIG_NAME="app-$ENV-$(date +%Y%m%d)"  # → "app-production-20250811"
export WORKER_COUNT=$(nproc)  # → Number of CPU cores
```

## Error Handling

The library provides clear error messages for common issues:

```python
# Missing environment variable
try:
    value = envsh.read_env('MISSING_VAR', str)
except EnvironmentError as e:
    print(f"Variable not found: {e}")

# Invalid integer conversion
os.environ['INVALID_NUMBER'] = 'not_a_number'
try:
    number = envsh.read_env('INVALID_NUMBER', int)
except ValueError as e:
    print(f"Conversion error: {e}")

# Unsupported type
try:
    value = envsh.read_env('SOME_VAR', dict)
except TypeError as e:
    print(f"Type error: {e}")
```

## Use Cases

- **Configuration Management**: Load application configuration from shell scripts
- **Development Environments**: Share environment setup across team members
- **CI/CD Pipelines**: Load environment-specific variables from shell scripts
- **Docker Deployments**: Initialize container environments from shell scripts

## Requirements

- Python 3.11+
- Unix-like system with Bash (Linux, macOS)
- Windows: Git Bash or MSYS2

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
