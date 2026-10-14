"""TV3 - các quan sát về key schedule AES-128 dùng trong tấn công Dunkelman-Keller lên LEX.

Nguồn: O. Dunkelman, N. Keller, "A New Attack on the LEX Stream Cipher", ASIACRYPT 2008,
Observation 3 và Observation 4 (k_r(i, j) = byte hàng i, cột j của khóa vòng r; chỉ số phẳng 4*j + i).
Đây là kiểm tra thực nghiệm trên bản cài đặt của nhóm với nhiều khóa ngẫu nhiên.
"""
import random
import unittest

from lex.aes.key_schedule import expand_key
from lex.aes.sbox import RCON, SBOX


def k(rks, r, i, j):
    return rks[r][4 * j + i]


class TestDunkelmanKellerObservations(unittest.TestCase):
    def keys(self):
        rng = random.Random(2008)
        yield bytes(16)
        yield bytes(range(16))
        for _ in range(200):
            yield bytes(rng.randrange(256) for _ in range(16))

    def test_observation_3(self):
        for key in self.keys():
            rks = expand_key(key)
            for r in range(0, 9):                      # cần r + 2 <= 10
                for i in range(4):
                    self.assertEqual(k(rks, r + 2, i, 0) ^ k(rks, r + 2, i, 2), k(rks, r, i, 2))
                    self.assertEqual(k(rks, r + 2, i, 1) ^ k(rks, r + 2, i, 3), k(rks, r, i, 3))

    def test_observation_4(self):
        for key in self.keys():
            rks = expand_key(key)
            for r in range(0, 9):
                for i in range(4):
                    rcon = RCON[r + 1] if i == 0 else 0   # RCON dùng khi sinh khóa vòng r + 2 (RCON[0] ứng khóa vòng 1)
                    lhs = k(rks, r + 2, i, 1) ^ SBOX[k(rks, r + 1, (i + 1) % 4, 3)] ^ rcon
                    self.assertEqual(lhs, k(rks, r, i, 1), (key.hex(), r, i))


if __name__ == "__main__":
    unittest.main()
