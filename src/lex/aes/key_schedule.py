from typing import Union
from .sbox import SBOX

# Hang so vong cua AES-128
RCON = (
    0x00,
    0x01, 0x02, 0x04, 0x08, 0x10,
    0x20, 0x40, 0x80, 0x1B, 0x36,
)

ByteData = Union[bytes, bytearray, memoryview]

def _validate_input(
    data: ByteData,
    expected_len: int,
    name: str,
) -> bytes:
    """Kiem tra kieu du lieu va do dai dau vao."""
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError(
            f"{name} must be bytes, bytearray, or memoryview"
        )
    data_bytes = bytes(data)
    if len(data_bytes) != expected_len:
        raise ValueError(
            f"{name} length must be exactly {expected_len} bytes"
        )
    return data_bytes
def _rot_word(word: bytes) -> bytes:
    """Xoay trai mot tu gom 4 byte."""
    return word[1:] + word[:1]

def _sub_word(word: bytes) -> bytes:
    """Thay the moi byte bang gia tri trong bang SBOX."""
    return bytes(SBOX[value] for value in word)
def expand_key(key: ByteData) -> tuple[bytes, ...]:
    """
    Mo rong khoa AES-128 thanh 11 khoa vong.
    Dau vao: khoa 16 byte.
    Dau ra: tuple gom 11 khoa, moi khoa 16 byte.
    """
    key = _validate_input(key, 16, "key")

    # Chia khoa ban dau thanh 4 tu, moi tu 4 byte.
    words = [
        key[i:i + 4]
        for i in range(0, 16, 4)
    ]

    # AES-128 can tong cong 44 tu (W0 den W43).
    for i in range(4, 44):
        temp = words[i - 1]

        # Moi khi bat dau mot nhom 4 tu moi,
        # thuc hien RotWord, SubWord va XOR voi RCON.
        if i % 4 == 0:
            temp = _sub_word(_rot_word(temp))

            rcon_value = bytes((RCON[i // 4], 0, 0, 0))
            temp = bytes(
                a ^ b for a, b in zip(temp, rcon_value)
            )

        # Wi = W(i-4) XOR temp.
        new_word = bytes(
            a ^ b for a, b in zip(words[i - 4], temp)
        )
        words.append(new_word)

    # Ghep moi 4 tu thanh mot khoa vong 16 byte.
    round_keys = tuple(
        b"".join(words[i:i + 4])
        for i in range(0, 44, 4)
    )

    return round_keys