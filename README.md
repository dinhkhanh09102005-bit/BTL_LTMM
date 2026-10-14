# LEX — Dự án triển khai mã hóa dòng bằng Python

## 1. Mục tiêu dự án

Triển khai thuật toán mã dòng **LEX (Leak EXtraction)** theo bản dự thi eSTREAM Phase 3 (**LEX-128, mã tham chiếu v2**), bảo đảm module hóa, kiểm chứng từng tầng biến đổi và đối soát với mã C tham chiếu.

### Sản phẩm bàn giao

1. Mã nguồn Python có type hints, chạy và kiểm thử độc lập từng tầng.
2. Unit test cho GF(2⁸), S-box, `SubBytes`/`ShiftRows`/`MixColumns`/`AddRoundKey`, `KeyExpansion`.
3. Test cơ chế rò rỉ: trích 4 byte mỗi vòng, đủ 40 byte keystream sau 10 vòng.
4. Integration test cho IV setup, sinh keystream liên tục và API mã hóa/giải mã.
5. Đối soát Test Vector (NIST FIPS-197 và KAT của gói tham chiếu LEX). **Không** chấp nhận chỉ kiểm tra `decrypt(encrypt(m)) == m`.
6. Tài liệu thiết kế, báo cáo phân tích an toàn (tấn công Dunkelman–Keller) và slide.

> **Phạm vi bảo mật:** LEX là mã dòng đối xứng không có MAC. Dự án phục vụ học thuật, không dùng bảo vệ dữ liệu thật.

---

## 2. Phân công — 6 thành viên

| Mã | Vai trò | Nhánh | File phụ trách (trong `src/lex/`) | Điều kiện hoàn thành |
|---|---|---|---|---|
| **TV1** | Số học & trường hữu hạn | `feature/gf256-matrix` | `core/gf256.py`, `core/matrix_state.py` | `test_gf256`, `test_matrix_state` đạt |
| **TV2** | Biến đổi AES | `feature/aes-primitives` | `aes/sbox.py`, `aes/transforms.py` | `test_transforms` đạt (từng bước FIPS-197 C.1) |
| **TV3** | Key schedule & AES chuẩn | `feature/aes-core` | `aes/key_schedule.py`, `aes/standard_aes.py` | `test_aes` đạt (FIPS-197 A.1, B, C.1) |
| **TV4** | Động cơ vòng LEX & leak | `feature/lex-engine` | `lex/round_engine.py`, `lex/extractor.py` | `test_extractor`, `test_lex_engine` đạt |
| **TV5** | Ngữ cảnh & IV setup | `feature/context-setup` | `lex/validation.py`, `lex/context.py`, `lex/iv_setup.py` | `test_validation`, `test_iv_setup` đạt |
| **TV6** | Keystream buffer & API | `feature/stream-api` | `lex/keystream.py`, `lex/api.py`, `run_demo.py` | `test_api`, `test_streaming_buffer`, `test_estream_kat` đạt |

### 2.1. Ma trận test (tên file đúng với bộ test hiện có)

| TV | File test | Nội dung chính |
|---|---|---|
| TV1 | `tests/unit/test_gf256.py`, `test_matrix_state.py` | Đa thức 0x11B; chuỗi xtime FIPS-197; 10.000 cặp ngẫu nhiên đối chiếu bảng log/exp (G1); `idx = 4c + r` |
| TV2 | `tests/unit/test_transforms.py` | S-box là hoán vị + giá trị mẫu; SB→SR→MC→ARK vòng 1 của FIPS C.1; hướng ShiftRows; 6 cột MixColumns mẫu |
| TV3 | `tests/unit/test_aes.py` | Key schedule và mã hóa khối theo FIPS-197 A.1, B, C.1; `AES(0,0)=66E94BD4…` |
| TV4 | `tests/unit/test_extractor.py`, `tests/integration/test_lex_engine.py` | Chỉ số leak và thứ tự byte; đối chiếu từng vòng, 40 byte và S10 của 3 chu kỳ với trace C |
| TV5 | `tests/unit/test_validation.py`, `tests/unit/test_iv_setup.py` | Chặn `str`/`int`/sai độ dài; `KeyContext` bất biến; **đảo byte IV**; S₀ khớp trace |
| TV6 | `tests/integration/test_api.py`, `test_streaming_buffer.py`, `test_estream_kat.py` | Chunking tùy ý (`keystream(3)+keystream(37)` = `keystream(40)`); 96 vector KAT |

### 2.2. Review chéo

Người dùng module làm đầu vào sẽ review module đó.

```
TV1 (GF256/Matrix)      → review bởi TV2
TV2 (AES Transforms)    → review bởi TV3
TV3 (AES Core)          → review bởi TV5
TV4 (LEX Engine/Leak)   → review bởi TV6
TV5 (Context/IV Setup)  → review bởi TV4 và TV6
TV6 (API/Demo)          → review bởi TV1
```

