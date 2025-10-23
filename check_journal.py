#!/usr/bin/env python3
"""Check latest journal entries for HGE signals."""

import json
from pathlib import Path
from datetime import datetime, timedelta

# Get journal path
journal_path = Path(r"C:\Users\sique\Saved Games\Frontier Developments\Elite Dangerous")

if not journal_path.exists():
    print(f"Journal path not found: {journal_path}")
    exit(1)

# Find latest journal file
journal_files = sorted(journal_path.glob("Journal.*.log"), reverse=True)
if not journal_files:
    print("No journal files found")
    exit(1)

latest_journal = journal_files[0]
print(f"Checking latest journal: {latest_journal.name}\n")

# Read last 100 lines
lines = latest_journal.read_text(encoding='utf-8').splitlines()
recent_lines = lines[-100:] if len(lines) > 100 else lines

print("=== Recent Journal Entries ===\n")

for line in recent_lines:
    try:
        entry = json.loads(line)
        timestamp = entry.get('timestamp', 'N/A')
        event = entry.get('Event', 'N/A')
        system = entry.get('StarSystem', 'N/A')
        
        # Look for relevant events
        if event in ['Location', 'FSDJump', 'FSS', 'Scan']:
            print(f"{timestamp} - {event:20} - {system}")
        
        # Look for any mention of "High" or "emission" or "USS"
        full_line = line.lower()
        if any(x in full_line for x in ['high', 'emission', 'uss', 'signal']):
            print(f"  >> {line[:100]}")
            
    except json.JSONDecodeError:
        continue

print("\n=== Looking for HGE-related events ===\n")
for line in recent_lines:
    try:
        entry = json.loads(line)
        full_line = json.dumps(entry).lower()
        
        if 'high grade emission' in full_line or ('high' in full_line and 'grade' in full_line and 'emission' in full_line):
            print(f"FOUND HGE: {json.dumps(entry, indent=2)}")
            
    except json.JSONDecodeError:
        continue
