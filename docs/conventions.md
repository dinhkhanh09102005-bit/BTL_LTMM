# Quy ước chung (Gate G0)

> Trạng thái: các điểm thuật toán ở mục 5 đã được xác minh với `lex.c` (LEX-v2).

## 1. Kiểu dữ liệu

- Đầu vào công khai (`key`, `iv`, `plaintext`, `ciphertext`): chấp nhận `bytes`, `bytearray`, `memoryview`.
- Từ chối `str`, `int`, `list` bằng `TypeError`. Sai độ dài khóa/IV: `ValueError`.
- `lex/validation.py` chuẩn hóa mọi đầu vào thành `bytes` ngay tại biên. Các module bên trong chỉ làm việc với `bytes`/`bytearray`.
- Mọi hàm có type hints (PEP 484).

## 2. Ma trận trạng thái

- Trạng thái AES/LEX là `bytearray` độ dài **16**, thứ tự **column-major**.
- Ô hàng `r`, cột `c` (0 ≤ r, c ≤ 3) nằm ở chỉ số `idx = 4*c + r`.
- Không dùng `list[list[int]]` ở bất kỳ ranh giới module nào.
- Hàm biến đổi (`sub_bytes`, `shift_rows`, `mix_columns`, `add_round_key`) là **hàm thuần**: nhận state, trả về `bytearray` mới, không sửa tại chỗ.

## 3. Trường GF(2^8)

- Đa thức tối giản: `m(x) = x^8 + x^4 + x^3 + x + 1` (`0x11B`).
- Phần tử là `int` trong `[0, 255]`.

## 4. Đánh số

- Vòng: **1..10** (`for r in range(1, 11)`). Đây là quy ước nội bộ của nhóm để khớp công thức; mọi log/trace cũng đánh số 1..10.
- Round key: `round_keys[0..10]`, mỗi phần tử `bytes` dài 16.
- Vị trí byte rò rỉ luôn ghi theo **chỉ số byte 0..15** (theo mục 2), **không** ghi theo cặp `(hàng, cột)` để tránh hiểu ngược.

## 5. Các điểm đã xác minh với `lex.c` (LEX-v2, eSTREAM Phase 3)

Nguồn: `lex/v2/lex.c` (hàm `LEX_ivsetup`, `rijndaelEncrypt`, `ECRYPT_ivsetup`, `ECRYPT_keystream_bytes`).
Đối chiếu: mô hình độc lập khớp C trên 200 cặp key/IV ngẫu nhiên và **96/96** vector trong `unverified.test-vectors` của chính gói tham chiếu.

| # | Điểm | Kết quả (từ code C) |
|---|------|---------------------|
| T1 | Vòng 10 có `MixColumns`? | **Có.** Chu kỳ sinh khóa dùng 10 vòng giống hệt nhau (SB→SR→MC→ARK), kể cả vòng 10. Chỉ pha IV setup dùng AES chuẩn. |
| T2 | Trích trước/sau `AddRoundKey`? | **Sau ARK** của vòng đó (code ghi: "leak after the key addition of each round"). |
| T3 | Chỉ số byte rò rỉ (idx = 4*c + r) | Vòng **lẻ** (1,3,5,7,9): byte **{0, 2, 8, 10}**, ghi vào keystream theo thứ tự **10, 2, 8, 0**. Vòng **chẵn** (2,4,6,8,10): byte **{1, 3, 9, 11}**, thứ tự **11, 3, 9, 1**. |
| T4 | Trạng thái chu kỳ kế | `S10` (sau vòng 10, đã MC và ARK K10) là đầu vào trực tiếp vòng 1 của chu kỳ sau. **Không** cộng K0, không có biến đổi xen giữa. Chu kỳ đầu dùng `S0`. |
| T5 | 40 byte keystream đầu tiên của Key=0, IV=0 | `FF27889A64BBC76D9D9548F2E50FCB4F5BC4F94DEDC76FC23347ED94AB279CE4F5F608648D8B5EE8`. Chuỗi `B4DEE29E...` trong tài liệu cũ **sai**, không dùng. |
| T6 | Đánh số vòng | Vòng `r` dùng `K_r` = `round_keys[r]`, r = 1..10 (khớp quy ước nhóm). |
| T7 | **Thứ tự byte của IV** | `ECRYPT_ivsetup` nạp IV bằng `U8TO32_LITTLE`, còn bảng Te đọc từ là big-endian. Do đó **khối đưa vào AES = IV với mỗi nhóm 4 byte bị đảo ngược** (`iv[3],iv[2],iv[1],iv[0],iv[7],...`). Với IV toàn 0 không thấy khác biệt; 19/19 vector có IV khác 0 chỉ khớp khi đảo. Key thì nạp big-endian bình thường. |
| T8 | Thứ tự byte keystream | Mỗi vòng sinh một từ 32 bit, ghi ra **little-endian** (byte thấp trước), nên có thứ tự `10,2,8,0` / `11,3,9,1` ở T3. |

`S0 = AES-128_K(IV')` với `IV'` ở T7, dùng AES chuẩn (vòng cuối không `MixColumns`, không trích leak). Với Key=0, IV=0: `S0 = 66E94BD4EF8A2C3B884CFA59CA342B2E`.

Vector đối chiếu máy đọc được: `tests/vectors/reference_trace.json` (sinh bằng `tools/ref_diff/build_reference_trace.py`).

## 6. Test và vector

- Vector chuẩn chỉ lấy từ: NIST FIPS-197 / SP 800-38A, KAT eSTREAM, trace sinh từ C tham chiếu.
- Mọi file vector ghi nguồn trong `tests/vectors/SOURCES.md`.
- Không chấp nhận chỉ kiểm tra `decrypt(encrypt(m)) == m`.

## 7. Phân định AES chuẩn và chu kỳ sinh khóa LEX

| Đặc điểm | IV Setup (`aes/standard_aes.py`) | Chu kỳ sinh dòng (`lex/round_engine.py`) |
|---|---|---|
| Mục đích | `S0 = AES_K(IV')` | Sinh 40 byte keystream / chu kỳ |
| Pre-whitening `AddRoundKey(K0)` | Có | **Không** |
| `MixColumns` ở vòng 10 | Không (AES chuẩn) | **Có** |
| Trích rò rỉ | Không | 4 byte/vòng, sau ARK, theo T3 |

## 8. Ngữ nghĩa bổ sung

- `shift_rows`: hàng `r` dịch trái `r` vị trí (theo FIPS-197).
- `add_round_key`: round key 16 byte được đọc theo cùng thứ tự column-major với state.
- XOR (`^`) là phép cộng trong GF(2^8); không dùng `+`.
- Ngoại lệ: sai kiểu → `TypeError`; sai độ dài/giá trị → `ValueError`. `n_bytes` không phải `int` → `TypeError`, `n_bytes < 0` → `ValueError`.
- `KeyContext` bất biến (`frozen=True`, round keys là `tuple[bytes, ...]` hoặc `list` không bị sửa ngoài module).
- Gate G0 chỉ đóng khi cả 6 thành viên xác nhận trên PR; không có kiểm tra tự động.
