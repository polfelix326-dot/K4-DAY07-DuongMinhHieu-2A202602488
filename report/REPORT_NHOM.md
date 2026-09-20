# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** 
**Thành viên:** Dương Minh Hiếu
**Ngày:** 2026-09-19

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Học phí và hỗ trợ học phí/học bổng tại USTH.

**Tại sao nhóm chọn chủ đề này?**
Thông báo của USTH có mức thu, mốc thời gian và hướng dẫn thanh toán cụ thể,
giúp kiểm chứng câu trả lời bằng tài liệu gốc. Bộ tài liệu còn có chính sách
học bổng theo đối tượng để thiết kế thử nghiệm lọc metadata.

### Danh sách tài liệu (Data Inventory)

Số ký tự được tính bằng `len(body.strip())` sau khi bỏ frontmatter, chuẩn hóa
xuống dòng thành LF; bao gồm tiêu đề và ký hiệu Markdown trong phần nội dung.
Mỗi file có một dòng tương ứng trong `data/hoc-phi-usth/sources.csv`.

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | [USTH - Học bổng Tăng cường năng lực cho cán bộ VAST](../data/hoc-phi-usth/hoc-bong-tang-cuong-nang-luc-can-bo.md) | [USTH](https://usth.edu.vn/chinh-sach-hoc-bong-cua-usth-8361/) | 2026-09-19 / `not-stated` | 339 | `audience=staff; category=scholarship; language=vi; source_section=3.2. Học bổng Tăng cường năng lực; eligibility_group=vast-institute-center-staff; temporal_scope=historical-overview` |
| 2 | [USTH - Học bổng Tiếp nối cho người tốt nghiệp USTH](../data/hoc-phi-usth/hoc-bong-tiep-noi-sinh-vien.md) | [USTH](https://usth.edu.vn/chinh-sach-hoc-bong-cua-usth-8361/) | 2026-09-19 / `not-stated` | 275 | `audience=student; category=scholarship; language=vi; source_section=3.1. Học bổng Tiếp nối; eligibility_group=usth-graduate; temporal_scope=historical-overview` |
| 3 | [Mức học phí USTH năm học 2026-2027](../data/hoc-phi-usth/muc-hoc-phi-2026-2027.md) | [USTH](https://usth.edu.vn/thong-bao-quy-dinh-muc-hoc-phi-chinh-thuc-ap-dung-cho-nam-hoc-2026-2027-33107/) | 2026-09-19 / `not-stated` | 1567 | `audience=student; category=tuition-rates; language=vi; academic_year=2026-2027` |
| 4 | [Phí gia hạn đào tạo USTH năm học 2025-2026](../data/hoc-phi-usth/phi-gia-han-dao-tao-2025-2026.md) | [USTH](https://usth.edu.vn/thong-bao-thu-phi-gia-han-dao-tao-nam-hoc-2025-2026-31390/) | 2026-09-19 / `not-stated` | 706 | `audience=student; category=training-extension-fee; language=vi; academic_year=2025-2026` |
| 5 | [Thu học phí USTH học kỳ II năm học 2025-2026](../data/hoc-phi-usth/thu-hoc-phi-hk2-2025-2026.md) | [USTH](https://usth.edu.vn/tb-ve-viec-thu-hoc-phi-hoc-ky-ii-nam-hoc-2025-2026-chuong-trinh-dao-tao-trinh-do-dai-hoc-29249/) | 2026-09-19 / `not-stated` | 1802 | `audience=student; category=tuition-payment; language=vi; academic_year=2025-2026` |

**Phạm vi và tính minh bạch nguồn:** Có 5 file từ 4 URL nguồn độc lập.
Hai file học bổng là bản diễn giải riêng mục 3.1 và 3.2 của cùng một bài tổng
quan cũ; không tính là hai trang nguồn khác nhau và không xác nhận áp dụng
năm 2026-2027. Các thông báo thu phí ghi rõ năm học; không trộn mức phí giữa
2025-2026 và 2026-2027. `document_version=not-stated` nghĩa là chưa xác định
phiên bản của bài thông báo, không lấy ngày crawl làm ngày hiệu lực.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu lấy từ trang công khai của USTH; không chứa hồ sơ cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` và `audience` trong metadata.
- [x] Mỗi tài liệu có trường lọc bổ sung `category` và `language`.
- [x] Có 5 file, `doc_id` duy nhất, khớp tên file và `sources.csv` khớp 1-1.
- [x] Có hai giá trị `audience`: `student` (4 file), `staff` (1 file).

Nguồn bổ sung về phí gia hạn có danh sách sinh viên trong tài liệu nhúng;
chỉ lấy phần HTML thông báo, không tải danh sách. `public-source` trong CSV
là căn cứ nguồn công khai theo quy ước lab, không phải tuyên bố giấy phép mở.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string, bắt buộc | `muc-hoc-phi-2026-2027` | Định danh tài liệu gốc, khớp tên file và CSV; giữ trên mọi chunk. |
| `title` | string, bắt buộc | Mức học phí USTH năm học 2026-2027 | Nhận diện nội dung và hiển thị nguồn. |
| `source_url` | string URL, bắt buộc | URL bài viết USTH ở bảng trên | Truy vết và kiểm chứng đáp án. |
| `retrieved_at` | string YYYY-MM-DD, bắt buộc | `2026-09-19` | Ngày thu thập; không phải ngày hiệu lực. |
| `document_version` | string, bắt buộc | `not-stated` | Ghi phiên bản nếu nguồn nêu; không tự suy đoán. |
| `audience` | enum string, bắt buộc | `student`, `staff` | Lọc theo đối tượng; schema cho phép thêm `faculty`, `all`. |
| `category` | string, bắt buộc trong corpus này | `tuition-rates`, `tuition-payment`, `scholarship`, `training-extension-fee` | Phân biệt mức thu, thanh toán, học bổng và phí gia hạn. |
| `language` | string, bắt buộc trong corpus này | `vi` | Xác định ngôn ngữ; hiện tất cả file là tiếng Việt. |
| `academic_year` | string, tùy tài liệu | `2025-2026`, `2026-2027` | Ngăn lấy nhầm năm học; không gán năm cho bài học bổng tổng quan cũ. |
| `source_section` | string, tùy tài liệu | `3.1. Học bổng Tiếp nối` | Chỉ đúng mục được diễn giải từ nguồn chung. |
| `eligibility_group` | string, tùy tài liệu | `usth-graduate`, `vast-institute-center-staff` | Phân biệt điều kiện đối tượng của hai học bổng. |
| `temporal_scope` | string, tùy tài liệu | `historical-overview` | Đánh dấu bài tổng quan cũ, tránh coi là chính sách hiện hành. |
| `audience_basis` | string, tùy tài liệu | Cán bộ VAST đang học sau đại học | Giải thích vì sao mục học bổng được gán `staff`. |
| `fee_basis` | string, tùy tài liệu | Quyết định số 563/QĐ-ĐHKHCN ngày 01/07/2025 | Lưu căn cứ mức thu được thông báo dẫn chiếu. |
| `extraction_note` | string, tùy tài liệu | Chỉ lấy HTML, chưa trích tài liệu nhúng | Ghi phạm vi trích xuất và giới hạn dữ liệu. |

`staff` mô tả nhóm cán bộ VAST đủ điều kiện học bổng; họ đồng thời có thể là
người học. Đây không phải tài liệu hướng dẫn nhân viên thu học phí. Khi nạp
dữ liệu cần truyền metadata vào mọi chunk, giữ `metadata.doc_id` là tài liệu
gốc và đặt `Document.id` riêng cho từng chunk.

**Kết quả kiểm tra:** `py -3.11 scripts/check_corpus.py` xác nhận cấu trúc dữ liệu.
Đã có A/B CP6 bằng mock ở mục 3; Q5 vẫn chưa chứng minh cần bộ lọc. Điểm rubric còn chờ đánh giá câu trả lời agent.

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Đã chạy `ChunkingStrategyComparator().compare(body, chunk_size=500)` trên
3 tài liệu bên dưới. `body` đã bỏ YAML frontmatter; giữ tiêu đề Markdown.
FixedSize dùng overlap 50, Sentence dùng 3 câu/chunk. Các số liệu và toàn bộ
chunk được lưu tại [`benchmark/baseline_cp5.json`](../benchmark/baseline_cp5.json).
Nhận xét cột cuối mô tả cấu trúc đoạn; chưa kết luận chất lượng retrieval.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình (ký tự) | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `muc-hoc-phi-2026-2027` | `fixed_size` | 4 | 429.25 | Giới hạn 500 ký tự, overlap 50; có thể cắt giữa câu hoặc dòng mức phí. |
| `muc-hoc-phi-2026-2027` | `by_sentences` | 7 | 222.43 | Giữ dấu câu; tối đa 3 câu. Danh sách/bảng ít dấu kết câu có thể tạo chunk dài hơn 500. |
| `muc-hoc-phi-2026-2027` | `recursive` | 4 | 391.75 | Ưu tiên đoạn/dòng và gom mảnh nhỏ; có thể mất tiêu đề ở chunk sau, chưa lặp lại đơn vị bảng. |
| `thu-hoc-phi-hk2-2025-2026` | `fixed_size` | 4 | 488.00 | Giới hạn 500 ký tự, overlap 50; có thể cắt giữa câu hoặc dòng mức phí. |
| `thu-hoc-phi-hk2-2025-2026` | `by_sentences` | 7 | 255.29 | Giữ dấu câu; tối đa 3 câu. Danh sách/bảng ít dấu kết câu có thể tạo chunk dài hơn 500. |
| `thu-hoc-phi-hk2-2025-2026` | `recursive` | 5 | 360.40 | Ưu tiên đoạn/dòng và gom mảnh nhỏ; có thể mất tiêu đề ở chunk sau, chưa lặp lại đơn vị bảng. |
| `phi-gia-han-dao-tao-2025-2026` | `fixed_size` | 2 | 378.00 | Giới hạn 500 ký tự, overlap 50; có thể cắt giữa câu hoặc dòng mức phí. |
| `phi-gia-han-dao-tao-2025-2026` | `by_sentences` | 2 | 349.50 | Giữ dấu câu; tối đa 3 câu. Danh sách/bảng ít dấu kết câu có thể tạo chunk dài hơn 500. |
| `phi-gia-han-dao-tao-2025-2026` | `recursive` | 2 | 353.00 | Ưu tiên đoạn/dòng và gom mảnh nhỏ; có thể mất tiêu đề ở chunk sau, chưa lặp lại đơn vị bảng. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Chiến lược cá nhân đang chạy trong repo — Dương Minh Hiếu**
- **Loại chiến lược:** Heading, `chunk_size=500`.
- **Lý do:** Thông báo USTH phân mục mức phí, thời hạn và thanh toán. Giữ tiêu đề của mục cùng tiêu đề tài liệu trên từng chunk giúp nhận diện nội dung và năm học.
- **Cách xử lý:** Tách trước heading Markdown; section dài được chia bằng RecursiveChunker với ngân sách còn lại sau tiêu đề. Mỗi mảnh con được gắn lại chuỗi heading cha/con. Không nhận dòng `#` trong fenced code block là heading.
- **Giới hạn:** Không tự lặp lại đơn vị/mô tả cột nếu chúng nằm trong thân bảng; heading quá dài so với ngân sách sẽ báo lỗi để tăng chunk_size. Metadata vẫn giữ trên mọi chunk.
- **Mã nguồn:** [`src/heading_chunking.py`](../src/heading_chunking.py).
- **CP5:** `python bench.py` chạy thành công: 5 tài liệu, 19 chunk, 5 câu hỏi, top-3 mỗi câu. Output: [`ket_qua_benchmark.txt`](../ket_qua_benchmark.txt).
- **Cấu hình chung:** MockEmbedder, top_k=3, cùng corpus và `benchmark/usth_queries.json`. Chỉ đổi `DEFAULT_STRATEGY` trong `bench.py` hoặc `--strategy`; chưa dùng API embedding, không phát sinh phí API.
- **Ghi chú:** Tại thời điểm này, dữ liệu benchmark và báo cáo đều chạy trên mock backend, nên kết luận về semantic quality chỉ mang tính tương đối và phải được kiểm tra lại bằng embedder thật trong môi trường có thể cài đặt backend. 

**Thành viên 2 — [Tên]**
- **Loại chiến lược:** FixedSize / Recursive (có thể bổ sung khi nhóm xác nhận thành viên thứ hai).
- **Mô tả & lý do chọn:** Dùng mô hình chia đoạn theo kích thước cố định hoặc theo đoạn/đường phân tách, phù hợp cho dữ liệu dài gồm nhiều bảng mức thu.
- **Code snippet (nếu custom):** Chưa bổ sung trong bản này; lưu lại nháp tích lũy khi nhóm chạy thêm chiến lược độc lập.

**Thành viên 3 — [Tên]**
- **Loại chiến lược:** FixedSize / Recursive (có thể bổ sung khi nhóm xác nhận thành viên thứ ba).
- **Mô tả & lý do chọn:** Khảo sát bổ sung từ cùng corpus để so sánh phân bổ chunk, độ dài và khả năng giữ ngữ cảnh giữa các cấu hình.
- **Code snippet (nếu custom):** Chưa bổ sung trong bản này; lưu lại nháp tích lũy khi nhóm chạy thêm chiến lược độc lập.

### So Sánh Giữa Các Thành Viên

**Hiện đây là phép so sánh ba cấu hình chạy trong cùng repo**, chưa phải kết
quả do ba thành viên độc lập nộp. Giữ trống tên/phân công cho tới khi nhóm xác nhận;
không gán kết quả giả cho thành viên khác.

Backend: **MockEmbedder (MD5), không có ngữ nghĩa**, theo lựa chọn của người làm bài.
Không cài backend thật và không dùng API trả phí. Cả ba cấu hình chạy trên cùng
5 tài liệu, 5 câu hỏi, chunk_size=500, top_k=3; FixedSize overlap=50.
Tập trung phân tích số lượng/độ dài chunk và khả năng giữ điều khoản.
Điểm và thứ hạng mock chỉ mô tả lượt chạy này, không chứng minh chiến lược nào tốt hơn về ngữ nghĩa.

**Hai mức kiểm tra:** `document_hit` chỉ cần doc_id gold có trong top-3;
`evidence_hit` cần đủ mọi chuỗi `evidence_substrings` trong các chunk của đúng
tài liệu gold. Chuỗi được chuẩn hóa khoảng trắng và chữ hoa/thường, không nối
hai mảnh bị cắt để giả lập một câu nguyên vẹn. Đây là phép kiểm tra bằng chuỗi,
có thể bỏ sót cách diễn đạt tương đương và không tự đánh giá tính đúng đắn của LLM.
Điểm proxy retrieval là 2 nếu top-1 đủ bằng chứng, 1 nếu phải dùng tới top-2/3,
0 nếu thiếu. **Không coi proxy là điểm rubric chính thức**: chưa có LLM tổng hợp
để kiểm tra agent trả lời đúng. Agent hiện chỉ trả bản trích ngữ cảnh qua
`llm_fn` được ghi nhãn, không đọc hoặc sao chép gold answer khi tạo output.

| Cấu hình (chưa gán thành viên) | Số chunk | TB ký tự | Đúng doc /5 | Đủ bằng chứng /5 | Proxy /10 | Nhận xét cấu trúc |
|---|---|---|---|---|---|---|
| fixed | 12 | 419.92 | 3 | 0 | 0 | Overlap giữ vùng biên nhưng có thể cắt dòng mức phí và từ. |
| recursive | 13 | 360.69 | 4 | 0 | 0 | Giữ ranh giới đoạn/dòng; không lặp tiêu đề ở từng chunk. |
| heading | 19 | 297.11 | 3 | 2 | 2 | Lặp tiêu đề cha/con; nhiều chunk hơn vì tiêu đề chiếm ngân sách; đơn vị bảng trong thân vẫn có thể bị tách. |

**Chưa chọn chiến lược thắng về ngữ nghĩa.** Với corpus quy định có nhiều mục,
Heading có lợi thế giữ tiêu đề và năm học, nhưng làm tăng số đoạn; cần thêm
đơn vị bảng và đối tượng vào ngữ cảnh từng dòng phí. Kết quả mock không đủ
để kết luận lợi thế retrieval. Failure case Q1 được phân tích tại mục 4.

Output đầy đủ: [fixed](../benchmark/cp6/fixed.txt),
[recursive](../benchmark/cp6/recursive.txt), [heading](../benchmark/cp6/heading.txt).

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

Bộ 5 câu hỏi và đáp án nguồn lưu tại
[`benchmark/usth_queries.json`](../benchmark/usth_queries.json); cả ba chiến lược
đã chạy cùng bộ này. Nhóm vẫn cần xác nhận bộ dùng chung.
Q5 đã chạy A/B bằng mock, nhưng **chưa đạt điều kiện cần filter mới trả lời đúng**.

Hai mục học bổng được tách từ cùng một bài tổng quan cũ (mục 3.1 và 3.2),
không phải hai nguồn độc lập và chưa xác nhận áp dụng năm 2026-2027.
`staff` ở đây chỉ cán bộ VAST đang học sau đại học, không phải cán bộ xử lý
thu học phí. Vai trò cán bộ và người học có thể giao nhau; Q5 giới hạn ngữ
cảnh người hỏi là người tốt nghiệp USTH học tiếp, không xét tư cách cán bộ VAST.

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|---|---|---|
| Q1 | Năm học 2026-2027, học phí theo niên chế của chương trình chuẩn 3 năm và B0 dành cho sinh viên Việt Nam là bao nhiêu?<br>Filter: `{"academic_year": "2026-2027"}` | 59 triệu đồng/năm. | `muc-hoc-phi-2026-2027` — 1. Mức học phí áp dụng cho sinh viên Việt Nam |
| Q2 | Hạn cuối đóng học phí học kỳ II năm học 2025-2026 là ngày nào, và đóng không đúng hạn có hậu quả gì?<br>Filter: `{"academic_year": "2025-2026"}` | Hạn cuối 05/02/2026; sinh viên không hoàn thành đóng học phí đúng hạn không được tham gia các học phần thuộc học kỳ II năm học 2025-2026. | `thu-hoc-phi-hk2-2025-2026` — 3. Thời gian đóng học phí |
| Q3 | Theo thông báo thu học phí học kỳ II năm học 2025-2026, đóng học phí qua đâu và khi nào được xác nhận đã thanh toán?<br>Filter: `{}` | Đăng nhập ERP tại https://erp.usth.edu.vn/students, chọn Học phí và tra cứu hóa đơn, kiểm tra mức phải nộp, quét QR chuyển khoản. Thanh toán được xác nhận khi hóa đơn có trạng thái Đã đóng. | `thu-hoc-phi-hk2-2025-2026` — 4. Phương thức đóng học phí |
| Q4 | Theo thông báo mức học phí năm học 2026-2027, mức thu theo tín chỉ được áp dụng trong những trường hợp nào?<br>Filter: `{"academic_year": "2026-2027"}` | Áp dụng khi đăng ký học theo tín chỉ và đăng ký học lại. | `muc-hoc-phi-2026-2027` — Chú thích cuối bảng |
| Q5 | Khi theo học thạc sĩ hoặc tiến sĩ tại USTH, có loại học bổng nào hỗ trợ học tiếp và dành cho đối tượng nào?<br>Filter: `{"audience": "student"}` | Học bổng Tiếp nối: đã tốt nghiệp đại học hoặc thạc sĩ tại USTH và tiếp tục học thạc sĩ hoặc tiến sĩ tại trường. Đây là thông tin từ bài tổng quan cũ, chưa xác nhận áp dụng năm 2026-2027. | `hoc-bong-tiep-noi-sinh-vien` — Học bổng Tiếp nối (nguồn: mục 3.1) |

Q5 sử dụng ngữ cảnh người hỏi là người tốt nghiệp USTH học tiếp, không xét tư cách cán bộ VAST. Câu hỏi không nói rõ đối tượng; bộ lọc truyền ngữ cảnh đó.

### Tổng hợp chất lượng truy xuất của nhóm

| Câu | Fixed: doc/evidence | Recursive: doc/evidence | Heading: doc/evidence | Kết luận |
|---|---|---|---|---|
| Q1 | 1/0 | 1/0 | 1/0 | Chỉ số chạy mock; chưa chấm LLM |
| Q2 | 1/0 | 1/0 | 1/1 | Chỉ số chạy mock; chưa chấm LLM |
| Q3 | 0/0 | 1/0 | 0/0 | Chỉ số chạy mock; chưa chấm LLM |
| Q4 | 1/0 | 1/0 | 1/1 | Chỉ số chạy mock; chưa chấm LLM |
| Q5 | 0/0 | 0/0 | 0/0 | Chỉ số chạy mock; chưa chấm LLM |

`doc/evidence`: 1 là có, 0 là không; kiểm evidence chỉ nhận nội dung từ đúng
file gold để tránh lấy thông tin giống nhau từ thông báo khác.

### A/B Q5 — có và không có bộ lọc trên ba chiến lược

| Chiến lược | Filter | Top-3: chunk_id, score, audience | Đủ bằng chứng? |
|---|---|---|---|
| fixed | Không lọc | 1. `muc-hoc-phi-2026-2027#0` (0.312793, student)<br>2. `muc-hoc-phi-2026-2027#1` (0.232020, student)<br>3. `muc-hoc-phi-2026-2027#3` (0.157149, student) | Không |
| fixed | audience=student | 1. `muc-hoc-phi-2026-2027#0` (0.312793, student)<br>2. `muc-hoc-phi-2026-2027#1` (0.232020, student)<br>3. `muc-hoc-phi-2026-2027#3` (0.157149, student) | Không |
| recursive | Không lọc | 1. `muc-hoc-phi-2026-2027#0` (0.119306, student)<br>2. `muc-hoc-phi-2026-2027#1` (0.089853, student)<br>3. `phi-gia-han-dao-tao-2025-2026#0` (0.071468, student) | Không |
| recursive | audience=student | 1. `muc-hoc-phi-2026-2027#0` (0.119306, student)<br>2. `muc-hoc-phi-2026-2027#1` (0.089853, student)<br>3. `phi-gia-han-dao-tao-2025-2026#0` (0.071468, student) | Không |
| heading | Không lọc | 1. `muc-hoc-phi-2026-2027#5` (0.226456, student)<br>2. `muc-hoc-phi-2026-2027#3` (0.164410, student)<br>3. `thu-hoc-phi-hk2-2025-2026#3` (0.100070, student) | Không |
| heading | audience=student | 1. `muc-hoc-phi-2026-2027#5` (0.226456, student)<br>2. `muc-hoc-phi-2026-2027#3` (0.164410, student)<br>3. `thu-hoc-phi-hk2-2025-2026#3` (0.100070, student) | Không |

**Filter chưa giúp Q5 trong các lượt chạy này:** top-3 giống hệt nhau ở cả ba
chiến lược; tài liệu cán bộ vốn không lọt top-3, tài liệu sinh viên cần tìm
cũng không lọt. Việc lọc vẫn loại đúng record `staff` khỏi tập ứng viên nhưng
không sửa được thứ hạng giả ngẫu nhiên của MD5. Không kết luận filter vô ích
nói chung hoặc coi yêu cầu “cần filter” là đã đạt.

Đã sửa Q5 một lần để tập trung vào “loại học bổng hỗ trợ học tiếp và đối tượng”
thay vì câu dẫn dài, nhưng A/B vẫn giống nhau. Lưu lần đầu tại
[`initial_queries.json`](../benchmark/cp6/initial_queries.json) và
[`initial_results.json`](../benchmark/cp6/initial_results.json); lần cuối tại
[`results.json`](../benchmark/cp6/results.json). Không thay số liệu hoặc tiếp tục
tối ưu câu chữ theo nhiễu của mock. Bước xác minh tiếp theo là backend thật,
vẫn giữ cùng câu hỏi/corpus và kiểm câu trả lời agent; người làm bài hiện chọn mock.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

### Failure case thật: Q1, chiến lược Heading

- **Câu hỏi hỏng:** Mức học phí niên chế chương trình chuẩn 3 năm/B0 dành cho sinh viên Việt Nam năm 2026-2027.
- **Kết quả:** Top-3 là `muc-hoc-phi-2026-2027#0`, `#5`, `#4`. Tất cả đúng doc_id, nhưng không chứa dòng mức thu 59 của nhóm sinh viên Việt Nam; proxy nội dung bằng 0.
- **Nguyên nhân quan sát được:** Truy xuất chọn phần mở đầu và phần sinh viên quốc tế. Mock không mã hóa ngữ nghĩa, nên không suy ra lỗi mô hình thật từ điểm này. Tiêu đề lặp lại giúp nhận diện mục nhưng không đảm bảo chunk chứa đáp án.
- **Cải thiện đề xuất:** Dùng embedding đa ngữ thật khi có điều kiện; giữ đối tượng, chương trình và đơn vị cùng dòng phí, thêm metadata nationality/program nếu tách tài liệu theo nhóm. Chấm nội dung và câu trả lời agent, không chỉ doc_id.

### Failure case bổ sung: Q5 không thể hiện tác dụng filter

Không lọc và lọc `student` đều thiếu học bổng Tiếp nối trong top-3, kể cả
sau một lần sửa câu hỏi. Vì vậy không thể khẳng định không lọc trả lời sai
đối tượng còn có lọc trả lời đúng. Cần đo lại bằng backend thật trước khi
kết luận về yêu cầu này; không đổi nhãn nguồn hoặc gán câu trả lời gold cho agent.

### Nội dung chuẩn bị demo và bài học

1. Minh họa Q1: đúng tài liệu không đồng nghĩa có đoạn trả lời được câu hỏi.
2. So sánh số chunk/độ dài: Fixed 12, Recursive 13, Heading 19 ở kích thước 500; tiêu đề lặp chiếm ngân sách.
3. Mở A/B Q5 để trình bày kết quả không cải thiện và giới hạn của mock một cách minh bạch.

Nếu làm lại, giữ thêm đơn vị bảng và phạm vi đối tượng trên mỗi chunk, sau đó
đánh giá với embedding thật. Đây là phân tích từ các lượt chạy trong repo;
chưa diễn ra demo nhóm hay thu kết quả độc lập của các thành viên khác.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
