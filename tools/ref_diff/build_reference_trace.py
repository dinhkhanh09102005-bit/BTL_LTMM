#!/usr/bin/env python3
"""Build tests/vectors/reference_trace.json from the official LEX-v2 C reference.

Usage:
  python tools/ref_diff/build_reference_trace.py --src <dir with lex.c + ecrypt-sync.h> \
      [--out tests/vectors/reference_trace.json] [--cc gcc]

The C code is compiled at -O0 (the reference indexes ks[] past its declared bound
for Nr > 10 code paths that are not executed for LEX-128, but -O0 avoids any UB surprises).
Every trace is asserted byte-for-byte against ECRYPT_keystream_bytes() of the official code.
"""
import argparse, json, os, subprocess, sys, tempfile, hashlib

CASES = [
    ("key0_iv0", "00" * 16, "00" * 16),
    ("official_set1_v0", "80" + "00" * 15, "00" * 16),
    ("iv_byte_order_probe", "00" * 16, "00112233445566778899AABBCCDDEEFF"),
    ("mixed", "0123456789ABCDEFFEDCBA9876543210", "000102030405060708090A0B0C0D0E0F"),
]
CYCLES = 3

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", default="tests/vectors/reference_trace.json")
    ap.add_argument("--cc", default="gcc")
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    lex_c = os.path.join(a.src, "lex.c")
    if not os.path.exists(lex_c):
        sys.exit(f"lex.c not found in {a.src}")
    sha = hashlib.sha256(open(lex_c, "rb").read()).hexdigest()
    exe = os.path.join(tempfile.mkdtemp(), "trace")
    r = run([a.cc, "-O0", "-w", "-I", a.src, "-I", here, "-o", exe, os.path.join(here, "trace.c")])
    if r.returncode: sys.exit(r.stderr)
    out = {"source": {"file": "lex.c (LEX-v2, eSTREAM Phase 3 API-compliant code)", "sha256": sha,
                      "compiler": a.cc, "flags": "-O0"},
           "conventions": {"round_numbering": "1..10, K_r = round_keys[r]", "state_byte_index": "4*c + r (column-major)",
                           "cycles_per_case": CYCLES}, "cases": []}
    for name, key, iv in CASES:
        p = run([exe, key, iv, str(CYCLES)])
        lines = dict(l.split("=", 1) for l in p.stdout.split() if "=" in l and not l.startswith("LEAK"))
        raw = p.stdout.strip().splitlines()
        if p.returncode or "MATCH_OFFICIAL=1" not in raw:
            sys.exit(f"case {name}: C trace does not match official keystream\n{p.stdout}")
        case = {"name": name, "key": key, "iv": iv, "aes_input_block": raw[0].split("=")[1], "s0": raw[1].split("=")[1], "cycles": []}
        cyc = {}
        for l in raw[2:]:
            if l.startswith("MATCH"): continue
            head, rest = l.split("=", 1)
            c = int(head[1]); 
            if head.endswith("KS"): cyc[c]["keystream40"] = rest; continue
            rn = int(head.split("R")[1]); st, lk = rest.split(" LEAK=")
            cyc.setdefault(c, {"rounds": []})["rounds"].append({"round": rn, "state_after_ark": st, "leak": lk})
        case["cycles"] = [cyc[k] for k in sorted(cyc)]
        out["cases"].append(case)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)
    print("wrote", a.out, "with", len(out["cases"]), "cases; all verified against official ECRYPT_keystream_bytes")

if __name__ == "__main__":
    main()
