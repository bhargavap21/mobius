#!/usr/bin/env python3
"""
Simple script to monitor backend logs for a specific session
Usage: python watch_logs.py <session_id_prefix>
Example: python watch_logs.py 4eb4163a
"""
import sys
import subprocess
import re

if len(sys.argv) < 2:
    print("Usage: python watch_logs.py <session_id_prefix>")
    sys.exit(1)

session_prefix = sys.argv[1]
print(f"Monitoring logs for session starting with: {session_prefix}")
print("=" * 80)

# Get the PID of the uvicorn process
try:
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True
    )

    for line in result.stdout.split('\n'):
        if 'uvicorn main:app' in line and 'grep' not in line:
            parts = line.split()
            pid = parts[1]
            print(f"Found uvicorn process: PID {pid}")
            print("Tailing stderr...")
            print("=" * 80)

            # Tail the process stderr
            # Note: This is a simplified approach - in production you'd use proper logging
            subprocess.run([
                "tail", "-f", f"/proc/{pid}/fd/2"
            ], check=False)
            break
    else:
        print("Could not find uvicorn process")
        print("Try running: python main.py or uvicorn main:app --reload")

except Exception as e:
    print(f"Error: {e}")
    print("\nNote: Process monitoring may not work on macOS.")
    print("Alternative: Check console output where you started uvicorn")
