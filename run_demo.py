"""TV5 demo: --mock for isolated learning, default for real LEX integration."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="LEX TV5 demo")
    parser.add_argument(
        "--mock", action="store_true",
        help="Use fake TV3/TV4 modules (NOT cryptographic LEX)"
    )
    args = parser.parse_args()

    # Cho phep chay tu goc repository ma khong can pip install.
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root / "src"))

    if args.mock:
        from tests.support.mock_lex_dependencies import install_mock_dependencies
        install_mock_dependencies()  # Phai chay truoc import API

    try:
        from lex.lex.api import LEX, encrypt, decrypt
    except ImportError as exc:
        print("TV1-TV4 have not been integrated yet.")
        print("To try the isolated demo: py -3 run_demo.py --mock")
        print("Import error:", exc)
        return 2

    # CHI dung 16 byte zero trong vi du giao duc / kiem thu.
    key = bytes(16)
    iv = bytes(16)
    plaintext = b"HELLO"

    # Moi lenh encrypt/decrypt khoi tao phien LEX rieng.
    ciphertext = encrypt(key, iv, plaintext)
    recovered = decrypt(key, iv, ciphertext)
    if recovered != plaintext:
        raise AssertionError("Decryption did not recover the input")

    # Hai lan read trong mot doi tuong phai bang mot lan read lien tuc.
    stream = LEX(key, iv)
    first = stream.keystream(3)
    second = stream.keystream(37)
    combined = LEX(key, iv).keystream(40)
    if first + second != combined:
        raise AssertionError("Split keystream mismatch")

    # Thu viec doc qua ranh gioi block 40 byte.
    stream2 = LEX(key, iv)
    cross_boundary = stream2.keystream(45)
    if len(cross_boundary) != 45:
        raise AssertionError("Incorrect keystream length")

    print("MODE:", "MOCK (NOT REAL LEX)" if args.mock else "REAL LEX")
    print("KEY SIZE:", len(key), "bytes; IV SIZE:", len(iv), "bytes")
    print("Plaintext:", plaintext)
    print("Ciphertext (hex):", ciphertext.hex())
    print("Recovered:", recovered)
    print("Stream 3 + 37 == 40:", first + second == combined)
    print("Read 45 bytes across 40-byte boundary:", len(cross_boundary))
    print("DEMO PASS:", "isolated simulation only" if args.mock else "round-trip and chunking")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
