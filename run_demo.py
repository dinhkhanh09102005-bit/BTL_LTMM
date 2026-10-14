"""Demo LEX-128: đối chiếu vector chuẩn, xem rò rỉ từng vòng, mã hóa/giải mã một thông điệp.

Chạy:  python run_demo.py                      (dùng thông điệp mặc định)
       python run_demo.py --message "xin chao"
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from lex import LEX, decrypt, encrypt                      # noqa: E402
from lex.lex.extractor import extract_leak                 # noqa: E402
from lex.lex.iv_setup import compute_s0, make_key_context  # noqa: E402
from lex.lex.round_engine import lex_round                 # noqa: E402

EXPECTED_S0 = "66E94BD4EF8A2C3B884CFA59CA342B2E"
EXPECTED_KS40 = ("FF27889A64BBC76D9D9548F2E50FCB4F5BC4F94DEDC76FC23347ED94AB279CE4"
                 "F5F608648D8B5EE8")


def hx(b: bytes) -> str:
    return bytes(b).hex().upper()


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--message", default="LEX stream cipher - bai tap nhom 6 thanh vien")
    args = ap.parse_args()

    section("1. Vector chuẩn: Key = 0, IV = 0")
    key = iv = bytes(16)
    ctx = make_key_context(key)
    s0 = compute_s0(ctx, iv)
    print(f"S0           = {hx(s0)}")
    print(f"S0 mong đợi  = {EXPECTED_S0}   -> {'ĐẠT' if hx(s0) == EXPECTED_S0 else 'SAI'}")

    section("2. Rò rỉ từng vòng của chu kỳ đầu (4 byte/vòng, lấy sau AddRoundKey)")
    state = bytearray(s0)
    parts = []
    for r in range(1, 11):
        state = lex_round(state, ctx.round_keys[r], mix_columns=True)
        leak = extract_leak(state, r)
        parts.append(leak)
        print(f"vòng {r:2d}: trạng thái {hx(state)}  rò rỉ {hx(leak)}")
    ks = b"".join(parts)
    print(f"40 byte keystream = {hx(ks)}")
    print(f"mong đợi          = {EXPECTED_KS40}   -> {'ĐẠT' if hx(ks) == EXPECTED_KS40 else 'SAI'}")
    print(f"LEX.keystream(40) khớp: {LEX(key, iv).keystream(40) == ks}")

    section("3. Mã hóa / giải mã (khóa và IV ngẫu nhiên)")
    k, v = os.urandom(16), os.urandom(16)
    plain = args.message.encode("utf-8")
    cipher = encrypt(k, v, plain)
    print(f"key        = {hx(k)}\niv         = {hx(v)}")
    print(f"bản rõ     = {hx(plain)}")
    print(f"bản mã     = {hx(cipher)}")
    ok = decrypt(k, v, cipher) == plain
    print(f"giải mã khớp bản rõ: {ok}")

    section("4. Streaming: đọc theo từng đoạn cho cùng kết quả")
    a = LEX(k, v)
    chunks = b"".join(a.keystream(n) for n in (1, 7, 100, 3))
    print(f"keystream(1)+(7)+(100)+(3) == keystream(111): {chunks == LEX(k, v).keystream(111)}")

    print("\nLưu ý: LEX không có MAC và đã bị loại khỏi danh mục cuối eSTREAM; chỉ dùng học tập.")
    return 0 if (hx(s0) == EXPECTED_S0 and hx(ks) == EXPECTED_KS40 and ok) else 1


if __name__ == "__main__":
    sys.exit(main())
