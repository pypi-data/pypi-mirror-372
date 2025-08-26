#!/usr/bin/env python3
"""
Long-running example script for testing shellhorn interruption.
"""

import time

print("Starting long script...")
print("Press Ctrl+C to interrupt...")

try:
    for i in range(30):
        print(f"Step {i+1}/30")
        time.sleep(1)
    print("Completed all steps!")
except KeyboardInterrupt:
    print("Received interrupt, cleaning up...")
    time.sleep(0.5)
    print("Cleanup complete")
    exit(130)  # Standard exit code for SIGINT