#!/usr/bin/env python3
"""Analyze what USS types are coming through EDDN."""

import json
import zmq
import time
import zlib
from collections import defaultdict

EDDN_ENDPOINT = "tcp://eddn.edcd.io:9500"

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, b"")
socket.setsockopt(zmq.RCVTIMEO, 5000)
socket.connect(EDDN_ENDPOINT)

print("Connected to EDDN. Analyzing USS types...")
start = time.time()
msg_count = 0
uss_types = defaultdict(int)
systems_with_uss = set()

while time.time() - start < 300:  # Run for 5 minutes
    try:
        message = socket.recv_multipart()
        msg_count += 1
        
        decompressed = zlib.decompress(message[0])
        data = json.loads(decompressed.decode('utf-8'))
        schema = data.get("$schemaRef", "")
        msg = data.get("message", {})
        
        # Look for FSSSignalDiscovered with USS signals
        if "fsssignaldiscovered" in schema.lower():
            signals = msg.get("signals", [])
            for sig in signals:
                uss_type = sig.get("USSType")
                if uss_type:
                    uss_types[uss_type] += 1
                    system = msg.get("StarSystem", "Unknown")
                    systems_with_uss.add(f"{system}: {uss_type}")
        
        if msg_count % 1000 == 0:
            print(f"[{msg_count}] Processed {msg_count} messages")
            
    except zmq.error.Again:
        continue
    except Exception as e:
        print(f"Error: {e}")
        continue

print(f"\n\nAnalysis complete. Processed {msg_count} messages in 5 minutes")
print(f"\nUSS Types found:")
for uss_type, count in sorted(uss_types.items(), key=lambda x: x[1], reverse=True):
    print(f"  [{count:4d}] {uss_type}")

print(f"\nTotal unique systems with USS: {len(systems_with_uss)}")
if len(systems_with_uss) <= 20:
    for sys in sorted(systems_with_uss)[:20]:
        print(f"  - {sys}")

# Check for HGE specifically
hge_count = 0
for uss_type in uss_types:
    if "valuable" in uss_type.lower() or "high" in uss_type.lower() or "grade" in uss_type.lower():
        print(f"\n*** POSSIBLE HGE: {uss_type} ({uss_types[uss_type]} occurrences)")
        hge_count += uss_types[uss_type]

if hge_count > 0:
    print(f"\nTotal HGE-like signals: {hge_count}")
else:
    print(f"\nNO HGE-like signals found in EDDN stream")

socket.close()
context.term()
