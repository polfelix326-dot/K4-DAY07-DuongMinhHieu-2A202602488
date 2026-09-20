# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Dương Minh Hiếu
**Nhóm:** G02
**Ngày:** 2026-09-19

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
Hai vector có hướng gần nhau, nên cosine gần 1. Với embedding có khả năng biểu diễn ngữ nghĩa, điều này thường cho thấy hai đoạn có nội dung tương đồng; không bảo đảm mọi chi tiết đều giống nhau. MockEmbedder trong lab không có khả năng hiểu nghĩa.

**Ví dụ có độ tương tự CAO:**
- Câu A: Tôi muốn xin lùi hạn đóng học phí.
- Câu B: Em cần được phép thanh toán tiền học muộn hơn.
- Tại sao tương đồng: Khác cách diễn đạt nhưng cùng mong muốn được gia hạn thanh toán. Đây là dự đoán ngữ nghĩa, chưa phải điểm embedding đã đo.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên thanh toán học phí bằng mã QR.
- Câu B: Sao Mộc là hành tinh lớn nhất trong Hệ Mặt Trời.
- Tại sao khác: Một câu nói về thanh toán học phí, câu kia nói về thiên văn; dự đoán độ tương đồng ngữ nghĩa thấp.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
Cosine so sánh hướng của vector, không bị ảnh hưởng bởi việc nhân độ lớn của vector với một số dương; Euclid chịu ảnh hưởng cả hướng và độ lớn. Với vector đã chuẩn hóa có độ dài 1, khoảng cách Euclid bình phương bằng `2 - 2*cosine`, nên hai cách cho thứ tự tương đồng tương đương; cosine không phải lúc nào cũng tốt hơn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
`ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23` chunk.

Đã kiểm chứng bằng `FixedSizeChunker` có sẵn trên chuỗi `'a' * 10000`: kết quả thực tế **23**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
`ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25` chunk; chạy thực tế cho kết quả **25**, tăng 2 chunk. Overlap lớn hơn giúp giữ ngữ cảnh tại ranh giới đoạn, đổi lại tăng dữ liệu lặp, số lần embedding và chi phí lưu trữ/truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Dùng `re.split(r"(?<=[.!?])\s+", text)` để tách sau dấu câu, giữ dấu câu nhờ lookbehind. Strip từng câu, bỏ đoạn rỗng, gom tối đa `max_sentences_per_chunk` câu; text rỗng hoặc chỉ khoảng trắng trả `[]`.

Giới hạn: chưa hiểu chữ viết tắt như `TS.`, `v.v.` nên có thể tách sai khi sau dấu chấm là khoảng trắng. Số thập phân thông thường như `3.14` không bị tách vì không có khoảng trắng; số bị ngắt dòng hoặc có khoảng trắng như `3. 14` vẫn có thể bị tách sai. Đây là quy tắc dấu câu đơn giản, chưa phải bộ phân tích câu tiếng Việt đầy đủ.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Thử các separator theo thứ tự đoạn, dòng, câu, từ, ký tự; mảnh quá dài được xử lý đệ quy với separator còn lại. Giữ separator ở cuối mảnh để không mất dấu câu/khoảng trắng, rồi gom các mảnh liền kề khi tổng độ dài không vượt `chunk_size`.

Ba trường hợp dừng: text rỗng trả `[]`; text không vượt kích thước trả `[text]`; hết separator hoặc gặp `""` thì cắt theo số ký tự. Kích thước không dương bị từ chối bằng `ValueError`. Cách này bảo toàn nội dung, nhưng khi buộc phải cắt theo ký tự vẫn có thể cắt giữa từ.

**`compute_similarity`:** Tái sử dụng `_dot`, chia tích vô hướng cho tích hai độ dài vector; trả `0.0` nếu một vector có độ dài 0 (bao gồm vector rỗng). Đầu vào được giả định là hai vector cùng số chiều.

**`ChunkingStrategyComparator.compare`:** Trả đúng các key `fixed_size`, `by_sentences`, `recursive`, mỗi key có `count`, `avg_length`, `chunks`. Text rỗng cho count và độ dài trung bình bằng 0. FixedSize dùng overlap 50, giảm xuống `chunk_size - 1` nếu kích thước quá nhỏ; Sentence dùng mặc định 3 câu, nên không bị giới hạn theo số ký tự như hai chiến lược còn lại.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Store chỉ dùng danh sách trong bộ nhớ, không import hoặc rẽ nhánh ChromaDB. Mỗi Document tạo đúng một record; `_make_record` sao chép sâu metadata, giữ `doc_id` có sẵn hoặc suy ra từ phần trước `#` trong id của chunk, rồi tính embedding. `_search_records` tính dot product với embedding câu hỏi, sắp xếp giảm dần và lấy top-k; kết quả không chứa vector embedding và trả bản sao metadata. Dot product tương đương cosine khi embedder trả vector chuẩn hóa; store không tự chunk hoặc chuẩn hóa lại vector.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
Lọc trước theo tất cả cặp key/value của metadata_filter, rồi gọi chung `_search_records`; tránh để tài liệu sai đối tượng chiếm hết top-k. Khi không có bộ lọc, dùng cùng đường tìm kiếm với `search`. Xóa tất cả record có `metadata['doc_id']` khớp tài liệu gốc và so sánh kích thước trước/sau để trả True hoặc False; `top_k <= 0` hoặc tập ứng viên rỗng trả danh sách rỗng.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
Truy xuất top-k, đánh số từng đoạn `[1]`, `[2]` kèm URL/đường dẫn nguồn, doc_id và id của chunk, sau đó đưa cả ngữ cảnh lẫn câu hỏi vào prompt gọi `llm_fn`. Prompt yêu cầu chỉ dùng thông tin được cung cấp, trích dẫn số nguồn và nói rõ nếu không đủ thông tin; đây là chỉ dẫn cho LLM, không phải bảo đảm tuyệt đối chống bịa. Khi không có kết quả truy xuất, trả thông báo không tìm thấy thông tin ngay và không gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

