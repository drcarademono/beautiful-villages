#!/usr/bin/env python3
import os
import json

def main():
    combos = set()

    # Traverse current directory and subdirectories
    for root, _, files in os.walk('.'):
        for fn in files:
            if fn.lower().endswith('.json'):
                path = os.path.join(root, fn)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

                # Only process if the root is an object
                if not isinstance(data, dict):
                    continue

                # Navigate into RmbSubRecord → Interior → BlockFlatObjectRecords
                rmb_sub = data.get('RmbSubRecord')
                if not isinstance(rmb_sub, dict):
                    continue

                interior = rmb_sub.get('Interior', {})
                records = interior.get('BlockFlatObjectRecords', [])
                if not isinstance(records, list):
                    continue

                # Collect matching archive/record combos
                for entry in records:
                    ta = entry.get('TextureArchive')
                    tr = entry.get('TextureRecord')
                    if isinstance(ta, int) and isinstance(tr, int):
                        if (1200 <= ta <= 1400) or (10011 <= ta <= 10020):
                            combos.add((ta, tr))

    # Report results
    for ta, tr in sorted(combos):
        print(f"{ta}/{tr}")
    print(f"Total unique combinations: {len(combos)}")

if __name__ == '__main__':
    main()

