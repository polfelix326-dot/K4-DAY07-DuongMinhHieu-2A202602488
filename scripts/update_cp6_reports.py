"""Render CP6 measurements into the existing lab reports without inventing team results."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/'benchmark/cp6/results.json').read_text(encoding='utf-8'))
queries = json.loads((ROOT/'benchmark/usth_queries.json').read_text(encoding='utf-8'))
strategies = data['strategies']


def cell(text):
    return str(text).replace('|', '\\|').replace('\n', ' ')


def top3(value):
    return '<br>'.join(f"{i}. `{r['id']}` ({r['score']:.6f}, {r['metadata']['audience']})" for i,r in enumerate(value['results'],1))


def replace_between(text, start, end, content):
    a=text.index(start); b=text.index(end,a)
    return text[:a]+content+text[b:]


disclaimer = '''Backend: **MockEmbedder (MD5), không có ngữ nghĩa**, theo lựa chọn của người làm bài.
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

'''

heading=strategies['heading']
personal='''## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

**Chiến lược cá nhân trong repo:** Heading. Kết quả chạy CP6 lưu tại
[`ket_qua_benchmark.txt`](../ket_qua_benchmark.txt), bản cấu trúc tại
[`benchmark/cp6/results.json`](../benchmark/cp6/results.json).
Chạy lại: `python benchmark_cp6.py --backend mock`.

'''+disclaimer+f"Heading tạo **{heading['chunk_count']} chunk**, trung bình **{heading['avg_length']:.2f} ký tự/chunk**.\n\n"
personal+='| Câu | Câu hỏi | Top-3: chunk_id, score, audience | Đúng tài liệu? | Đủ bằng chứng? | Proxy /2 | Agent |\n|---|---|---|---|---|---|---|\n'
for q in queries:
    value=heading['evaluations'][q['id']]
    personal+=f"| {q['id']} | {cell(q['question'])} | {top3(value)} | {'Có' if value['document_hit'] else 'Không'} | {'Có' if value['evidence_hit'] else 'Không'} | {value['retrieval_proxy_score']} | Bản trích nguồn; chưa chấm câu trả lời LLM |\n"
personal+=f"\nĐúng doc_id trong top-3: **{heading['document_hits']}/5**. Đủ chuỗi bằng chứng từ nguồn gold: **{heading['evidence_hits']}/5**. Tổng proxy: **{heading['retrieval_proxy_total']}/10**, chưa phải điểm chính thức.\n\n"
personal+='''**Q1 — trường hợp lỗi:** Cả ba kết quả đều thuộc file mức học phí 2026-2027,
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

'''
p=ROOT/'report/REPORT_CANHAN.md'
text=p.read_text(encoding='utf-8')
text=replace_between(text,'## 5. Kết quả truy xuất','## Tự Đánh Giá',personal)
p.write_text(text,encoding='utf-8')

p=ROOT/'report/REPORT_NHOM.md'
text=p.read_text(encoding='utf-8')
comparison='''### So Sánh Giữa Các Thành Viên

**Hiện đây là phép so sánh ba cấu hình chạy trong cùng repo**, chưa phải kết
quả do ba thành viên độc lập nộp. Giữ trống tên/phân công cho tới khi nhóm xác nhận;
không gán kết quả giả cho thành viên khác.

'''+disclaimer
comparison+='| Cấu hình (chưa gán thành viên) | Số chunk | TB ký tự | Đúng doc /5 | Đủ bằng chứng /5 | Proxy /10 | Nhận xét cấu trúc |\n|---|---|---|---|---|---|---|\n'
notes={'fixed':'Overlap giữ vùng biên nhưng có thể cắt dòng mức phí và từ.',
       'recursive':'Giữ ranh giới đoạn/dòng; không lặp tiêu đề ở từng chunk.',
       'heading':'Lặp tiêu đề cha/con; nhiều chunk hơn vì tiêu đề chiếm ngân sách; đơn vị bảng trong thân vẫn có thể bị tách.'}
for name,d in strategies.items():
    comparison+=f"| {name} | {d['chunk_count']} | {d['avg_length']:.2f} | {d['document_hits']} | {d['evidence_hits']} | {d['retrieval_proxy_total']} | {notes[name]} |\n"
comparison+='''
**Chưa chọn chiến lược thắng về ngữ nghĩa.** Với corpus quy định có nhiều mục,
Heading có lợi thế giữ tiêu đề và năm học, nhưng làm tăng số đoạn; cần thêm
đơn vị bảng và đối tượng vào ngữ cảnh từng dòng phí. Kết quả mock không đủ
để kết luận lợi thế retrieval. Failure case Q1 được phân tích tại mục 4.

Output đầy đủ: [fixed](../benchmark/cp6/fixed.txt),
[recursive](../benchmark/cp6/recursive.txt), [heading](../benchmark/cp6/heading.txt).

---

'''
text=replace_between(text,'### So Sánh Giữa Các Thành Viên','## 3. Câu hỏi',comparison)
start=text.index('Bộ 5 câu hỏi dự thảo, đáp án')
end=text.index('Hai mục học bổng',start)
text=text[:start]+'''Bộ 5 câu hỏi và đáp án nguồn lưu tại
[`benchmark/usth_queries.json`](../benchmark/usth_queries.json); cả ba chiến lược
đã chạy cùng bộ này. Nhóm vẫn cần xác nhận bộ dùng chung.
Q5 đã chạy A/B bằng mock, nhưng **chưa đạt điều kiện cần filter mới trả lời đúng**.

'''+text[end:]
start=text.index('| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |')
end=text.index('### Tổng hợp chất lượng truy xuất của nhóm',start)
qt='| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |\n|---|---|---|---|\n'
for q in queries:
    qt+=f"| {q['id']} | {cell(q['question'])}<br>Filter: `{json.dumps(q['metadata_filter'],ensure_ascii=False)}` | {cell(q['gold_answer'])} | `{q['gold_doc_id']}` — {cell(q['gold_section'])} |\n"
qt+='\nQ5 sử dụng ngữ cảnh người hỏi là người tốt nghiệp USTH học tiếp, không xét tư cách cán bộ VAST. Câu hỏi không nói rõ đối tượng; bộ lọc truyền ngữ cảnh đó.\n\n'
text=text[:start]+qt+text[end:]
quality='''### Tổng hợp chất lượng truy xuất của nhóm

| Câu | Fixed: doc/evidence | Recursive: doc/evidence | Heading: doc/evidence | Kết luận |
|---|---|---|---|---|
'''
for q in queries:
    vals=[]
    for d in strategies.values():
        e=d['evaluations'][q['id']]
        vals.append(f"{int(e['document_hit'])}/{int(e['evidence_hit'])}")
    quality+=f"| {q['id']} | {' | '.join(vals)} | Chỉ số chạy mock; chưa chấm LLM |\n"
quality+='''
`doc/evidence`: 1 là có, 0 là không; kiểm evidence chỉ nhận nội dung từ đúng
file gold để tránh lấy thông tin giống nhau từ thông báo khác.

### A/B Q5 — có và không có bộ lọc trên ba chiến lược

| Chiến lược | Filter | Top-3: chunk_id, score, audience | Đủ bằng chứng? |
|---|---|---|---|
'''
for name,d in strategies.items():
    for key,label in [('without_filter','Không lọc'),('with_filter','audience=student')]:
        value=d['ab_q5'][key]
        quality+=f"| {name} | {label} | {top3(value)} | {'Có' if value['evidence_hit'] else 'Không'} |\n"
quality+='''
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

'''
text=replace_between(text,'### Tổng hợp chất lượng truy xuất của nhóm','## 4. Thuyết trình',quality)
failure='''## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

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

'''
text=replace_between(text,'## 4. Thuyết trình','## Tự Đánh Giá',failure)
text=text.replace('Việc có hai audience chưa chứng minh Q5 cần bộ lọc: còn phải chạy A/B và\nkiểm tra câu trả lời thực tế ở Giai đoạn 2. Chưa có kết quả retrieval để chấm điểm.',
                  'Đã có A/B CP6 bằng mock ở mục 3; Q5 vẫn chưa chứng minh cần bộ lọc. Điểm rubric còn chờ đánh giá câu trả lời agent.')
p.write_text(text,encoding='utf-8')
print('Updated personal section 5 and group sections 2-4 using measured CP6 results.')
