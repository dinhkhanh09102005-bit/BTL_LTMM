# Kế hoạch và trạng thái nhóm

## Trạng thái các cổng

| Cổng | Nội dung | Người phụ trách | File test | Trạng thái |
|---|---|---|---|---|
| G0 | Quy ước, hợp đồng module | cả nhóm | `docs/conventions.md`, `module_contracts.md` | Xong |
| G1 | GF(2^8), ma trận | TV1 | `test_gf256`, `test_matrix_state` | Xong (code + test đạt) |
| G2 | S-box, biến đổi AES | TV2 | `test_sbox`, `test_transforms` | Xong |
| G3 | Key schedule, AES chuẩn | TV3 | `test_aes`, `test_key_schedule_properties` | Xong |
| G4 | Động cơ vòng LEX, trích leak | TV4 | `test_extractor`, `test_round_engine`, `test_lex_engine` | Xong |
| G5 | Validation, context, IV setup | TV5 | `test_validation`, `test_iv_setup` | Xong |
| G6 | Keystream buffer, API, demo | TV6 | `test_api`, `test_streaming_buffer`, `test_estream_kat`, `run_demo.py` | Xong |
| G7 | Nghiệm thu, báo cáo, slide | cả nhóm | `python run_tests.py --require-reference-trace` | Còn báo cáo và slide |

## Việc còn lại để nộp bài

1. **Mỗi thành viên đọc và hiểu phần của mình** (kể cả khi code đã có sẵn): chạy test của phần mình, đọc docstring, tự giải thích được từng hàm. Giảng viên có thể hỏi bất kỳ ai về module được giao.
2. Chạy nghiệm thu một lần trên máy nhóm: `python run_tests.py --require-reference-trace` (phải đạt, 0 skip) và `python run_demo.py`.
3. Đối chiếu **vị trí byte rò rỉ vòng chẵn** với Hình 2 của Biryukov (SAC 2006) và `lex.c` (`docs/cryptanalysis_notes.md` mục 6). Quyết định cách ghi trong báo cáo.
4. Xác nhận lại trích dẫn trong báo cáo với bản gốc (README mục 9).
5. Viết báo cáo (khung ở dưới) và slide.
6. Quy trình Git: mỗi người một nhánh `feature/...`, PR có review chéo theo README mục 2.2.

## Khung báo cáo và phân bổ nội dung thuyết trình

| Phần | Nội dung | Người trình bày |
|---|---|---|
| 1 | Bối cảnh eSTREAM, ý tưởng leak extraction, sơ đồ LEX | TV4 |
| 2 | GF(2^8), ma trận trạng thái, quy ước | TV1 |
| 3 | SubBytes, ShiftRows, MixColumns, AddRoundKey; S-box sinh từ định nghĩa | TV2 |
| 4 | Key schedule, AES chuẩn, quan sát 3 và 4 của Dunkelman–Keller | TV3 |
| 5 | Khởi tạo khóa/IV, đảo byte IV, kiểm tra đầu vào | TV5 |
| 6 | Bộ đệm keystream, API, kết quả KAT 96/96, demo | TV6 |
| 7 | Phân tích tấn công Dunkelman–Keller (chia 2 người: TV3 trình bày key schedule, TV4 trình bày mẫu sai khác) | TV3, TV4 |

## Số liệu hiện có để đưa vào báo cáo

- 88 test, đạt hết; 96/96 vector của gói tham chiếu LEX (gồm 8 vector 131.072 byte).
- Tốc độ bản Python thuần: khoảng 0,5 MB/s (`python tools/run_benchmark.py`).
- Mức bằng chứng: AES khớp FIPS-197 (độc lập); LEX khớp mã C và vector do chính tác giả sinh (nhất quán với mã tham chiếu, chưa phải kiểm chứng độc lập).
