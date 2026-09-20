"""Populate CP5 report tables from the actual baseline and shared queries."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
baseline = json.loads((root / 'benchmark/baseline_cp5.json').read_text(encoding='utf-8'))
queries = json.loads((root / 'benchmark/usth_queries.json').read_text(encoding='utf-8'))
notes = {
    'fixed_size': 'Giới hạn 500 ký tự, overlap 50; có thể cắt giữa câu hoặc dòng mức phí.',
    'by_sentences': 'Giữ dấu câu; tối đa 3 câu. Danh sách/bảng ít dấu kết câu có thể tạo chunk dài hơn 500.',
    'recursive': 'Ưu tiên đoạn/dòng và gom mảnh nhỏ; có thể mất tiêu đề ở chunk sau, chưa lặp lại đơn vị bảng.',
}
rows = []
for doc_id, strategies in baseline['documents'].items():
    for name, stats in strategies.items():
        rows.append(f"| `{doc_id}` | `{name}` | {stats['count']} | {stats['avg_length']:.2f} | {notes[name]} |")
table = '''Đã chạy `ChunkingStrategyComparator().compare(body, chunk_size=500)` trên
3 tài liệu bên dưới. `body` đã bỏ YAML frontmatter; giữ tiêu đề Markdown.
FixedSize dùng overlap 50, Sentence dùng 3 câu/chunk. Các số liệu và toàn bộ
chunk được lưu tại [`benchmark/baseline_cp5.json`](../benchmark/baseline_cp5.json).
Nhận xét cột cuối mô tả cấu trúc đoạn; chưa kết luận chất lượng retrieval.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình (ký tự) | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
''' + '\n'.join(rows) + '\n\n'
path = root / 'report/REPORT_NHOM.md'
text = path.read_text(encoding='utf-8')
start = text.index('Chạy `ChunkingStrategyComparator().compare()`')
end = text.index('### Chiến lược của từng thành viên', start)
text = text[:start] + table + text[end:]

start = text.index('**Thành viên 1 — [Tên]**')
end = text.index('**Thành viên 2 — [Tên]**', start)
text = text[:start] + '''**Chiến lược cá nhân đang chạy trong repo — chưa điền tên thành viên**
- **Loại chiến lược:** Heading, `chunk_size=500`.
- **Lý do:** Thông báo USTH phân mục mức phí, thời hạn và thanh toán. Giữ tiêu đề của mục cùng tiêu đề tài liệu trên từng chunk giúp nhận diện nội dung và năm học.
- **Cách xử lý:** Tách trước heading Markdown; section dài được chia bằng RecursiveChunker với ngân sách còn lại sau tiêu đề. Mỗi mảnh con được gắn lại chuỗi heading cha/con. Không nhận dòng `#` trong fenced code block là heading.
- **Giới hạn:** Không tự lặp lại đơn vị/mô tả cột nếu chúng nằm trong thân bảng; heading quá dài so với ngân sách sẽ báo lỗi để tăng chunk_size. Metadata vẫn giữ trên mọi chunk.
- **Mã nguồn:** [`src/heading_chunking.py`](../src/heading_chunking.py).
- **CP5:** `python bench.py` chạy thành công: 5 tài liệu, 19 chunk, 5 câu hỏi, top-3 mỗi câu. Output: [`ket_qua_benchmark.txt`](../ket_qua_benchmark.txt).
- **Cấu hình chung:** MockEmbedder, top_k=3, cùng corpus và `benchmark/usth_queries.json`. Chỉ đổi `DEFAULT_STRATEGY` trong `bench.py` hoặc `--strategy`; chưa dùng API embedding, không phát sinh phí API.
- **Phân công còn chờ nhóm:** Hai thành viên khác cần nhận chiến lược khác nhau (gợi ý FixedSize và Recursive), tự chạy và ghi kết quả của mình. Chưa giả định hoặc ghi thay kết quả của họ.

''' + text[end:]
start = text.index('| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |')
end = text.index('### Tổng hợp chất lượng truy xuất của nhóm', start)
rows = []
for q in queries:
    filt = json.dumps(q['metadata_filter'], ensure_ascii=False)
    rows.append(f"| {q['id']} | {q['question']}<br>Filter: `{filt}` | {q['gold_answer']} | `{q['gold_doc_id']}` — {q['gold_section']} (mục nguồn; chunk_id cụ thể xem output) |")
table = '''| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
''' + '\n'.join(rows) + '''

Q1 tra số liệu; Q2 hỏi thời hạn và hậu quả; Q3 hỏi quy trình; Q4 liệt kê trường
hợp áp dụng; Q5 hỏi điều kiện học bổng. Q5 không nói rõ danh tính người hỏi;
ngữ cảnh ứng dụng là người tốt nghiệp USTH học tiếp, không xét tư cách cán bộ
VAST. Filter `audience=student` loại mục học bổng cán bộ khỏi tập ứng viên.
CP5 đã chạy tìm kiếm có lọc bằng mock; chưa chạy A/B với câu trả lời của agent,
chưa chứng minh điều kiện “phải có filter mới trả lời đúng”. Không dùng điểm
mock để kết luận chiến lược nào hiểu ngữ nghĩa tốt hơn.

'''
text = text[:start] + table + text[end:]
path.write_text(text, encoding='utf-8')
print('Populated 9 baseline rows and 5 benchmark queries in group report.')
