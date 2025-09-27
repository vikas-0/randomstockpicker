#!/usr/bin/env python3
"""Fetch the latest list of NSE equity symbols and write them to data/nse_symbols.json."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Sequence

import requests

API_URL = "https://www.nseindia.com/api/market-data-pre-open?key=ALL"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_symbols(session: requests.Session | None = None) -> List[str]:
    """Return a sorted list of unique NSE equity symbols."""
    http = session or requests.Session()
    response = http.get(API_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    payload = response.json()
    entries = payload.get("data", [])

    symbols = {
        (entry.get("metadata") or {}).get("symbol", "").strip()
        for entry in entries
    }

    return sorted(symbol for symbol in symbols if symbol)


def write_symbols_file(symbols: Sequence[str], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": API_URL,
        "updated_at": datetime.now(timezone.utc).replace(microsecond=False).isoformat(),
        "symbol_count": len(symbols),
        "symbols": list(symbols),
    }
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    try:
        symbols = fetch_symbols()
    except requests.RequestException as exc:  # pragma: no cover - CLI tool
        raise SystemExit(f"Unable to fetch NSE symbols: {exc}") from exc

    output_path = Path(__file__).resolve().parents[1] / "data" / "nse_symbols.json"
    write_symbols_file(symbols, output_path)
    print(f"Saved {len(symbols)} symbols to {output_path}")


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
