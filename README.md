# LEX - Bai tap lon (5 thanh vien)

Day la KHUNG DE TRONG sau khi nhom reset repository; khong khoi phuc code cu.

| TV | Phan viec | Branch | File |
|---|---|---|---|
| TV1 | GF256, AES transforms | feature/gf256-transforms | core/gf256.py, core/matrix_state.py, aes/sbox.py, aes/transforms.py |
| TV2 | Key schedule, AES chuan | feature/aes-core | aes/key_schedule.py, aes/standard_aes.py |
| TV3 | LEX engine, leak | feature/lex-engine | lex/extractor.py, lex/round_engine.py |
| TV4 | Context, IV setup | feature/context-setup | lex/validation.py, lex/context.py, lex/iv_setup.py |
| TV5 | Keystream buffer, API | feature/stream-api | lex/keystream.py, lex/api.py, run_demo.py |

Hop dong: docs/module_contracts.md. Quy uoc va dac ta: docs/conventions.md, docs/spec_lex.md.

Python 3.10+. Test code da co: py -3 run_tests.py

TEST TV5 doc lap voi Engine gia khong thay the full-system KAT.
Khong push truc tiep main; moi thanh vien dung nhanh feature va mo PR.
LEX chi phuc vu hoc tap, khong dung de ma hoa du lieu nhay cam.
