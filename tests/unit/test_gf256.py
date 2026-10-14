"""TV1 - GF(2^8) with polynomial 0x11B. Expected values: FIPS-197 sec. 4.2 (independent of LEX)."""
import unittest

from lex.core.gf256 import POLY, gmul, xtime


class TestXtime(unittest.TestCase):
    def test_poly(self):
        self.assertEqual(POLY, 0x11B)

    def test_fips197_chain(self):          # FIPS-197 sec. 4.2.1
        chain = [0x57, 0xAE, 0x47, 0x8E, 0x07]
        for a, b in zip(chain, chain[1:]):
            self.assertEqual(xtime(a), b)

    def test_reduction_boundary(self):
        self.assertEqual(xtime(0x80), 0x1B)
        self.assertEqual(xtime(0x7F), 0xFE)
        self.assertEqual(xtime(0x00), 0x00)

    def test_range(self):
        for bad in (-1, 256, 1000):
            with self.assertRaises(ValueError):
                xtime(bad)


class TestGmul(unittest.TestCase):
    def test_fips197_example(self):        # {57} x {83} = {c1}
        self.assertEqual(gmul(0x57, 0x83), 0xC1)
        self.assertEqual(gmul(0x57, 0x13), 0xFE)

    def test_identity_zero_and_two(self):
        for a in range(256):
            self.assertEqual(gmul(a, 1), a)
            self.assertEqual(gmul(a, 0), 0)
            self.assertEqual(gmul(a, 2), xtime(a))
            self.assertEqual(gmul(a, 3), xtime(a) ^ a)

    def test_commutative_and_distributive(self):
        for a in range(0, 256, 7):
            for b in range(0, 256, 11):
                self.assertEqual(gmul(a, b), gmul(b, a))
                for c in (0x1B, 0x53, 0xCA):
                    self.assertEqual(gmul(a, b ^ c), gmul(a, b) ^ gmul(a, c))

    def test_every_nonzero_has_inverse(self):
        for a in range(1, 256):
            self.assertTrue(any(gmul(a, b) == 1 for b in range(1, 256)), a)

    def test_range(self):
        for a, b in ((256, 1), (1, 256), (-1, 1), (1, -1)):
            with self.assertRaises(ValueError):
                gmul(a, b)


class TestAgainstLogExp(unittest.TestCase):
    """Gate G1: 10,000 random pairs checked against an independent log/exp table (generator 0x03)."""

    def test_random_pairs_vs_log_exp(self):
        import random
        exp, log, x = [0] * 255, [0] * 256, 1
        for i in range(255):
            exp[i], log[x] = x, i
            x ^= xtime(x)                      # x *= 0x03
        rng = random.Random(10_000)
        for _ in range(10_000):
            a, b = rng.randrange(256), rng.randrange(256)
            want = 0 if a == 0 or b == 0 else exp[(log[a] + log[b]) % 255]
            self.assertEqual(gmul(a, b), want, (a, b))


if __name__ == "__main__":
    unittest.main()
