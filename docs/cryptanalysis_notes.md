# Phân tích an toàn của LEX và tấn công Dunkelman–Keller

Nguồn chính: O. Dunkelman, N. Keller, *A New Attack on the LEX Stream Cipher*, ASIACRYPT 2008 (bản đã đọc: `https://iacr.org/archive/asiacrypt2008/53500545/53500545.pdf`). Các số liệu dưới đây lấy từ bản đó, diễn đạt lại. Ký hiệu `b[i][j]` là byte hàng `i`, cột `j`.

## 1. Ý tưởng thiết kế: leak extraction

- Keystream lấy từ **một phần trạng thái trong của AES** ở mỗi vòng, thay vì chỉ lấy đầu ra cuối của khối.
- LEX chạy AES ở chế độ OFB và rò rỉ 32 bit (4 byte) sau mỗi vòng, nên mỗi lần mã hóa cho 10 × 4 = **40 byte**.
- Khởi tạo chỉ tốn một lần mã hóa AES (`S = AES_K(IV)`), và LEX nhanh hơn AES khoảng 2,5 lần theo bài báo.
- Kỳ vọng của thiết kế: độ an toàn tương đương AES. Bài học của tấn công: vài vòng đầu của một mã khối mạnh **không** đủ ngẫu nhiên khi lộ một phần lớn trạng thái.

## 2. Khác biệt của LEX so với AES (đã khớp với bản cài đặt)

Bài báo (chú thích 2) xác nhận LEX dùng AES đã chỉnh: **không có AddRoundKey ban đầu** và **vòng cuối có MixColumns**. Điều này khớp với `lex_cycle` (10 vòng giống nhau, không K0). Pha IV vẫn dùng AES chuẩn.

Giới hạn sử dụng trong phiên bản chỉnh sửa (tweaked): sau 500 lần mã hóa (500 × 40 = 20.000 byte) phải đổi IV, và sau 2³² IV phải đổi khóa. Bản cài đặt của nhóm **không ép** các giới hạn này (vector kiểm thử có luồng dài 131.072 byte); người dùng tự chịu trách nhiệm. Đây là điểm nên nêu trong báo cáo.

## 3. Các tấn công trước đó (chỉ áp dụng cho phiên bản gốc)

| Tấn công | Điều kiện | Ghi chú |
|---|---|---|
| Tấn công trượt lên IV setup (Wu–Preneel, ECRYPT 2005/059) | khoảng 2⁶¹ IV, mỗi IV 20.000 byte | không áp dụng được cho bản chỉnh sửa vì giới hạn 2³² IV |
| Tấn công phân biệt tổng quát (Englund–Hell–Johansson, SASC 2007) | khoảng 2⁶⁵·⁷ lần đồng bộ lại | cũng bị chặn bởi giới hạn IV |

## 4. Tấn công Dunkelman–Keller (ASIACRYPT 2008)

**Kết quả:** khôi phục khóa với khoảng **2³⁶·³ byte** keystream (cùng một khóa, có thể nhiều IV) và **2¹¹² phép tính đơn giản**. Sau bản sơ bộ của tấn công, LEX bị loại khỏi danh mục cuối của eSTREAM.

Cấu trúc ba bước:

