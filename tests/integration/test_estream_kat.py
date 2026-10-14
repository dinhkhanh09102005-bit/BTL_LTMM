"""TV6 - KAT from the LEX-v2 reference package (tests/vectors/estream_lex_kat.json).

These vectors were produced by the submitter's own C code (file name: "unverified"),
so passing shows consistency with the reference implementation, not independent proof.
The 8 long vectors (131072 bytes) are slow in pure Python; they are separate test
methods (use `-k short` to iterate quickly) but are NOT skipped in the strict gate.
"""
import unittest

from lex.lex.api import LEX
from tests.support.kat import check_kat_vector, load_kat


def _keystream(key: bytes, iv: bytes, n: int) -> bytes:
    return LEX(key, iv).keystream(n)


class TestEstreamKat(unittest.TestCase):
    def _run(self, predicate):
        ran = 0
        for v in load_kat():
            if predicate(v):
                with self.subTest(set=v["set"], vector=v["vector"]):
                    self.assertEqual(check_kat_vector(v, _keystream), [])
                ran += 1
        self.assertGreater(ran, 0)

    def test_kat_short(self):
        self._run(lambda v: v["stream_length"] <= 512)

    def test_kat_long(self):
        self._run(lambda v: v["stream_length"] > 512)


if __name__ == "__main__":
    unittest.main()
