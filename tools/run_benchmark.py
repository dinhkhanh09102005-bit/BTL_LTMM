"""Đo tốc độ sinh keystream (MB/s) của bản cài đặt Python thuần.  python tools/run_benchmark.py [MiB]"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lex import LEX  # noqa: E402


def main() -> None:
    mib = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    n = int(mib * 1024 * 1024)
    t = time.perf_counter()
    LEX(bytes(16), bytes(16)).keystream(n)
    dt = time.perf_counter() - t
    print(f"{n} byte trong {dt:.2f} s = {n / dt / 1e6:.3f} MB/s ({n / dt * 8 / 1e6:.2f} Mbit/s)")


if __name__ == "__main__":
    main()
