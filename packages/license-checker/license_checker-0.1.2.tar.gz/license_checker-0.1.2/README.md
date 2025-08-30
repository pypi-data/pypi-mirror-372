## import-license-checker

Scan Python source trees for imports, map them to installed distributions, and report each package's license in a table or JSON. Useful for CI/CD license compliance gates and quick audits.

### Features
- Detects top-level imports across a project (recursively, ignoring common build/venv folders)
- Maps modules to installed distributions and aggregates license metadata
- Outputs a readable table or machine-friendly JSON
- Exit codes suitable for CI gating
- Optional helpers for discovering `.env` files and summarizing their key/value pairs

## Installation

### From PyPI
```bash
pip install import-license-checker
```

Requires Python 3.8+.

## Usage

### Basic scan
```bash
import-license-checker --path .
```

### JSON output
```bash
import-license-checker --path . --format json
```

### Discover .env-like files (filenames only)
```bash
import-license-checker --path . --simulate-env
```

### Summarize .env key/value pairs
```bash
import-license-checker --path . --env-summary
```

### CLI help
```bash
import-license-checker --help
```

## Exit codes (for CI)
- 0: all detected licenses are allowed
- 1: at least one dependency is marked deny
- 2: at least one dependency has unknown status

License policy is heuristic: permissive/business-friendly terms like MIT, Apache-2.0, BSD-2/3, ISC, MPL-2.0, PSF, Boost, Zlib, Unlicense, and Public Domain are treated as OK. Others are marked deny for review.

## Expected output

### Table format (default)
```text
MODULE    | DISTRIBUTIONS | LICENSE                                 | STATUS
----------+---------------+-----------------------------------------+-------
requests  | requests      | Apache Software License                  | ok
numpy     | numpy         | BSD License                             | ok
pkgutil   | -             | <stdlib or local>                        | ok
somepkg   | somepkg       | Proprietary License                      | deny
```

### JSON format
```json
[
  {
    "module": "requests",
    "distributions": ["requests"],
    "license": "Apache Software License",
    "status": "ok"
  },
  {
    "module": "somepkg",
    "distributions": ["somepkg"],
    "license": "Proprietary License",
    "status": "deny"
  }
]
```

## Programmatic use (optional)
```python
from import_license_checker.scanner import find_imports_in_tree
from import_license_checker.license_meta import build_license_report, print_report

modules = find_imports_in_tree(".")
report = build_license_report(modules)
print_report(report, fmt="table")  # or fmt="json"
```

## License
MIT