1. **Phát hiện trạng thái đặc biệt.** Xét hai lần mã hóa AES cùng khóa có mẫu sai khác đặc biệt: sau vòng `r+1`, sai khác chỉ khác 0 ở 8 byte (`b[0][0], b[0][2], b[1][1], b[1][3], b[2][0], b[2][2], b[3][1], b[3][3]`). Xác suất xảy ra là **2⁻⁶⁴**, nhưng có thể lọc bằng một điều kiện **32 bit** trên keystream: 4 byte rò rỉ của vòng `r+2` có sai khác 0. Trong khoảng 2⁶⁴ cặp có khoảng 2³² cặp qua bộ lọc, nên các bước sau lặp khoảng 2³² lần.
2. **Trích thông tin.** Nhờ mẫu sai khác, kèm việc đoán sai khác ở thêm 8 byte, kẻ tấn công khôi phục được giá trị thật của **16 byte** trạng thái trong cả hai lần mã hóa. Hai tính chất của AES được dùng: (a) với mỗi sai khác vào khác 0 của S-box, mỗi sai khác ra khả dĩ có xác suất 2⁻⁷ (Observation 1), nên tra bảng phân phối sai khác là suy ra được giá trị; (b) MixColumns tuyến tính và khả nghịch, biết 4 trong 8 byte vào/ra thì suy ra 4 byte còn lại (Observation 2).
3. **Đoán và xác định (guess-and-determine).** Biết 16 byte đó, đoán thêm 2 byte khóa vòng là suy ra toàn bộ khóa. Tổng cộng đoán **10 byte = 2⁸⁰** phép tính cho mỗi ứng viên, nhân với 2³² ứng viên cho **2¹¹²**. Bước này dễ song song hóa.

**Vai trò của lịch khóa AES.** Cuộc tấn công dựa mạnh vào cấu trúc đơn giản của key schedule. Hai quan sát then chốt (Observation 3 và 4), với `k_r(i,j)` là byte hàng `i`, cột `j` của khóa vòng `r`:

- Quan sát 3: `k_{r+2}(i,0) ⊕ k_{r+2}(i,2) = k_r(i,2)` và `k_{r+2}(i,1) ⊕ k_{r+2}(i,3) = k_r(i,3)`.
- Quan sát 4: `k_{r+2}(i,1) ⊕ SB(k_{r+1}((i+1) mod 4, 3)) ⊕ RCON_{r+2}(i) = k_r(i,1)`.

Cả hai đã được **kiểm tra thực nghiệm** bằng bản cài đặt của nhóm trên 202 khóa (`tests/unit/test_key_schedule_properties.py`). Biryukov từng gợi ý thay các khóa vòng bằng 1280 bit ngẫu nhiên; bài báo ghi nhận cách này sẽ làm tấn công thất bại (một số quan sát vẫn dùng được).

**Dữ liệu cần thiết.** Có 8 vị trí bắt đầu khả dĩ cho mẫu sai khác nên chỉ cần khoảng 2⁶⁴/8 = 2⁶¹ cặp, tức khoảng 2³¹ lần mã hóa AES, tương ứng khoảng 2³⁶·³ byte keystream (mỗi lần 40 byte).

**Bản cải tiến (tạp chí).** Dunkelman–Keller, *Cryptanalysis of the stream cipher LEX*, Designs, Codes and Cryptography 67(3), 357–373, 2013: khoảng **2⁴⁰ byte** keystream và khoảng **2¹⁰⁰ phép mã hóa AES** (2¹⁰⁰·³ theo bản đã công bố).

## 5. Các quan sát khác trong bài báo

- **Kháng lấy mẫu (sampling resistance) kém:** 32 trong 256 bit trạng thái được xuất trực tiếp mỗi vòng nên kháng lấy mẫu tối đa chỉ 2⁻³². Hệ quả: tấn công đánh đổi thời gian–bộ nhớ–dữ liệu với dữ liệu 2⁸⁸, thời gian và bộ nhớ 2¹¹², tức chỉ có **112 bit an toàn** đối với lớp tấn công này.
- **Mất entropy khi khởi tạo:** `S = AES_K(IV)` là hàm giống ngẫu nhiên của K, nên với một IV cố định chỉ khoảng 63% giá trị S xuất hiện, tức khoảng 2¹²⁷·³ trạng thái.
- **Chênh lệch giữa đặc tả và mã nộp (mục 5.3 của bài báo):** theo Bernstein và được các tác giả kiểm lại, mã tham chiếu của bản **chưa chỉnh sửa** xuất nhầm byte ở vòng chẵn (`b[1][1], b[1][3], b[3][1], b[3][3]` thay vì `b[0][1], b[0][3], b[2][1], b[2][3]`), làm bản đó yếu hơn hẳn (tấn công gặp-ở-giữa chỉ cần 256 bit đầu ra, vẫn 2¹¹² phép tính). Bài học: phải kiểm chứng bản cài đặt theo vector chuẩn.

