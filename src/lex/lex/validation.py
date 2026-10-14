"""Kiểm tra kiểu và độ dài khóa/IV ở biên API; chuẩn hóa về bytes (bản sao độc lập)."""
from __future__ import annotations

from typing import Union

ByteData = Union[bytes, bytearray, memoryview]

KEY_BYTES = 16
IV_BYTES = 16


def _to_bytes(value: object, name: str, length: int) -> bytes:
    if not isinstance(value, (bytes, bytearray, memoryview)):
        raise TypeError(f"{name} phải là bytes, bytearray hoặc memoryview, nhận {type(value).__name__}")
    data = bytes(value)
    if len(data) != length:
        raise ValueError(f"{name} phải đúng {length} byte, nhận {len(data)}")
    return data


def validate_key(key: ByteData) -> bytes:
    """Khóa: đúng 16 byte."""
    return _to_bytes(key, "key", KEY_BYTES)


def validate_iv(iv: ByteData) -> bytes:
    """IV: đúng 16 byte."""
    return _to_bytes(iv, "iv", IV_BYTES)


def validate_data(data: ByteData) -> bytes:
    """Dữ liệu cần mã hóa/giải mã: bytes-like, độ dài tùy ý."""
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError(f"data phải là bytes, bytearray hoặc memoryview, nhận {type(data).__name__}")
    return bytes(data)
