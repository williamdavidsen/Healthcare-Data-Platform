from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests

CDC_CATALOG_URL = "https://api.us.socrata.com/api/catalog/v1"
DEFAULT_OUTPUT = Path("data/raw/cdc_catalog.json")


def fetch_cdc_catalog(limit: int = 100, search: str | None = None) -> list[dict[str, Any]]:
    params = {
        "domains": "data.cdc.gov",
        "search_context": "data.cdc.gov",
        "limit": limit,
    }
    if search:
        params["search"] = search
    response = requests.get(CDC_CATALOG_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    return payload.get("results", [])


def fetch_cdc_resource(resource_id: str, limit: int = 1000) -> list[dict[str, Any]]:
    response = requests.get(
        f"https://data.cdc.gov/resource/{resource_id}.json",
        params={"$limit": limit},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def write_json(rows: list[dict[str, Any]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Download CDC Socrata catalog or resource rows.")
    parser.add_argument("--resource-id", help="CDC Socrata resource id, for example abcd-1234")
    parser.add_argument("--search")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    rows = (
        fetch_cdc_resource(args.resource_id, limit=args.limit)
        if args.resource_id
        else fetch_cdc_catalog(limit=args.limit, search=args.search)
    )
    output_path = write_json(rows, args.output)
    print(f"Wrote {len(rows)} CDC rows to {output_path}")


if __name__ == "__main__":
    main()
