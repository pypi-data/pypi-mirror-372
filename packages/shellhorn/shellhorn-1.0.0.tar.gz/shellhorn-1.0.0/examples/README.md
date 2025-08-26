# Shellhorn Examples

Simple test scripts for trying out shellhorn functionality.

## Files

**`example.py`** - Quick 3-second test script
- Takes optional exit code argument: `python3 example.py 1` (fails with code 1)
- Good for testing success/failure notifications

**`example_long.py`** - 30-second script with interrupt handling
- Handles Ctrl+C gracefully 
- Good for testing interrupt notifications and orphan detection

## Usage

```bash
# Test basic success notification
shellhorn python3 examples/example.py

# Test failure notification  
shellhorn python3 examples/example.py 1

# Test interrupt handling (press Ctrl+C)
shellhorn python3 examples/example_long.py
```