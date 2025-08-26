#!/usr/bin/env python3
"""
Simple example script for testing shellhorn.
"""

import time
import sys

print("Starting example script...")
print("This will take 3 seconds...")

for i in range(3):
    print(f"Step {i+1}/3")
    time.sleep(1)

print("Done!")

# Exit with code passed as argument (default 0)
exit_code = int(sys.argv[1]) if len(sys.argv) > 1 else 0
sys.exit(exit_code)