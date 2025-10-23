#!/usr/bin/env python3
"""Test to find HGE signals in EDDN stream."""

import json
import zmq
import time
import zlib

EDDN_ENDPOINT = "tcp://eddn.edcd.io:9500"

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, b"")
socket.setsockopt(zmq.RCVTIMEO, 5000)
socket.connect(EDDN_ENDPOINT)

print("Connected to EDDN. Listening for messages...")
start = time.time()
msg_count = 0
hge_count = 0
schemas = {}

while time.time() - start < 120:  # Run for 2 minutes
    try:
        message = socket.recv_multipart()
        msg_count += 1
        
        decompressed = zlib.decompress(message[0])
        data = json.loads(decompressed.decode('utf-8'))
        schema = data.get("$schemaRef", "unknown")
        msg = data.get("message", {})
        
        # Track schemas
        if schema not in schemas:
            schemas[schema] = 0
            print(f"New schema: {schema}")
        schemas[schema] += 1
        
        # Check for signals (HGE detection data)
        if "Signals" in msg:
            signals = msg.get("Signals", [])
            print(f"\n[SIGNALS] System: {msg.get('StarSystem')}, Count: {len(signals)}")
            for sig in signals:
                print(f"  - Type: {sig.get('Type')}")
                sig_type = sig.get("Type", "").lower()
                if "high" in sig_type and "grade" in sig_type:
                    print(f"[HGE FOUND] System: {msg.get('StarSystem')}, Type: {sig.get('Type')}")
                    hge_count += 1
        
        # Log message schemas periodically
        if msg_count % 500 == 0:
            print(f"\n[LOG] Processed {msg_count} messages")
            print(f"[LOG] Found {hge_count} HGE signals")
            print(f"[LOG] Schemas: {schemas}")
            
    except zmq.error.Again:
        continue
    except Exception as e:
        print(f"Error: {e}")
        continue

print(f"\n\nDone. Processed {msg_count} messages")
print(f"Found {hge_count} HGE signals")
print(f"\nSchema distribution:")
for schema, count in sorted(schemas.items(), key=lambda x: x[1], reverse=True)[:10]:
    pct = (count / msg_count * 100)
    print(f"  {pct:5.1f}% {schema}")

socket.close()
context.term()

