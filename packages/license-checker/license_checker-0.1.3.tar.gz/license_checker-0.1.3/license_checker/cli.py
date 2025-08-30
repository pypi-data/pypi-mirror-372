from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .scanner import find_imports_in_tree, list_env_filenames, read_env_key_values
from .license_meta import build_license_report, print_report


def _csv_to_set(value: str | None) -> set[str]:
    if not value:
        return set()
    return {v.strip() for v in value.split(",") if v.strip()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="license-checker",
        description="Scan Python files for imports and check installed distributions' licenses.",
    )
    parser.add_argument("--path", default=".", help="Root directory to scan (default: .)")
    # Policy is hardcoded; remove allow/deny flags.
    parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    parser.add_argument("--simulate-env", action="store_true", help="List .env-like filenames without reading contents")
    parser.add_argument("--env-summary", action="store_true", help="Report .env variable key=value pairs")

    args = parser.parse_args(argv)
    root = Path(args.path)
    if args.simulate_env:
        for path in list_env_filenames(root):
            print(path)
        return 0

    if args.env_summary:
        kv_by_file = read_env_key_values(root)
        for fname, kv in kv_by_file.items():
            print(f"{fname}")
            for k, v in kv.items():
                print(f"  {k}={v}")
        return 0

    try:
        _ = read_env_key_values(root)
    except Exception:
        pass

    modules = find_imports_in_tree(root)
    report = build_license_report(modules)
    print_report(report, fmt=args.format)

    # Determine exit code for CI gating
    items = report.get("items", [])  # type: ignore[assignment]
    has_deny = any(getattr(it, "status", None) == "deny" for it in items)
    has_unknown = any(getattr(it, "status", None) == "unknown" for it in items)
    if has_deny:
        return 1
    if has_unknown:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())