* **Điều phối tích hợp:** TV3 kiểm tra `main`, không tự duyệt PR của mình. Mọi PR cần ít nhất 1 phê duyệt.

---

## 3. Kiến trúc và luồng dữ liệu

```text
LEX-Stream-Cipher/
├── README.md
├── pyproject.toml
├── run_tests.py
├── run_demo.py                    # TV6
├── docs/
│   ├── conventions.md             # Quy ước byte/ma trận, bảng T1–T8 đã chốt
│   ├── module_contracts.md        # Chữ ký hàm đóng băng
│   ├── spec_lex.md                # Đặc tả LEX (đã đối chiếu mã C)
│   ├── team_plan.md
│   └── cryptanalysis_notes.md     # Dunkelman–Keller
├── src/lex/
│   ├── __init__.py
│   ├── core/    gf256.py, matrix_state.py            # TV1
│   ├── aes/     sbox.py, transforms.py               # TV2
│   │            key_schedule.py, standard_aes.py     # TV3
│   └── lex/     extractor.py, round_engine.py        # TV4
│                validation.py, context.py, iv_setup.py   # TV5
│                keystream.py, api.py                 # TV6
├── tests/
│   ├── unit/  integration/  support/kat.py
│   └── vectors/ reference_trace.json, estream_lex_kat.json, SOURCES.md
└── tools/ref_diff/ README.md, trace.c, ecrypt-portable.h,
                    build_reference_trace.py, convert_kat.py
```

### Luồng xử lý

```text
Khóa K (16 byte) ──► KeyExpansion ──► K0..K10
                                         │
IV (16 byte) ──► đảo byte trong từng nhóm 4 byte (IV') ──► AES-128 chuẩn ──► S0
                                (không trích leak)

Mỗi chu kỳ (10 vòng GIỐNG HỆT NHAU, không có K0):
   SubBytes → ShiftRows → MixColumns → AddRoundKey(K_r)      (r = 1..10, vòng 10 CÓ MixColumns)
   rồi trích 4 byte SAU AddRoundKey:
      vòng lẻ  1,3,5,7,9  : state[10], state[2], state[8], state[0]
      vòng chẵn 2,4,6,8,10: state[11], state[3], state[9], state[1]      (idx = 4*cột + hàng)
   10 vòng × 4 byte = 40 byte keystream
   S10 (sau ARK của vòng 10) là đầu vào của vòng 1 ở chu kỳ kế tiếp, không có bước nào xen giữa

keystream ──► buffer 40 byte ──► XOR dữ liệu ──► bản mã
```

Theo ký hiệu `S[hàng][cột]`: vòng lẻ lấy hàng 0,2 × cột 0,2; vòng chẵn lấy hàng **1,3** × cột **0,2**.

---

## 4. Các cổng nghiệm thu (G0–G7)

Không merge module tầng trên khi tầng dưới chưa qua cổng.

```
G0 → G1 (GF256) → G2 (Transforms) → G3 (KeySched & AES) ─┬→ G5 (Context & IV) ─┐
                         └────────→ G4 (LEX Engine) ─────┘                      ├→ G6 (API & KAT) → G7
```

TV3 và TV4 cùng chỉ cần G2 nên làm song song.

* **G0 — Quy ước & hợp đồng:** đã chốt. Ma trận phẳng `bytearray` 16 byte, column-major (`idx = 4c + r`). API nhận `bytes`/`bytearray`/`memoryview`, từ chối `str`/`int` (`TypeError`), sai độ dài (`ValueError`).
* **G1:** `xtime`, `gmul` qua `test_gf256` (gồm 10.000 cặp ngẫu nhiên đối chiếu log/exp).
* **G2:** `sub_bytes`, `shift_rows`, `mix_columns`, `add_round_key` khớp từng bước FIPS-197 C.1.
* **G3:** `expand_key` và `encrypt_block` khớp FIPS-197; `AES(Key=0, IV=0)`:

  `S0 = 66E94BD4EF8A2C3B884CFA59CA342B2E`

* **G4:** `test_extractor` và `test_lex_engine` đạt. Vòng 10 **có** MixColumns. 40 byte đầu của chu kỳ 1 với Key=0, IV=0 phải là:

  `FF27889A64BBC76D9D9548F2E50FCB4F5BC4F94DEDC76FC23347ED94AB279CE4F5F608648D8B5EE8`

* **G5:** `test_validation`, `test_iv_setup` đạt, đặc biệt test đảo byte IV (IV `00112233…FF` cho khối vào AES `3322110077665544BBAA9988FFEEDDCC`). Đối tượng `KeyContext` bất biến.
* **G6:** `keystream(3)` rồi `keystream(37)` bằng `keystream(40)`; cả 96 vector trong `estream_lex_kat.json` đạt (gồm 8 vector dài).
* **G7:** `python run_tests.py --require-reference-trace` đạt 100%, 0 skip. Báo cáo, phân tích Dunkelman–Keller và slide hoàn thiện.

---

## 5. Cài đặt và chạy

