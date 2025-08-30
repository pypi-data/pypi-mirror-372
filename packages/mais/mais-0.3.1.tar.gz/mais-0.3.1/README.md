# MAIS - ML Model Audit & Inspection System

A Python notebook plugin that watches for potentially risky model or dataset loads in Jupyter notebooks. MAIS analyzes code in real-time to detect when you're trying to load models that might require special permissions or licensing.

## Installation

```bash
# Using pip
pip install mais
```

```python
# Import and initialize the MAIS plugin
from mais import MAIS

m = MAIS(api_token="<manifest-api-token>")
# Now run your notebook as normal
# MAIS will monitor for potentially risky model loads
```

## SBOM Generation

```python
# Generate an SBOM for your project or notebook environment.
m.create_sbom(path=".", publish=False)
```

## SBOM Publishing
```python
m.create_sbom(path=".", publish=True)
```

## Environment Variables

MAIS supports configuration through environment variables:
- `MANIFEST_API_TOKEN` - API token for MOSAIC/Manifest integration
- `MAIS_MOSAIC_API_URL` - Override default API URL
- `MAIS_DEFAULT_VERBOSITY` - Set default logging level
- `MAIS_API_TIMEOUT` - API request timeout in seconds

All configuration values can be overridden with `MAIS_` prefix.
