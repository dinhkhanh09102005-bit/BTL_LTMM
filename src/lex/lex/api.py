"""Public streaming and one-shot API for the LEX educational implementation."""

from __future__ import annotations

from typing import TypeAlias

from .iv_setup import compute_s0, make_key_context
from .keystream import KeystreamBuffer
from .validation import validate_data, validate_iv, validate_key

ByteData: TypeAlias = bytes | bytearray | memoryview


class LEX:
    """One stateful LEX stream.

    Calls to keystream() and process() consume the same stream position.
    """

    def __init__(self, key: ByteData, iv: ByteData) -> None:
        valid_key = validate_key(key)
        valid_iv = validate_iv(iv)

        key_ctx = make_key_context(valid_key)
        initial_state = compute_s0(key_ctx, valid_iv)
        self._buffer = KeystreamBuffer(key_ctx, initial_state)

    def keystream(self, n_bytes: int) -> bytes:
        """Return the next n_bytes keystream bytes."""
        return self._buffer.read(n_bytes)

    def process(self, data: ByteData) -> bytes:
        """XOR data with the next keystream bytes."""
        raw = validate_data(data)
        stream = self._buffer.read(len(raw))
        return bytes(
            data_byte ^ stream_byte
            for data_byte, stream_byte in zip(raw, stream)
        )


def encrypt(key: ByteData, iv: ByteData, plaintext: ByteData) -> bytes:
    """Encrypt one message using a fresh LEX stream."""
    return LEX(key, iv).process(plaintext)


def decrypt(key: ByteData, iv: ByteData, ciphertext: ByteData) -> bytes:
    """Decrypt one message using a fresh LEX stream."""
    return LEX(key, iv).process(ciphertext)
