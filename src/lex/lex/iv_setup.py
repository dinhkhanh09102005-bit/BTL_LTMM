"""Pha khởi tạo: S0 = AES-128_K(IV'), trong đó IV' là IV đảo thứ tự byte trong từng nhóm 4 byte.

Mã C tham chiếu nạp IV theo little-endian từng từ 32 bit còn bảng AES đọc big-endian, nên
khối đưa vào AES là iv[3],iv[2],iv[1],iv[0], iv[7],... (conventions.md T7). Pha này không trích rò rỉ.
"""
from __future__ import annotations

from ..aes.key_schedule import expand_key
from ..aes.standard_aes import encrypt_block
from .context import KeyContext

State = bytearray


def swap32_words(block: bytes) -> bytes:
    """Đảo thứ tự byte trong từng nhóm 4 byte của khối 16 byte."""
    if len(block) != 16:
        raise ValueError(f"khối phải đúng 16 byte, nhận {len(block)}")
    return b"".join(bytes(block[i:i + 4])[::-1] for i in range(0, 16, 4))


def make_key_context(key: bytes) -> KeyContext:
    """Mở rộng khóa thành ngữ cảnh khóa."""
    return KeyContext(round_keys=expand_key(bytes(key)))


def compute_s0(key_ctx: KeyContext, iv: bytes) -> State:
    """Tính trạng thái ban đầu S0 (16 byte, dạng byte chuẩn của AES)."""
    return bytearray(encrypt_block(key_ctx.round_keys, swap32_words(bytes(iv))))
