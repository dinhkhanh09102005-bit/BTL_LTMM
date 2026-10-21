"""TV5 - Giao dien ma hoa dong LEX (API)."""
from __future__ import annotations

from typing import Union

from .iv_setup import compute_s0, make_key_context
from .keystream import KeystreamBuffer
from .validation import validate_data, validate_iv, validate_key

ByteData = Union[bytes, bytearray, memoryview]


class LEX:
    """Mot phien LEX co trang thai keystream rieng."""

    def __init__(self, key: ByteData, iv: ByteData) -> None:
        valid_key = validate_key(key)
        valid_iv = validate_iv(iv)

        key_ctx = make_key_context(valid_key)
        initial_state = compute_s0(key_ctx, valid_iv)
        self._buffer = KeystreamBuffer(key_ctx, initial_state)

    def keystream(self, n_bytes: int) -> bytes:
        """Lay chinh xac n_bytes byte keystream tiep theo."""
        return self._buffer.read(n_bytes)

    def process(self, data: ByteData) -> bytes:
        """Ma hoa hoac giai ma voi keystream tai vi tri hien tai."""
        raw = validate_data(data)
        stream = self._buffer.read(len(raw))
        return bytes(a ^ b for a, b in zip(raw, stream))


def encrypt(key: ByteData, iv: ByteData, plaintext: ByteData) -> bytes:
    """Ma hoa mot thong diep voi mot phien LEX moi."""
    return LEX(key, iv).process(plaintext)


def decrypt(key: ByteData, iv: ByteData, ciphertext: ByteData) -> bytes:
    """Giai ma mot thong diep voi mot phien LEX moi."""
    return LEX(key, iv).process(ciphertext)