**Checkpoint 3 — đã chạy trên Python 3.11.9:**

```text
python -m pytest tests/ -k "Chunker or Similarity or Compare" -v
collected 42 items / 19 deselected / 23 selected
23 passed, 19 deselected, 1 warning in 0.10s
```

Warning do pytest không ghi được thư mục cache (`WinError 5`), không có test thất bại.
23 test được chọn gồm 7 FixedSize, 4 Sentence, 4 Recursive, 4 Similarity,
3 Compare và 1 kiểm tra tồn tại các lớp chunker. Đây là kết quả CP3,
chưa phải kết quả toàn bộ 42 test. Kết quả toàn bộ ở CP4 được ghi dưới đây.

### Checkpoint 4 — toàn bộ bộ kiểm thử và demo

```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0 -- D:\K4-DAY07-DuongMinhHieu-2A202602488\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\K4-DAY07-DuongMinhHieu-2A202602488
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== warnings summary ===============================
.venv\Lib\site-packages\_pytest\cacheprovider.py:469
  D:\K4-DAY07-DuongMinhHieu-2A202602488\.venv\Lib\site-packages\_pytest\cacheprovider.py:469: PytestCacheWarning: could not create cache path D:\K4-DAY07-DuongMinhHieu-2A202602488\.pytest_cache\v\cache\nodeids: [WinError 5] Access is denied: 'D:\\K4-DAY07-DuongMinhHieu-2A202602488\\.pytest_cache\\v\\cache'
    config.cache.set("cache/nodeids", sorted(self.cached_nodeids))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 42 passed, 1 warning in 0.09s ========================
```

Đã chạy `python main.py "Chunking là gì?"`: mã thoát 0, nạp 5 tài liệu,
lưu 5 record, trả top-3 và gọi agent đến cuối. File mẫu
`data/customer_support_playbook.txt` bị bỏ qua vì không có trong repo, đúng dự kiến.
Demo dùng mock embedding và `demo_llm` chỉ in một phần prompt; chưa phải đánh giá
ngữ nghĩa, benchmark USTH hoặc kiểm chứng chất lượng trích dẫn của LLM thật.

Đã kiểm tra thêm: lọc trước top-k khi tài liệu sai đối tượng có điểm cao hơn;
metadata đầu vào và kết quả tìm kiếm không sửa được dữ liệu trong store;
xóa nhiều chunk của cùng doc_id; prompt có số nguồn và id chunk; store rỗng
không gọi LLM. Các kiểm tra này đều thành công, không tính vào số 42 test của đề.

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Học phí niên chế sinh viên Việt Nam năm 2026-2027 | Học phí tín chỉ cho sinh viên quốc tế năm 2026-2027 | cao | chưa đo với embedding thật | chưa xác minh |
| 2 | Hạn cuối đóng học phí học kỳ II 2025-2026 | Thời gian gia hạn đào tạo 2025-2026 | thấp | mock không biểu diễn ngữ nghĩa | chưa xác minh |
| 3 | Cách thanh toán học phí qua ERP | Học bổng Tiếp nối cho sinh viên tốt nghiệp USTH | thấp | mock không biểu diễn ngữ nghĩa | chưa xác minh |
| 4 | Mức thu theo tín chỉ áp dụng khi đăng ký học lại | Mức thu theo tín chỉ áp dụng cho sinh viên quốc tế | cao | mock chỉ đo MD5, không ngữ nghĩa | chưa xác minh |
| 5 | Học bổng Tiếp nối cho người tốt nghiệp USTH | Học bổng Tăng cường năng lực cho cán bộ VAST | cao | không có backend thật nên không suy ra ý nghĩa | chưa xác minh |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Những cặp câu cùng chủ đề nhưng khác đối tượng hoặc khác đơn vị có thể trông gần nhau theo từ khóa, nhưng mock embedding không có khả năng hiểu sắc thái ngữ nghĩa. Vì vậy, khi chạy benchmark bằng MD5, kết quả top-k bị chi phối bởi trùng ký tự chứ không phải bởi ý nghĩa thực sự của câu hỏi.*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

