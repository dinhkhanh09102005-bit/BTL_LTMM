# Đặc tả LEX-128 (v2) dùng cho dự án

Nguồn xác minh: mã tham chiếu `lex/v2/lex.c` (eSTREAM Phase 3), hàm `ECRYPT_keysetup`, `ECRYPT_ivsetup`, `LEX_ivsetup`, `rijndaelEncrypt`, `ECRYPT_keystream_bytes`.
Đối chiếu: `tests/vectors/reference_trace.json` (từng vòng) và `tests/vectors/estream_lex_kat.json` (96 vector đi kèm mã tham chiếu).
Quy ước ký hiệu: xem `docs/conventions.md`. Trạng thái là 16 byte, `idx = 4*c + r`, vòng đánh số 1..10.

## 1. Tham số

| | |
|---|---|
| Khóa | 128 bit (16 byte); đọc big-endian từng từ 32 bit như AES |
| IV | 128 bit (16 byte) |
| Khối trạng thái | 128 bit |
| Keystream mỗi chu kỳ | 40 byte (10 vòng x 4 byte) |

## 2. Mở rộng khóa

Đúng AES-128 (`rijndaelKeySetupEnc`): sinh `K_0 .. K_10`, mỗi khóa 16 byte.

## 3. Khởi tạo IV

```
IV'  = swap32(IV)                     # đảo byte trong từng nhóm 4 byte
S_0  = AES-128_K(IV')                 # AES chuẩn: ARK(K0), 9 vòng đủ, vòng 10 không MixColumns
```

- `swap32([b0,b1,b2,b3, b4,b5,b6,b7, ...]) = [b3,b2,b1,b0, b7,b6,b5,b4, ...]`.
- Lý do: `ECRYPT_ivsetup` nạp IV bằng `U8TO32_LITTLE`, còn bảng Te xử lý từ như big-endian.
- Không trích leak trong pha này. `S_0` giữ nguyên ở dạng byte chuẩn (không đảo lại).
- Key=0, IV=0: `S_0 = 66E94BD4EF8A2C3B884CFA59CA342B2E`.

## 4. Chu kỳ sinh keystream

Đầu vào: trạng thái `S` (lần đầu là `S_0`). Với `r = 1..10`:

```
S = SubBytes(S)
S = ShiftRows(S)
S = MixColumns(S)          # có ở CẢ 10 vòng, kể cả vòng 10
S = S xor K_r              # không có K_0 ở đầu chu kỳ
leak_r = bytes S[i] for i in LEAK(r)
```

`LEAK(r)` (chỉ số byte, đúng thứ tự ghi vào keystream):

| Vòng | Chỉ số | Tương ứng `S[hàng][cột]` |
|---|---|---|
| 1, 3, 5, 7, 9 | 10, 2, 8, 0 | `[2][2], [2][0], [0][2], [0][0]` |
| 2, 4, 6, 8, 10 | 11, 3, 9, 1 | `[3][2], [3][0], [1][2], [1][0]` |

Vị trí lấy từ mã C tham chiếu v2 và khớp 96/96 vector của gói; xem `docs/cryptanalysis_notes.md` mục 6 về cách bài báo Dunkelman–Keller mô tả tập vòng chẵn.

Keystream của chu kỳ = `leak_1 || leak_2 || ... || leak_10` (40 byte). Trạng thái sau vòng 10 (`S_10`) là đầu vào trực tiếp của chu kỳ kế tiếp, không có biến đổi hay cộng khóa nào xen giữa.

Thứ tự byte trong mỗi leak là do mã C gom 4 byte vào một từ 32 bit rồi ghi little-endian; khi cài bằng Python chỉ cần ghi đúng thứ tự trong bảng.

## 5. Mã hóa / giải mã

`C = P xor keystream` (giải mã giống hệt). Keystream được dùng liên tục theo byte; nếu yêu cầu không chia hết cho 40 thì phần dư của chu kỳ cuối được giữ trong bộ đệm cho lần gọi sau (`generate(5)` rồi `generate(35)` phải bằng `generate(40)`).

## 6. Khác biệt so với AES chuẩn

| | AES-128 | Chu kỳ LEX |
|---|---|---|
| `ARK(K_0)` đầu vào | Có | Không |
| `MixColumns` vòng 10 | Không | Có |
| Đầu ra | Khối bản mã | 40 byte leak; `S_10` dùng làm đầu vào tiếp |

Chỉ pha IV dùng AES chuẩn.

## 7. Kiểm chứng

- Ví dụ (Key=0, IV=0), vòng 1 sau ARK: `9AEA270705AEB45188BBFF401273AD1D`, leak `FF27889A`.
- 40 byte keystream đầu: `FF27889A64BBC76D9D9548F2E50FCB4F5BC4F94DEDC76FC23347ED94AB279CE4F5F608648D8B5EE8`.
- Phân biệt đảo IV: IV `00112233445566778899AABBCCDDEEFF` cho khối vào AES `3322110077665544BBAA9988FFEEDDCC`.
- Vector đi kèm mã tham chiếu do chính tác giả sinh ra, nên chỉ chứng minh nhất quán với mã C; AES được kiểm chứng độc lập bằng NIST FIPS-197.

## 8. An toàn

LEX bị loại khỏi danh mục cuối của eSTREAM sau tấn công khôi phục khóa của Dunkelman và Keller (ASIACRYPT 2008): khoảng 2^36,3 byte keystream và 2^112 phép tính đơn giản; bản tạp chí (Designs, Codes and Cryptography 2013) cần khoảng 2^40 byte và 2^100 phép mã hóa AES. Không có MAC; dự án chỉ phục vụ học tập. Chi tiết, kèm điểm cần đối chiếu về vị trí byte rò rỉ vòng chẵn: `docs/cryptanalysis_notes.md` (mục 6).
