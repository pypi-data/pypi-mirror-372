# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python memcached client library that supports both synchronous and asynchronous operations using memcached's meta commands. The project uses uv for dependency management and packaging.

## Key Architecture

- **Core Components**: `Memcache` (sync), `AsyncMemcache` (async), `MetaCommand` for protocol handling
- **Serialization**: Custom serialization in `serialize.py` with support for bytes, int, str, and pickle
- **Connection Management**: Separate connection classes for sync (`Connection`) and async (`AsyncConnection`)
- **Error Handling**: `MemcacheError` and `SerializeError` exceptions

## Development Commands

**Install dependencies:**
```bash
uv sync
```

**Run tests:**
```bash
uv run pytest
```

**Run specific test file:**
```bash
uv run pytest tests/test_client.py
```

**Run specific test function:**
```bash
uv run pytest tests/test_client.py::test_set_get -v
```

**Linting and formatting:**
```bash
uv run black .
uv run flake8 .
uv run mypy .
```

**Build package:**
```bash
uv build
```

**Install in development mode:**
```bash
uv pip install -e .
```

## Testing

Tests are located in `/tests/` and use pytest with pytest-asyncio for async tests. Tests assume a memcached server running on `localhost:11211`.

## Documentation

Documentation uses Sphinx and can be built with:
```bash
cd docs && make html
```

## Dependencies

- **Runtime**: `hashring>=1.5.1,<2`
- **Development**: `flake8`, `black`, `mypy`, `pytest`, `pytest-asyncio`
- **Documentation**: `furo` (Sphinx theme)

## Important Files

- `memcache/memcache.py` - Synchronous client implementation
- `memcache/async_memcache.py` - Asynchronous client implementation  
- `memcache/meta_command.py` - Meta command protocol implementation
- `memcache/serialize.py` - Serialization utilities
- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Locked dependencies