**Chiến lược cá nhân trong repo:** Heading. Kết quả chạy CP6 lưu tại
[`ket_qua_benchmark.txt`](../ket_qua_benchmark.txt), bản cấu trúc tại
[`benchmark/cp6/results.json`](../benchmark/cp6/results.json).
Chạy lại: `python benchmark_cp6.py --backend mock`.

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

Heading tạo **19 chunk**, trung bình **297.11 ký tự/chunk**.

| Câu | Câu hỏi | Top-3: chunk_id, score, audience | Đúng tài liệu? | Đủ bằng chứng? | Proxy /2 | Agent |
|---|---|---|---|---|---|---|
| Q1 | Năm học 2026-2027, học phí theo niên chế của chương trình chuẩn 3 năm và B0 dành cho sinh viên Việt Nam là bao nhiêu? | 1. `muc-hoc-phi-2026-2027#0` (0.261108, student)<br>2. `muc-hoc-phi-2026-2027#5` (0.095389, student)<br>3. `muc-hoc-phi-2026-2027#4` (0.060324, student) | Có | Không | 0 | Bản trích nguồn; chưa chấm câu trả lời LLM |
| Q2 | Hạn cuối đóng học phí học kỳ II năm học 2025-2026 là ngày nào, và đóng không đúng hạn có hậu quả gì? | 1. `phi-gia-han-dao-tao-2025-2026#0` (0.147876, student)<br>2. `thu-hoc-phi-hk2-2025-2026#6` (0.073625, student)<br>3. `thu-hoc-phi-hk2-2025-2026#5` (0.026680, student) | Có | Có | 1 | Bản trích nguồn; chưa chấm câu trả lời LLM |
| Q3 | Theo thông báo thu học phí học kỳ II năm học 2025-2026, đóng học phí qua đâu và khi nào được xác nhận đã thanh toán? | 1. `phi-gia-han-dao-tao-2025-2026#0` (0.147874, student)<br>2. `hoc-bong-tiep-noi-sinh-vien#0` (0.120204, student)<br>3. `hoc-bong-tang-cuong-nang-luc-can-bo#0` (0.118235, staff) | Không | Không | 0 | Bản trích nguồn; chưa chấm câu trả lời LLM |
| Q4 | Theo thông báo mức học phí năm học 2026-2027, mức thu theo tín chỉ được áp dụng trong những trường hợp nào? | 1. `muc-hoc-phi-2026-2027#5` (0.322824, student)<br>2. `muc-hoc-phi-2026-2027#6` (0.067856, student)<br>3. `muc-hoc-phi-2026-2027#0` (0.043796, student) | Có | Có | 1 | Bản trích nguồn; chưa chấm câu trả lời LLM |
| Q5 | Khi theo học thạc sĩ hoặc tiến sĩ tại USTH, có loại học bổng nào hỗ trợ học tiếp và dành cho đối tượng nào? | 1. `muc-hoc-phi-2026-2027#5` (0.226456, student)<br>2. `muc-hoc-phi-2026-2027#3` (0.164410, student)<br>3. `thu-hoc-phi-hk2-2025-2026#3` (0.100070, student) | Không | Không | 0 | Bản trích nguồn; chưa chấm câu trả lời LLM |

Đúng doc_id trong top-3: **3/5**. Đủ chuỗi bằng chứng từ nguồn gold: **2/5**. Tổng proxy: **2/10**, chưa phải điểm chính thức.

**Q1 — trường hợp lỗi:** Cả ba kết quả đều thuộc file mức học phí 2026-2027,
nhưng là phần mở đầu hoặc mức phí sinh viên quốc tế; không có dòng chương
trình chuẩn 3 năm/B0 của sinh viên Việt Nam với niên chế 59. Chấm chỉ theo
doc_id sẽ coi là thành công; kiểm nội dung cho 0. Cần embedding thật và giữ
đối tượng, chương trình, đơn vị cùng dòng mức phí khi chunk; không sửa điểm mock.

**Q5 — A/B:** Bật/tắt audience cho top-3 giống nhau, cả hai đều thiếu mục học
bổng Tiếp nối. Đã rút gọn câu hỏi để tập trung vào điều kiện học bổng rồi chạy
lại; kết quả vẫn chưa chứng minh bộ lọc cần thiết. Giữ kết quả thất bại để
báo cáo, không thử hàng loạt cách diễn đạt chỉ nhằm tìm một mã băm thuận lợi.

**Điều học được từ so sánh trong repo:** Heading giữ chuỗi tiêu đề nhưng có
thể lấy đúng tài liệu và sai mục; cần đọc nội dung từng chunk thay vì chỉ
nhìn doc_id. Chưa có kết quả do thành viên khác tự chạy hoặc buổi demo thực tế
để ghi nhận trải nghiệm học hỏi giữa các thành viên.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 |
| **Tổng phần cá nhân** | **58 / 60** |
