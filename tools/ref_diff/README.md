# Đối soát với mã C tham chiếu LEX-v2

1. Lấy `lex_p3`/`lex.tar.gz` từ trang eSTREAM (LEX, Phase 3, "API-compliant C code"), dùng thư mục `lex/v2/` (gồm `lex.c`, `ecrypt-sync.h`).
2. Gói tham chiếu **không** có `ecrypt-portable.h`. File `ecrypt-portable.h` trong thư mục này là shim tối thiểu do nhóm viết (kiểu `u8/u32` và vài macro), không phải bản chính thức.
3. Chạy: `python tools/ref_diff/build_reference_trace.py --src <đường dẫn lex/v2> --out tests/vectors/reference_trace.json`
4. Script biên dịch `trace.c` ở `-O0`, tính từng vòng bằng bảng `Te` của `lex.c`, và **tự assert** kết quả bằng đúng `ECRYPT_keystream_bytes()` của mã chính thức. JSON ghi sha256 của `lex.c` đã dùng.

Ghi chú: `lex.c` bản chính thức có cảnh báo chỉ số mảng `ks[]` trong nhánh `Nr > 10` (không chạy với LEX-128).
