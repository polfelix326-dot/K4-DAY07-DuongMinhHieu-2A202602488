"""Clean the extension notice and refresh section 1 of the group report."""
import csv
from pathlib import Path
from check_corpus import read_document

root = Path('data/hoc-phi-usth')
path = root / 'phi-gia-han-dao-tao-2025-2026.md'
text = path.read_text(encoding='utf-8')
if 'Chia sẻ' in text:
    front, rest = text.split('\n---\n', 1)
    body = rest[rest.index('USTH thông báo thu phí'):].split('Chia sẻ')[0].strip()
    body = body.replace('(Danh sách sinh viên trong thông báo đính kèm bên dưới)\n\n', '')
    body = body.replace('ERP:https', 'ERP: https')
    front += '\nextraction_note: "Chỉ lấy HTML công khai; không tải danh sách sinh viên đính kèm. HTML không nêu số tiền phí gia hạn."'
    path.write_text(front + '\n---\n\n# Phí gia hạn đào tạo USTH năm học 2025-2026\n\n' + body + '\n', encoding='utf-8')

manifest = root / 'sources.csv'
with manifest.open(encoding='utf-8', newline='') as f:
    reader = csv.DictReader(f)
    fields, rows = reader.fieldnames, list(reader)
for row in rows:
    row['file_path'] = row['file_path'].replace('\\', '/')
with manifest.open('w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

inventory = []
for index, path in enumerate(sorted(root.glob('*.md')), 1):
    meta, body = read_document(path)
    values = '; '.join(f'{key}={meta[key]}' for key in ('audience', 'category', 'language', 'academic_year', 'source_section', 'eligibility_group', 'temporal_scope') if key in meta)
    inventory.append(f"| {index} | [{meta['title']}](../{path.as_posix()}) | [USTH]({meta['source_url']}) | {meta['retrieved_at']} / `{meta['document_version']}` | {len(body)} | `{values}` |")

section = '''## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

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
''' + '\n'.join(inventory) + '''

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
Việc có hai audience chưa chứng minh Q5 cần bộ lọc: còn phải chạy A/B và
kiểm tra câu trả lời thực tế ở Giai đoạn 2. Chưa có kết quả retrieval để chấm điểm.

---

'''
report = Path('report/REPORT_NHOM.md')
text = report.read_text(encoding='utf-8')
start = text.index('## 1. Lựa chọn tài liệu')
end = text.index('## 2. Thiết kế chiến lược', start)
report.write_text(text[:start] + section + text[end:], encoding='utf-8')
print('Updated Data Inventory and Metadata Schema from 5 documents.')
