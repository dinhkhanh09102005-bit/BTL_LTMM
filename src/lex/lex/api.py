"""Giao diện cấp cao: LEX, encrypt, decrypt."""
from __future__ import annotations

from typing import Union

from .iv_setup import compute_s0, make_key_context
from .keystream import KeystreamBuffer
from .validation import validate_data, validate_iv, validate_key

ByteData = Union[bytes, bytearray, memoryview]


class LEX:
    """Phiên mã dòng LEX-128 giữ trạng thái nội bộ liên tục.

    Một cặp (key, iv) chỉ được dùng cho MỘT thông điệp. LEX không có MAC.
    """

    def __init__(self, key: ByteData, iv: ByteData) -> None:
        key_ctx = make_key_context(validate_key(key))
        self._buffer = KeystreamBuffer(key_ctx, compute_s0(key_ctx, validate_iv(iv)))

    def keystream(self, n_bytes: int) -> bytes:
        """Sinh đúng n_bytes byte keystream kế tiếp."""
        return self._buffer.read(n_bytes)

    def process(self, data: ByteData) -> bytes:
        """XOR data với keystream (mã hóa và giải mã là cùng một phép)."""
        raw = validate_data(data)
        ks = self._buffer.read(len(raw))
        return bytes(a ^ b for a, b in zip(raw, ks))


def encrypt(key: ByteData, iv: ByteData, plaintext: ByteData) -> bytes:
    """Mã hóa cả thông điệp bằng một phiên LEX mới."""
    return LEX(key, iv).process(plaintext)


def decrypt(key: ByteData, iv: ByteData, ciphertext: ByteData) -> bytes:
    """Giải mã cả thông điệp bằng một phiên LEX mới."""
    return LEX(key, iv).process(ciphertext)
