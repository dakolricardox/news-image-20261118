#!/usr/bin/env python3
"""Front page: the world's news of Wednesday 18 November 2026, one picture.

The image is rendered at build time (host toolchain, PIL) into entry.png,
which ships next to this file. The sandbox provides no image library, so the
runtime job is deterministic: validate the bundled 1024x1024 PNG and copy it
to the output directory. Every story on the page is sourced and dated; the
content is fixed data, so repeated runs produce byte-identical output.
"""
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
os.makedirs(out, exist_ok=True)
DST = os.path.join(out, "entry.png")

with open(SRC, "rb") as f:
    data = f.read()

# Sanity: valid PNG, 1024x1024 as required.
assert data[:8] == b"\x89PNG\r\n\x1a\n", "entry.png is not a PNG"
w = int.from_bytes(data[16:20], "big")
h = int.from_bytes(data[20:24], "big")
assert (w, h) == (1024, 1024), f"unexpected image size {w}x{h}"

with open(DST, "wb") as f:
    f.write(data)

print(f"entry.png -> {DST} ({len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()[:16]})")
