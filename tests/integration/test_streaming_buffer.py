"""TV6 - streaming / chunking properties of KeystreamBuffer and LEX.keystream."""
import random
import unittest

from lex.lex.api import LEX
from lex.lex.iv_setup import compute_s0, make_key_context
from lex.lex.keystream import KeystreamBuffer

K0 = bytes(16)
KEY = bytes(range(16))
IV = bytes(range(16, 32))


def one_shot(n: int) -> bytes:
    return LEX(KEY, IV).keystream(n)


class TestChunking(unittest.TestCase):
    def test_spec_example_5_then_35(self):
        c = LEX(KEY, IV)
        self.assertEqual(c.keystream(5) + c.keystream(35), one_shot(40))

    def test_boundaries_around_40(self):
        for split in (1, 7, 39, 40, 41, 79, 80, 81, 100):
            with self.subTest(split=split):
                c = LEX(KEY, IV)
                self.assertEqual(c.keystream(split) + c.keystream(200 - split), one_shot(200))

    def test_single_byte_reads(self):
        c = LEX(KEY, IV)
        self.assertEqual(b"".join(c.keystream(1) for _ in range(130)), one_shot(130))

    def test_random_chunk_sizes(self):
        rng = random.Random(20260814)
        for trial in range(25):
            sizes = [rng.randint(0, 120) for _ in range(rng.randint(1, 12))]
            with self.subTest(trial=trial, sizes=sizes):
                c = LEX(KEY, IV)
                self.assertEqual(b"".join(c.keystream(s) for s in sizes), one_shot(sum(sizes)))

    def test_zero_reads_do_not_advance(self):
        c = LEX(KEY, IV)
        self.assertEqual(c.keystream(0) + c.keystream(40), one_shot(40))

    def test_keystream_and_process_share_state(self):
        c = LEX(KEY, IV)
        a = c.keystream(7)
        b = c.process(bytes(33))            # XOR with zeros exposes the keystream
        self.assertEqual(a + b, one_shot(40))


class TestKeystreamBufferDirect(unittest.TestCase):
    def _buf(self):
        ctx = make_key_context(KEY)
        return KeystreamBuffer(ctx, compute_s0(ctx, IV))

    def test_read_matches_api(self):
        buf = self._buf()
        self.assertEqual(buf.read(3) + buf.read(37), one_shot(40))

    def test_read_zero_and_invalid(self):
        buf = self._buf()
        self.assertEqual(buf.read(0), b"")
        with self.assertRaises(ValueError):
            buf.read(-1)
        with self.assertRaises(TypeError):
            buf.read(1.0)


if __name__ == "__main__":
    unittest.main()
