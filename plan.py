#!/usr/bin/env python3
import os
import json
import hashlib
from pathlib import Path

# Configuration
LAPTOP_DIR = Path("/Users/chris/Music/Music/Media.localized/Music")
NAS_DIR = Path("/Users/chris/share/Music")
PLAN_OUTPUT = Path("change_plan.json")

def hash_file(file_path):
    """Compute SHA256 hash of a given file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def build_file_index(base_dir):
    """Build a dictionary of relative_path -> hash for all files under base_dir."""
    index = {}
    for root, dirs, files in os.walk(base_dir):
        for fname in files:
            rel_path = Path(root).relative_to(base_dir) / fname
            full_path = Path(root) / fname
            # Compute hash to compare content
            index[str(rel_path)] = {
                "hash": hash_file(full_path),
                "size": full_path.stat().st_size
            }
    return index

def main():
    print("Building file indexes, this may take a while...")
    laptop_index = build_file_index(LAPTOP_DIR)
    nas_index = build_file_index(NAS_DIR)

    to_add = []    # Files present on laptop but not on NAS
    to_update = [] # Files present on both but with different hashes

    # Check for additions and updates
    for rel_path, laptop_info in laptop_index.items():
        if rel_path not in nas_index:
            # File on laptop not on NAS, we should add it to NAS
            to_add.append(rel_path)
        else:
            # File present on both, check hash
            nas_info = nas_index[rel_path]
            if laptop_info["hash"] != nas_info["hash"]:
                # File differs, update NAS with laptop file
                to_update.append(rel_path)

    # At this point, we only add or update NAS. We do not delete anything from the NAS.
    # Files that exist on NAS but not on laptop are not modified.

    change_plan = {
        "laptop_dir": str(LAPTOP_DIR),
        "nas_dir": str(NAS_DIR),
        "add": to_add,
        "update": to_update
    }

    # Write plan to JSON
    with open(PLAN_OUTPUT, "w") as f:
        json.dump(change_plan, f, indent=4)

    # Print human-readable summary
    print("Change Plan Summary:")
    if not to_add and not to_update:
        print("No changes are required. The NAS is already in sync with this laptop.")
    else:
        if to_add:
            print("Files to be added to NAS:")
            for item in to_add:
                print(f"  ADD: {item}")

        if to_update:
            print("Files to be updated on NAS:")
            for item in to_update:
                print(f"  UPDATE: {item}")

    print(f"\nA detailed plan has been written to {PLAN_OUTPUT}.")
    print("Review this plan. If approved, run `execute_plan.py` to apply changes.")


if __name__ == "__main__":
    main()
