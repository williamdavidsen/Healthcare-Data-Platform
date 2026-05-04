from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests

WHO_GHO_BASE_URL = "https://ghoapi.azureedge.net/api"
DEFAULT_OUTPUT = Path("data/raw/who_indicators.json")


def fetch_who_indicators(limit: int = 100) -> list[dict[str, Any]]:
    response = requests.get(f"{WHO_GHO_BASE_URL}/Indicator", timeout=30)
    response.raise_for_status()
    payload = response.json()
    return payload.get("value", [])[:limit]


def fetch_who_indicator_values(indicator_code: str, limit: int = 1000) -> list[dict[str, Any]]:
    response = requests.get(f"{WHO_GHO_BASE_URL}/{indicator_code}", timeout=60)
    response.raise_for_status()
    payload = response.json()
    return payload.get("value", [])[:limit]


def write_json(rows: list[dict[str, Any]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Download WHO GHO metadata or indicator values.")
    parser.add_argument("--indicator", help="WHO indicator code to download values for")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    rows = (
        fetch_who_indicator_values(args.indicator, limit=args.limit)
        if args.indicator
        else fetch_who_indicators(limit=args.limit)
    )
    output_path = write_json(rows, args.output)
    print(f"Wrote {len(rows)} WHO rows to {output_path}")


if __name__ == "__main__":
    main()