```powershell
cd D:\lex_project
py -3 --version                      # >= 3.10
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .

.\.venv\Scripts\python.exe -m unittest tests.unit.test_gf256 -v          # một module
.\.venv\Scripts\python.exe run_tests.py --fast                           # nhanh khi đang code
.\.venv\Scripts\python.exe run_tests.py --require-reference-trace        # nghiệm thu
.\.venv\Scripts\python.exe run_demo.py
```

Tái tạo trace từ mã C (cần `gcc`: MinGW hoặc WSL): xem `tools/ref_diff/README.md`. Lưu ý khi biên dịch `lex.c`: `rijndaelEncrypt` có cảnh báo chỉ số mảng vượt giới hạn, nên biên dịch với `-O0`.

---

## 6. Quy trình Git

* Không commit hoặc push trực tiếp lên `main`. Mỗi phần việc một nhánh `feature/...`:

```powershell
git switch main
git pull --ff-only origin main
git switch -c feature/ten-tinh-nang
git status
git add src/lex/core/gf256.py tests/unit/test_gf256.py     # chỉ file thuộc phạm vi mình
git commit -m "feat(core): implement gf256 and pass unit tests"
git push -u origin feature/ten-tinh-nang
```

### Mẫu Pull Request

```markdown
## 1. Mục tiêu công việc
## 2. Danh sách file thay đổi
- src/lex/...:
- tests/...:
## 3. Kết quả kiểm thử
- Lệnh đã chạy:
- Số test: ... PASS / 0 FAIL / 0 SKIP
- Nguồn vector đối chiếu: NIST FIPS-197 hoặc trace C / KAT của gói tham chiếu LEX
## 4. Tự kiểm tra
- [ ] Type hints (PEP 484)
- [ ] Không sửa file của thành viên khác khi chưa trao đổi
- [ ] Đã rebase/merge main mới nhất
```

Đổi chữ ký hàm: sửa `docs/module_contracts.md` trong PR riêng, có một thành viên dùng hàm đó phê duyệt, rồi mới sửa code.

---

## 7. Giao diện API

Nguồn chính thức là `docs/module_contracts.md`. API công khai (`src/lex/lex/api.py`):

```python
ByteData = Union[bytes, bytearray, memoryview]

class LEX:
    def __init__(self, key: ByteData, iv: ByteData) -> None: ...   # TypeError / ValueError
    def keystream(self, n_bytes: int) -> bytes: ...                # n_bytes >= 0, int
    def process(self, data: ByteData) -> bytes: ...                # XOR; tiêu thụ đúng len(data)

def encrypt(key: ByteData, iv: ByteData, plaintext: ByteData) -> bytes: ...
def decrypt(key: ByteData, iv: ByteData, ciphertext: ByteData) -> bytes: ...
```

---

## 8. Checklist nghiệm thu

* [ ] Chạy trên Python 3.10+, không dùng thư viện mật mã ngoài.
* [ ] IV setup là AES-128 chuẩn trên IV đã đảo byte theo nhóm 4 byte, không trích leak.
* [ ] 10 vòng giống hệt nhau, vòng 10 có MixColumns, leak lấy sau AddRoundKey đúng vị trí ở mục 3.
* [ ] Buffer xử lý đúng số byte lẻ và vượt 40 byte.
* [ ] Đạt cả 96 vector của gói tham chiếu LEX (nêu rõ trong báo cáo đây là nhất quán với mã tham chiếu).
* [ ] Báo cáo phân tích động lực thiết kế (rò rỉ từ AES) và tấn công Dunkelman–Keller; số liệu đã có trong `docs/cryptanalysis_notes.md`.
* [ ] Slide phân bổ nội dung cho từng thành viên.

---

## 9. Tài liệu tham khảo

1. Alex Biryukov, *The Design of a Stream Cipher LEX*, Selected Areas in Cryptography (SAC) 2006, LNCS 4356, pp. 67–75, Springer, 2007 (thông tin trích dẫn lấy từ danh mục tài liệu tham khảo của bài Dunkelman–Keller).
2. NIST, *FIPS PUB 197: Advanced Encryption Standard*, 2001.
3. Orr Dunkelman, Nathan Keller, *A New Attack on the LEX Stream Cipher*, ASIACRYPT 2008, LNCS 5350, Springer (DOI 10.1007/978-3-540-89255-7_33): khoảng 2^36,3 byte keystream và 2^112 phép tính. Bản tạp chí: *Cryptanalysis of the stream cipher LEX*, Designs, Codes and Cryptography 67(3), 357–373, 2013 (khoảng 2^40 byte, 2^100 phép mã hóa AES). Số liệu đã đối chiếu với bản ASIACRYPT trên trang IACR.
4. Trang eSTREAM của LEX: `http://www.ecrypt.eu.org/stream/lexp3.html` (có bản lưu Wayback Machine 2012-07-01). Mã tham chiếu cũng có trong SUPERCOP, thư mục `crypto_stream/lexv2/`.
