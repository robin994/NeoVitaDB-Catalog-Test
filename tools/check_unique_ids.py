#!/usr/bin/env python3
"""Check catalog primary keys and referenced asset paths without network access."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    seen = {}
    errors = []
    for path in sorted((ROOT / "apps").glob("**/*.json")):
        if path.name.startswith("_"):
            continue
        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
            platform, entry_id = entry["platform"], entry["id"]
            if not isinstance(entry_id, int) or isinstance(entry_id, bool):
                raise ValueError("id must be an integer")
        except (ValueError, KeyError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        key = (platform, entry_id)
        if key in seen:
            errors.append(f"Duplicate {platform} id {entry_id}: {seen[key]} and {path.relative_to(ROOT)}")
        else:
            seen[key] = path.relative_to(ROOT)
        for filename in [entry.get("icon"), *entry.get("screenshots", [])]:
            if not filename:
                continue
            asset = ROOT / ("icons_vita" if platform == "vita" else "icons_psp") / filename if filename == entry.get("icon") else ROOT / filename
            if not asset.is_file():
                errors.append(f"{path.relative_to(ROOT)}: missing asset {asset.relative_to(ROOT)}")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"OK: {len(seen)} unique platform-scoped IDs and referenced assets validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
