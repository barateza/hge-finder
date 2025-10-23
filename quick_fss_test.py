#!/usr/bin/env python3
"""Quick test to see if FSSSIgnalDiscovered messages are coming through."""

import json
import zmq
import zlib
import time

socket = zmq.Context().socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, b"")
socket.setsockopt(zmq.RCVTIMEO, 5000)
socket.connect("tcp://eddn.eddn.edcd.io:9500")

print("Listening for 30 seconds...")
start = time.time()
count = 0
fss_count = 0

while time.time() - start < 30:
    try:
        msg = socket.recv_multipart()
        count += 1
        data = json.loads(zlib.decompress(msg[0]).decode('utf-8'))
        schema = data.get("$schemaRef", "")
        
        if "fsssignaldiscovered" in schema.lower():
            fss_count += 1
            signals = data.get("message", {}).get("signals", [])
            uss_count = sum(1 for s in signals if s.get("USSType"))
            print(f"FSSSig #{fss_count}: {len(signals)} signals ({uss_count} USS)")
            for sig in signals:
                if sig.get("USSType"):
                    print(f"  - USS: {sig.get('USSType')}")
    except zmq.error.Again:
        continue
    except Exception as e:
        print(f"Error: {e}")

print(f"\nProcessed {count} messages, {fss_count} were FSSSignalDiscovered")
socket.close()
