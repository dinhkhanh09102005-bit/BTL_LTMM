"""TV5 only: API tests with fake TV3/TV4 dependencies, NOT LEX KAT."""
import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch


ZERO = bytes(16)


def check_bytes(data):
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("Expected bytes-like data")
    return bytes(data)


def check_key_or_iv(data):
    result = check_bytes(data)
    if len(result) != 16:
        raise ValueError("Expected exactly 16 bytes")
    return result


def fake_make_key_context(key):
    return SimpleNamespace(round_keys=[key] * 11)


def fake_compute_s0(key_ctx, iv):
    return bytearray(iv)


def fake_lex_cycle(state, round_keys):
    # Deterministic TEST ONLY: returns 40 bytes and the next state.
    count = int.from_bytes(state[:4], "big")
    offset = (sum(state[4:]) + round_keys[0][0]) % 256
    stream = bytes((offset + 40 * count + i) % 256 for i in range(40))
    new_state = bytearray(state)
    new_state[:4] = (count + 1).to_bytes(4, "big")
    return stream, new_state


class TestAPIIsolated(unittest.TestCase):
    def setUp(self):
        validation = types.ModuleType("lex.lex.validation")
        validation.validate_key = check_key_or_iv
        validation.validate_iv = check_key_or_iv
        validation.validate_data = check_bytes

        setup = types.ModuleType("lex.lex.iv_setup")
        setup.make_key_context = fake_make_key_context
        setup.compute_s0 = fake_compute_s0

        engine = types.ModuleType("lex.lex.round_engine")
        engine.lex_cycle = fake_lex_cycle

        self.patcher = patch.dict(sys.modules, {
            "lex.lex.validation": validation,
            "lex.lex.iv_setup": setup,
            "lex.lex.round_engine": engine,
        })
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        sys.modules.pop("lex.lex.api", None)
        self.addCleanup(lambda: sys.modules.pop("lex.lex.api", None))
        self.api = importlib.import_module("lex.lex.api")

    def test_keystream_starts_at_zero_and_crosses_40(self):
        obj = self.api.LEX(ZERO, ZERO)
        self.assertEqual(obj.keystream(100), bytes(range(100)))

    def test_keystream_split_equals_single(self):
        obj = self.api.LEX(ZERO, ZERO)
        out = obj.keystream(7) + obj.keystream(35) + obj.keystream(78)
        self.assertEqual(out, self.api.LEX(ZERO, ZERO).keystream(120))

    def test_process_xor(self):
        plaintext = b"ABC"
        self.assertEqual(self.api.LEX(ZERO, ZERO).process(plaintext), b"ACA")
        # 0x41^0x00=0x41; 0x42^0x01=0x43; 0x43^0x02=0x41

    def test_roundtrip_with_new_session(self):
        plaintext = b"HELLO - TV5 - STREAM API"
        ciphertext = self.api.encrypt(ZERO, ZERO, plaintext)
        self.assertEqual(self.api.decrypt(ZERO, ZERO, ciphertext), plaintext)

    def test_process_chunks_equal_one_call(self):
        data = bytes(range(135))
        one = self.api.LEX(ZERO, ZERO).process(data)
        obj = self.api.LEX(ZERO, ZERO)
        split = obj.process(data[:3]) + obj.process(data[3:40]) + obj.process(data[40:])
        self.assertEqual(split, one)

    def test_keystream_and_process_share_position(self):
        obj = self.api.LEX(ZERO, ZERO)
        prefix = obj.keystream(7)
        encrypted = obj.process(b"AB")
        recovered_keystream = bytes(a ^ b for a, b in zip(encrypted, b"AB"))
        self.assertEqual(prefix + recovered_keystream, bytes(range(9)))

    def test_empty_input_does_not_consume(self):
        obj = self.api.LEX(ZERO, ZERO)
        self.assertEqual(obj.process(b""), b"")
        self.assertEqual(obj.keystream(0), b"")
        self.assertEqual(obj.keystream(5), bytes(range(5)))

    def test_accepts_bytes_like(self):
        expected = self.api.encrypt(ZERO, ZERO, b"ABC")
        actual = self.api.encrypt(bytearray(ZERO), memoryview(ZERO), memoryview(b"ABC"))
        self.assertEqual(actual, expected)

    def test_rejects_invalid_key_iv_and_data(self):
        with self.assertRaises(TypeError):
            self.api.LEX("not bytes", ZERO)
        with self.assertRaises(ValueError):
            self.api.LEX(ZERO, bytes(15))
        with self.assertRaises(TypeError):
            self.api.LEX(ZERO, ZERO).process("text")

    def test_rejects_bad_keystream_length(self):
        obj = self.api.LEX(ZERO, ZERO)
        with self.assertRaises(ValueError):
            obj.keystream(-1)
        for bad in (1.5, True, None, "3"):
            with self.subTest(value=bad), self.assertRaises(TypeError):
                obj.keystream(bad)

    def test_different_key_or_iv_change_mock_stream(self):
        ks = self.api.LEX(ZERO, ZERO).keystream(40)
        self.assertNotEqual(ks, self.api.LEX(bytes([1]) + bytes(15), ZERO).keystream(40))
        self.assertNotEqual(ks, self.api.LEX(ZERO, bytes(15) + bytes([1])).keystream(40))


if __name__ == "__main__":
    unittest.main()
