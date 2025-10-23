#!/usr/bin/env python3
"""Quick test to verify EDDN connectivity."""

import json
import zmq
import time
import zlib
import sys

# Set encoding to UTF-8 for output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

EDDN_ENDPOINT = "tcp://eddn.edcd.io:9500"
TIMEOUT_MS = 5000

def test_eddn():
    """Test EDDN connection and receive first message."""
    print("CONN: Testing EDDN connection to tcp://eddn.edcd.io:9500")
    print("INFO: Timeout set to 5000ms\n")
    
    context = None
    socket = None
    
    try:
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBE, b"")
        socket.setsockopt(zmq.RCVTIMEO, TIMEOUT_MS)
        socket.connect(EDDN_ENDPOINT)
        
        print("✅ Connected! Waiting for first message...")
        start_time = time.time()
        
        while True:
            try:
                message = socket.recv_multipart()
                elapsed = time.time() - start_time
                print(f"\n📨 Received first message after {elapsed:.1f}s")
                print(f"   Message has {len(message)} parts")
                
                # Try to parse whichever part is available
                for i, part in enumerate(message):
                    print(f"\n   --- Part {i} (size: {len(part)} bytes) ---")
                    try:
                        # Try to decompress first
                        decompressed = zlib.decompress(part)
                        text = decompressed.decode('utf-8')
                        data = json.loads(text)
                        print(f"   [Decompressed] JSON keys: {list(data.keys())}")
                        schema_ref = data.get("$schemaRef", "unknown")
                        system_name = data.get("StarSystem", "unknown")
                        event_type = data.get("Event", "unknown")
                        uss_type = data.get("USSType", "unknown")
                        print(f"   Schema: {schema_ref}")
                        print(f"   System: {system_name}")
                        print(f"   Event: {event_type}")
                        print(f"   USSType: {uss_type}")
                        
                        # Check for nested message
                        if "message" in data:
                            msg = data["message"]
                            print(f"\n   Message keys: {list(msg.keys())}")
                            print(f"   Message StarSystem: {msg.get('StarSystem', 'N/A')}")
                            print(f"   Message Event: {msg.get('Event', 'N/A')}")
                            print(f"   Message USSType: {msg.get('USSType', 'N/A')}")
                    except zlib.error:
                        # Not compressed, try direct parsing
                        try:
                            text = part.decode('utf-8', errors='ignore')
                            if text.startswith('{'):
                                data = json.loads(text)
                                print(f"   [Raw] JSON keys: {list(data.keys())}")
                            else:
                                print(f"   Text (first 100 chars): {text[:100]}")
                        except Exception as e:
                            print(f"   Parse error: {e}")
                            print(f"   Raw bytes (first 50): {part[:50]}")
                
                print(f"\n✅ EDDN connection is working!")
                print(f"\n📊 Looking for HGE signals... continuing to receive messages for 60 seconds...")
                
                # Continue receiving to look for HGE
                start_time2 = time.time()
                hge_found = False
                while time.time() - start_time2 < 60:
                    try:
                        message = socket.recv_multipart()
                        decompressed = zlib.decompress(message[0])
                        text = decompressed.decode('utf-8')
                        data = json.loads(text)
                        schema = data.get("$schemaRef", "").lower()
                        
                        # Look for USS or Codex HGE signals
                        if "signals" in data.get("message", {}):
                            msg = data["message"]
                            signals = msg.get("Signals", [])
                            for sig in signals:
                                sig_type = sig.get("Type", "").lower()
                                if "high" in sig_type and "grade" in sig_type:
                                    print(f"\n🎯 FOUND HGE! In system: {msg.get('StarSystem')}")
                                    print(f"   Signal type: {sig_type}")
                                    print(f"   Signal: {sig}")
                                    hge_found = True
                                    break
                        
                        if hge_found:
                            break
                    except zmq.error.Again:
                        continue
                
                if not hge_found:
                    print(f"⚠️ No HGE signals found in 60 seconds of streaming")
                return True
                
            except zmq.error.Again:
                elapsed = time.time() - start_time
                if elapsed > 30:
                    print(f"\n❌ Timeout after {elapsed:.1f}s - no messages from EDDN")
                    print("   This could mean:")
                    print("   1. EDDN server is down")
                    print("   2. Firewall is blocking port 9500")
                    print("   3. Network connectivity issue")
                    return False
                print(f"   ⏱️  Still waiting... ({elapsed:.1f}s elapsed)")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    finally:
        if socket:
            socket.close()
        if context:
            context.term()

if __name__ == "__main__":
    success = test_eddn()
    exit(0 if success else 1)
