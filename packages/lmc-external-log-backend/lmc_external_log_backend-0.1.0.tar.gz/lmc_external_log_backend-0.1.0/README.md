# LMCache External Log Backend

This project provides an external logging backend implementation for LMCache.

## Features
- Implements the `StorageBackendInterface` from LMCache
- Logs all backend operations (put, get, prefetch, pin, etc.)
- Easy to integrate with existing LMCache systems

## Installation

```bash
pip install lmc_external_log_backend
```

## Usage

To use this backend in your LMCache configuration:

1. Add the following to your LMCache extra_config:
```json
{
  "external_backend.log_backend": {
    "module_path": "lmc_external_log_backend",
    "class_name": "ExternalLogBackend"
  }
}
```

2. Enable external backends in your LMCache config:
```python
config.external_backends = ["log_backend"]
```

## Development

To build the package:
```bash
python setup.py sdist bdist_wheel
```

To install locally:
```bash
pip install -e .
```

## License
Apache-2.0 License