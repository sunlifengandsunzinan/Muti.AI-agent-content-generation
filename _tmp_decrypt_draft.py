#!/usr/bin/env python3
import base64
import struct
import json

with open(r'C:\Users\Administrator\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\6月9日\draft_content.json', 'rb') as f:
    raw = f.read()

decoded = base64.b64decode(raw)
print(f"Base64-decoded length: {len(decoded)}")

print(f"First 16 bytes hex: {decoded[:16].hex()}")

# RC4 with empty key
from Crypto.Cipher import ARC4, AES
cipher = ARC4.new(b'0')
result = cipher.decrypt(decoded[:200])
print(f"RC4 empty key: {result[:50]}")

# zlib/gzip
import zlib
try:
    decompressed = zlib.decompress(decoded)
    print(f"zlib decompressed: {decompressed[:200]}")
except Exception as e:
    print(f"zlib failed: {e}")

try:
    import gzip
    decompressed = gzip.decompress(decoded)
    print(f"gzip decompressed: {decompressed[:200]}")
except Exception as e:
    print(f"gzip failed: {e}")

# Meta file
with open(r'C:\Users\Administrator\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\6月9日\draft_meta_info.json', 'rb') as f:
    meta_raw = f.read()

meta_decoded = base64.b64decode(meta_raw)
print(f"\nMeta decoded length: {len(meta_decoded)}")
print(f"Meta first 16 hex: {meta_decoded[:16].hex()}")

# Try XOR 0xFF
xored = bytes([b ^ 0xFF for b in decoded[:100]])
print(f"XOR 0xFF: {xored[:50]}")

# Check first 4 bytes as length
if len(decoded) >= 4:
    header_len = struct.unpack('<I', decoded[:4])[0]
    print(f"\nFirst 4 bytes as LE uint32: {header_len}")

# Try lzma/bz2
if len(decoded) > 4:
    rest = decoded[4:]
    try:
        import lzma
        decomp = lzma.decompress(rest)
        print(f"lzma compressed! Decoded: {decomp[:100]}")
    except Exception as e:
        print(f"lzma failed: {e}")
    try:
        import bz2
        decomp = bz2.decompress(rest)
        print(f"bzip2 compressed! Decoded: {decomp[:100]}")
    except Exception as e:
        print(f"bzip2 failed: {e}")

# Try: maybe it's XOR with mask based on position
# Try to find repeating pattern by analyzing frequency
from collections import Counter
if len(decoded) > 100:
    # Check byte distribution
    freq = Counter(decoded[:1000])
    print(f"\nByte frequency in first 1000 bytes (top 10): {freq.most_common(10)}")
    
    # If encrypted, bytes should be ~uniformly distributed
    # Check: looking for repeating key pattern
    for key_len in range(1, 33):
        score = 0
        for i in range(min(16, len(decoded) - key_len * 4)):
            if decoded[i] == decoded[i + key_len]:
                score += 1
        if score > 10:
            print(f"Key length {key_len}: {score} repeats found")