## 6. Điểm cần nhóm đối chiếu trước khi nộp (vị trí byte rò rỉ)

Vị trí byte rò rỉ trong dự án được lấy từ **mã C tham chiếu v2** (`lex.c`) và khớp 96/96 vector của gói, nên cài đặt đúng theo mã đó. Tuy nhiên có một chênh lệch về cách mô tả cần nêu rõ:

| | Vòng lẻ 1,3,5,7,9 (đánh số từ 1) | Vòng chẵn 2,4,6,8,10 |
|---|---|---|
| Mã C v2 (dự án này, trạng thái sau AddRoundKey) | hàng 0,2 × cột 0,2 | hàng 1,3 × cột 0,2 |
| Mô tả trong bài báo (ký hiệu `b[hàng][cột]`) | `b[0][0], b[0][2], b[2][0], b[2][2]` (suy ra từ bước 2, mục 3.2) | `b[0][1], b[0][3], b[2][1], b[2][3]` (mục 2.3) |

Tập vòng lẻ khớp. Tập vòng chẵn **không khớp** nếu đọc trực tiếp. Một nhận xét tính toán: nếu áp ShiftRows của vòng kế tiếp lên tập hàng 1,3 × cột 0,2 của mã C thì được hàng 1,3 × cột 1,3, chính là tập mà bài báo gán cho mã nộp *lỗi*. Điều này gợi ý hai khả năng (hệ tọa độ trong bài báo khác, hoặc mã v2 vẫn giữ đúng hành vi đó), nhưng **mình chưa kết luận được**; bài báo cũng đánh số vòng từ 0 và hình 2 không đọc được từ văn bản.

Cách xử lý cho báo cáo: đọc Hình 2 trong Biryukov (SAC 2006, LNCS 4356, tr. 67–75) và đối chiếu từng dòng `leak_even` trong `lex.c`; trong bài nộp nên ghi rõ "cài đặt theo mã tham chiếu và vector chính thức của gói LEX v2". Vector là căn cứ nghiệm thu; nếu giảng viên yêu cầu theo mô tả trong bài báo thì chỉ cần đổi `LEAK_INDICES_EVEN` rồi chạy lại, và khi đó các vector sẽ không còn khớp.

## 7. Liên hệ với bản cài đặt Python

- Bản cài đặt không phải là tấn công; nó chỉ sinh keystream. Phần tấn công không được cài đặt.
- Có thể minh họa thực nghiệm hai quan sát về lịch khóa (đã có test) và điều kiện lọc 32 bit (4 byte rò rỉ của vòng `r+2` có sai khác 0 khi hai lần mã hóa cùng khóa thỏa mẫu đặc biệt).
- Hạn chế an toàn khi dùng LEX: không có MAC, không dùng lại cặp (khóa, IV), tôn trọng giới hạn 20.000 byte mỗi IV và 2³² IV mỗi khóa.

## 8. Tài liệu tham khảo

1. A. Biryukov, *The Design of a Stream Cipher LEX*, Selected Areas in Cryptography 2006, LNCS 4356, pp. 67–75, Springer, 2007.
2. A. Biryukov, *A New 128-bit Key Stream Cipher LEX*, ECRYPT report 2005/013; *The Tweak for LEX-128, LEX-192, LEX-256*, ECRYPT report 2006/037.
3. H. Wu, B. Preneel, *Attacking the IV Setup of Stream Cipher LEX*, ECRYPT report 2005/059.
4. O. Dunkelman, N. Keller, *A New Attack on the LEX Stream Cipher*, ASIACRYPT 2008, LNCS 5350, Springer. DOI 10.1007/978-3-540-89255-7_33.
5. O. Dunkelman, N. Keller, *Cryptanalysis of the stream cipher LEX*, Designs, Codes and Cryptography 67(3):357–373, 2013.
6. NIST, *FIPS PUB 197*, 2001.
