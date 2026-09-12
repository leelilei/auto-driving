#!/usr/bin/env python3
"""
Prepare ChinaTravel dev dataset for baseline experiments.

This script loads all dev_split JSON files and creates a consolidated
dev dataset in the format expected by baseline experiments.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
CHINATRAVEL_DATA = PROJECT_ROOT / "external" / "ChinaTravel" / "chinatravel" / "data" / "dev_split"
OUTPUT_FILE = PROJECT_ROOT / "9-AutoDriving-core" / "data" / "chinatravel_dev_60.json"


def load_dev_split() -> Dict[str, Dict[str, Any]]:
    """Load all dev split files."""
    dev_data = {}

    if not CHINATRAVEL_DATA.exists():
        raise FileNotFoundError(f"Dev data directory not found: {CHINATRAVEL_DATA}")

    json_files = list(CHINATRAVEL_DATA.glob("*.json"))
    print(f"Found {len(json_files)} JSON files in {CHINATRAVEL_DATA}")

    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        uid = data.get('uid')
        if not uid:
            print(f"Warning: No uid in {json_file}, skipping")
            continue

        # Transform to format expected by baselines
        query = {
            'uid': uid,
            'tag': data.get('tag', ''),
            'org': data.get('start_city', ''),  # org = start_city
            'dest': data.get('target_city', ''),  # dest = target_city
            'target_city': data.get('target_city', ''),  # Keep target_city for evaluator
            'days': data.get('days', 1),
            'people_number': data.get('people_number', 1),
            'limit_rooms': data.get('limit_rooms', False),
            'limits_room_type': data.get('limits_room_type', False),
            'hard_logic_py': data.get('hard_logic_py', []),
            'nature_language': data.get('nature_language', ''),
            'nature_language_en': data.get('nature_language_en', ''),
            'query': data.get('query', data.get('nature_language', ''))
        }

        dev_data[uid] = query

    print(f"Loaded {len(dev_data)} dev examples")

    # Count by tag
    tag_counts = {}
    for query in dev_data.values():
        tag = query['tag']
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    print("\nBreakdown by tag:")
    for tag, count in sorted(tag_counts.items()):
        print(f"  {tag}: {count}")

    return dev_data


def main():
    print("Preparing ChinaTravel dev dataset...")
    print(f"Source: {CHINATRAVEL_DATA}")
    print(f"Output: {OUTPUT_FILE}")
    print()

    # Load dev data
    dev_data = load_dev_split()

    # Create output directory
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Save consolidated file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dev_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved {len(dev_data)} examples to {OUTPUT_FILE}")
    print(f"   File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")


if __name__ == '__main__':
    main()
