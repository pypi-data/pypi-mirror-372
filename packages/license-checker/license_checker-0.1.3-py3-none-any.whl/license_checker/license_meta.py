from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

try:  
    from importlib.metadata import (
        packages_distributions,  
        metadata,
        PackageNotFoundError,
        Distribution,
        distributions,
    )
except Exception:
    from importlib_metadata import (
        packages_distributions,  
        metadata,
        PackageNotFoundError,
        Distribution,
        distributions,
    )  


def _fallback_packages_distributions() -> Mapping[str, List[str]]:
    mapping: Dict[str, List[str]] = {}
    for dist in distributions():
        top_levels: List[str] = []
        try:
            tl = dist.read_text("top_level.txt")
            if tl:
                top_levels = [line.strip() for line in tl.splitlines() if line.strip()]
        except Exception:
            top_levels = []
        for top in top_levels:
            mapping.setdefault(top, []).append(dist.metadata["Name"])  
    return mapping


def _get_packages_distributions() -> Mapping[str, List[str]]:
    try:
        mapping = packages_distributions()  
        if isinstance(mapping, dict) and mapping:
            return mapping
    except Exception:
        pass
    return _fallback_packages_distributions()


def _license_from_metadata(dist_name: str) -> str:
    try:
        md = metadata(dist_name)
    except PackageNotFoundError:
        return "<not installed>"
    license_text = md.get("License") or ""
    # Also collect license classifiers
    classifiers = [c for c in md.get_all("Classifier", []) if c.startswith("License :: ")]
    if classifiers:
        # Compress classifier list into a single string
        classifier_leafs = [c.split("::")[-1].strip() for c in classifiers]
        classifier_text = ", ".join(sorted(set(classifier_leafs)))
        if license_text:
            return f"{license_text} | {classifier_text}"
        return classifier_text
    return license_text or "<unknown>"


@dataclass
class LicenseItem:
    module: str
    distributions: List[str]
    license: str
    status: str  # ok | deny | unknown

TRUSTED_LICENSE_TERMS: Set[str] = {
    # Common permissive / business-friendly licenses and classifier leafs
    "mit",
    "apache-2.0",
    "apache software license",
    "bsd-3-clause",
    "bsd license",
    "bsd-2-clause",
    "isc",
    "mpl-2.0",
    "python software foundation license",
    "python-2.0",
    "boost software license",
    "zlib",
    "unlicense",
    "public domain",
}


def build_license_report(modules: Iterable[str]) -> Dict[str, List[LicenseItem]]:
    pkg_map = _get_packages_distributions()
    items: List[LicenseItem] = []
    for mod in sorted(set(modules)):
        dists = pkg_map.get(mod, [])
        if not dists:
            items.append(LicenseItem(module=mod, distributions=[], license="<stdlib or local>", status="ok"))
            continue
        # Many modules map to one dist; sample the first for license signal
        licenses = [_license_from_metadata(d) for d in dists]
        # Merge licenses for readability
        license_text = "; ".join(sorted(set(licenses))) if licenses else "<unknown>"

        norm = license_text.lower()
        status = "ok" if any(term in norm for term in TRUSTED_LICENSE_TERMS) else "deny"

        items.append(LicenseItem(module=mod, distributions=dists, license=license_text, status=status))

    return {"items": items}


def print_report(report: Dict[str, List[LicenseItem]], fmt: str = "table") -> None:
    items: List[LicenseItem] = report.get("items", [])  # type: ignore[assignment]
    if fmt == "json":
        print(json.dumps([
            {
                "module": it.module,
                "distributions": it.distributions,
                "license": it.license,
                "status": it.status,
            }
            for it in items
        ], indent=2))
        return

    # table format
    rows = [("MODULE", "DISTRIBUTIONS", "LICENSE", "STATUS")]
    for it in items:
        rows.append((
            it.module,
            ", ".join(it.distributions) if it.distributions else "-",
            it.license,
            it.status,
        ))

    widths = [
        max(len(r[i]) for r in rows) for i in range(4)
    ]
    for idx, row in enumerate(rows):
        line = " | ".join(val.ljust(widths[i]) for i, val in enumerate(row))
        print(line)
        if idx == 0:
            print("-+-".join("-" * w for w in widths))


