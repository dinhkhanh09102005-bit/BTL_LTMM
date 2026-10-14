# Nguồn vector
- `reference_trace.json`: sinh bởi `tools/ref_diff/build_reference_trace.py` từ `lex/v2/lex.c` (eSTREAM Phase 3). Ghi sha256 của `lex.c` trong file.
- Vector đi kèm mã tham chiếu: `unverified.test-vectors` trong gói `lex/v2/` (96 vector, 512 byte keystream mỗi vector). Tên file là "unverified": vector do chính tác giả sinh từ mã C, nên khớp với chúng chứng minh nhất quán với mã tham chiếu, chưa phải kiểm chứng độc lập. Chuyển sang `estream_lex_kat.json` khi viết `test_estream_kat.py`.
- AES: NIST FIPS-197 Appendix B/C.
