# TV5 - Ban giao Keystream Buffer, API, Demo va kiem thu

## Pham vi nhiem vu TV5

TV5 so huu cac file:
- `src/lex/lex/keystream.py`: giu byte keystream chua dung, doc lien tuc khong lap/bo sot.
- `src/lex/lex/api.py`: `LEX(key, iv)`, `keystream(n_bytes)`, `process(data)`, `encrypt`, `decrypt`.
- `run_demo.py`: minh hoa API, co che do gia lap `--mock`.
- `tests/integration/test_streaming_buffer.py`, `test_api_isolated.py`, `test_tv5_error_cases.py`, `test_tv5_contract.py`.
- `tests/support/mock_lex_dependencies.py`: ho tro demo/test doc lap.

TV5 KHONG thuc hien GF256/AES (TV1/TV2), `lex_cycle` (TV3), `compute_s0` hay `validate_key` (TV4).

## Hop dong can tu cac thanh vien khac

- TV3: `lex.lex.round_engine.lex_cycle(state, round_keys)` tra `(chunk, next_state)`, voi `chunk` dung 40 byte va `next_state` dung 16 byte.
- TV4: `lex.lex.validation.validate_key/validate_iv/validate_data` tra bytes, `lex.lex.iv_setup.make_key_context(key)` tra object co `.round_keys`; `compute_s0(key_ctx, iv)` tra state 16 byte.
- TV1/TV2 cung cap AES cho TV3/TV4, khong phai phan TV5.
- Nhat quan `docs/module_contracts.md` va `docs/spec_lex.md`; Key/IV 16 byte.

## Chay va kiem chung

Tu thu muc goc repository, Python 3.10+:

```powershell
py -3 run_tests.py
py -3 run_demo.py --mock
```

Tat ca test tren la test TV5 voi dependencies gia lap; ket qua PASS **KHONG** chung minh LEX cryptographic KAT. Output gia lap khong duoc su dung de ma hoa du lieu that.

Khi TV1-TV4 da tich hop day du va qua KAT:

```powershell
py -3 run_demo.py
py -3 run_tests.py
```

Phai chay va bao cao vector LEX tham chieu (96 KAT), test key/IV khac 0, kiem tra continuity 39/40/41, va test full system. `decrypt(encrypt(m)) == m` la dieu kien can, khong du xac nhan tinh dung thuat toan.

## Luu y khi su dung API

- `LEX(key, iv)` la mot phien stream co vi tri doc rieng. `process` va `keystream` cung tieu thu mot luong byte.
- `encrypt` va `decrypt` tao phien moi; decrypt can dung key va IV cua encrypt.
- Khong tai su dung cung cap key/IV cho **nhieu ban tin doc lap**: stream cipher reuse keystream co the ro ri thong tin khi XOR.
- LEX la thuat toan phuc vu bai tap, KHONG an toan cho du lieu nhay cam va khong co authentication.
- Khong tua/rewind Buffer; muon bat dau lai phai tao `LEX(key, iv)` moi (chi de giai ma du lieu tuong ung).

## Check-list TV5 truoc khi giao cho nhom

- [x] Buffer doc N byte, giu phan du, tu choi dau vao sai.
- [x] API `LEX/process/encrypt/decrypt` va nhan bytes-like.
- [x] Demo gia lap chay khi TV3/TV4 chua co san.
- [x] Test input errors, boundaries, chunking, multi-session.
- [ ] Integrated demo voi TV1-TV4 that (phu thuoc cac thanh vien).
- [ ] Full-system 96 KAT PASS (phu thuoc ghep code/kiem chung toan nhom).
