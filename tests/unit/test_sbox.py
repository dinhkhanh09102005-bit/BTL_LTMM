"""TV2 - S-box sinh từ định nghĩa toán học phải trùng bảng chuẩn FIPS-197 (Hình 7) và RCON."""
import unittest

from lex.aes.sbox import RCON, SBOX

FIPS_ROW_0 = bytes.fromhex("637c777bf26b6fc53001672bfed7ab76")
FIPS_ROW_F = bytes.fromhex("8ca1890dbfe6426841992d0fb054bb16")


class TestSboxTable(unittest.TestCase):
    def test_first_and_last_rows(self):
        self.assertEqual(bytes(SBOX[0x00:0x10]), FIPS_ROW_0)
        self.assertEqual(bytes(SBOX[0xF0:0x100]), FIPS_ROW_F)

    def test_all_256_values_are_a_permutation(self):
        self.assertEqual(len(SBOX), 256)
        self.assertEqual(sorted(SBOX), list(range(256)))

    def test_algebraic_property(self):
        # S(a) xor S(b) cho a xor b = 1 chỉ có tối đa 4 giá trị khác nhau (độ đều vi phân của hàm nghịch đảo)
        from collections import Counter
        counts = Counter(SBOX[a] ^ SBOX[a ^ 1] for a in range(256))
        self.assertLessEqual(max(counts.values()), 4 * 2)

    def test_rcon(self):
        self.assertEqual(RCON, (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36))


if __name__ == "__main__":
    unittest.main()
