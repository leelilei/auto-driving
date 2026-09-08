#!/usr/bin/env python3
"""Download the frozen HIPP.json dataset from LLMAP repository.

Commit: 281f6ad95f42ca386400e5288f006aeffa2ac282
Source: https://github.com/liangqiyuan/LLMAP/blob/281f6ad95f42ca386400e5288f006aeffa2ac282/dataset/HIPP.json
"""

import hashlib
import json
import urllib.request
from pathlib import Path

FROZEN_COMMIT = "281f6ad95f42ca386400e5288f006aeffa2ac282"
RAW_URL = f"https://raw.githubusercontent.com/liangqiyuan/LLMAP/{FROZEN_COMMIT}/dataset/HIPP.json"

ROOT_DIR = Path(__file__).resolve().parents[1]  # points to 9-AutoDriving-core
DEST_DIR = ROOT_DIR / "data" / "raw"
DEST_FILE = DEST_DIR / "HIPP.json"
CHECKSUM_FILE = DEST_DIR / "HIPP_checksum.json"


def main():
    print(f"Downloading frozen HIPP.json from commit {FROZEN_COMMIT[:8]}...")
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": "Mozilla/5.0 DARC-RouteDataCollector/1.0"}
    req = urllib.request.Request(RAW_URL, headers=headers)

    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read()

    DEST_FILE.write_bytes(content)
    size_kb = len(content) / 1024
    sha256 = hashlib.sha256(content).hexdigest()

    data = json.loads(content.decode("utf-8"))
    count = len(data)

    metadata = {
        "dataset": "HIPP.json",
        "source_repo": "https://github.com/liangqiyuan/LLMAP",
        "commit": FROZEN_COMMIT,
        "raw_url": RAW_URL,
        "sha256": sha256,
        "size_bytes": len(content),
        "record_count": count,
    }
    CHECKSUM_FILE.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"[✓] Downloaded {count} records ({size_kb:.1f} KB) to {DEST_FILE.relative_to(ROOT_DIR.parent)}")
    print(f"[✓] SHA256: {sha256}")
    print(f"[✓] Metadata saved to {CHECKSUM_FILE.relative_to(ROOT_DIR.parent)}")


if __name__ == "__main__":
    main()
