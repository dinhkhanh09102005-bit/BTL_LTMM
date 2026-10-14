# Tests

| File | Owner | Expected values from |
|---|---|---|
| unit/test_gf256, test_matrix_state | TV1 | FIPS-197 §4.2, conventions.md |
| unit/test_sbox, test_transforms | TV2 | FIPS-197 Hình 7 (S-box), App. C.1 round 1 |
| unit/test_aes, test_key_schedule_properties | TV3 | FIPS-197 App. A.1, B, C.1; Observation 3 và 4 của Dunkelman–Keller |
| unit/test_extractor, test_round_engine, integration/test_lex_engine | TV4 | vectors/reference_trace.json (C code) |
| unit/test_validation, test_iv_setup | TV5 | reference_trace.json (swap32 of the IV) |
| integration/test_api, test_streaming_buffer, test_estream_kat | TV6 | reference_trace.json, estream_lex_kat.json |

Run: `python run_tests.py` (all), `python run_tests.py --fast` (skip 8 long vectors).

Evidence levels: FIPS-197 = independent standard. reference_trace.json / estream_lex_kat.json come from the
LEX authors' own C code ("unverified.test-vectors"): they show consistency with the reference code only.
Test runs are TDD: until a module exists its tests ERROR on import.
