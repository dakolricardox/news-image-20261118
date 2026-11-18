#!/usr/bin/env python3
"""Copy the bundled front page for 18 November 2026 to the output directory.

make.fun news-image-20261118: the entry image ships in the repository and this
program writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default ./out). Deterministic
by construction: the same bytes are copied on every run.
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
EXPECTED_SHA256 = "86ade12b3d65f5513d953094eb1eae8a9fd1f3d235d000141cd34684ed451747"


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    with open(dst, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit("entry.png corrupted: sha256 mismatch")
    print("wrote", dst, os.path.getsize(dst), "bytes sha256", digest[:12])


if __name__ == "__main__":
    main()
