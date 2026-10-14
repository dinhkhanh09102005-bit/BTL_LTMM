"""Loader for tests/vectors/estream_lex_kat.json and reference_trace.json."""
import json
from pathlib import Path

VECTORS = Path(__file__).resolve().parents[1] / "vectors"

def load_kat() -> list[dict]:
    return json.loads((VECTORS / "estream_lex_kat.json").read_text())["vectors"]

def load_trace() -> dict:
    return json.loads((VECTORS / "reference_trace.json").read_text())

def xor_digest(stream: bytes) -> bytes:
    d = bytearray(64)
    for i in range(0, len(stream), 64):
        for j, b in enumerate(stream[i:i + 64]):
            d[j] ^= b
    return bytes(d)

def check_kat_vector(v: dict, keystream_fn) -> list[str]:
    """keystream_fn(key: bytes, iv: bytes, n: int) -> bytes. Returns a list of mismatch descriptions (empty = pass)."""
    key, iv = bytes.fromhex(v["key"]), bytes.fromhex(v["iv"])
    stream = keystream_fn(key, iv, v["stream_length"])
    errs = []
    for s in v["segments"]:
        if stream[s["start"]:s["end"] + 1] != bytes.fromhex(s["hex"]):
            errs.append(f"segment {s['start']}..{s['end']}")
    if xor_digest(stream) != bytes.fromhex(v["xor_digest"]):
        errs.append("xor-digest")
    return errs
