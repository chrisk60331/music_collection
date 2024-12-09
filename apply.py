#!/usr/bin/env python3
import os
import json
import shutil
from pathlib import Path

PLAN_INPUT = Path("change_plan.json")


def main():
    if not PLAN_INPUT.exists():
        print(f"Error: {PLAN_INPUT} does not exist. Generate a plan first.")
        return

    with open(PLAN_INPUT, "r") as f:
        plan = json.load(f)

    laptop_dir = Path(plan["laptop_dir"])
    nas_dir = Path(plan["nas_dir"])
    to_add = plan["add"]
    to_update = plan["update"]

    # Execute changes
    for item in to_add:
        src = laptop_dir / item
        dst = nas_dir / item
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"Added: {item}")

    for item in to_update:
        src = laptop_dir / item
        dst = nas_dir / item
        # Update file on NAS
        shutil.copy2(src, dst)
        print(f"Updated: {item}")

    print("All changes have been applied to the NAS.")

    # Optionally, you may want to sync the laptop now from the updated NAS.
    # That step is not explicitly requested in the original prompt,
    # but could be done here if desired.
    # For instance, you could run a separate script or code to pull changes
    # from NAS to laptop. For now, we leave that as a separate manual step.


if __name__ == "__main__":
    main()
