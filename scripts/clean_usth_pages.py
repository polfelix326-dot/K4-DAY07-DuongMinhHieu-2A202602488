"""Clean the two USTH pages after running fetch_public_pages.py.

Run from the repository root. Source wording and numeric values are preserved.
"""

import csv
import re
from pathlib import Path


ROOT = Path("data/hoc-phi-usth")


def clean(name, start, end):
    path = ROOT / name
    raw = path.read_text(encoding="utf-8")
    front, body = raw.split("\n---\n", 1)
    title = body.strip().splitlines()[0]
    body = body[body.index(start):]
    body = body[:body.index(end)].strip()
    body = re.sub(r"\n[ \t\u00a0]*\n", "\n\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    body = re.sub(r"(?m)^(\d+\. .+)$", r"## \1", body)
    return path, front, title, body


path, front, title, body = clean(
    "muc-hoc-phi-2026-2027.md",
    "Trường Đại học Khoa học và Công nghệ Hà Nội thông báo quy định",
    "Chi tiết xem tại:",
)
sections = body.split("## ")
intro = sections[0]
formatted = []
for section in sections[1:]:
    heading, content = section.split("\n", 1)
    # Extract each source row from the already downloaded plain text.
    content = content[content.index("(1.000đ/năm)") + len("(1.000đ/năm)"):].strip()
    note = ""
    if "*Áp dụng" in content:
        content, note = content.split("*Áp dụng", 1)
        note = "\n\n*Áp dụng " + note.strip()
    rows = [r.strip() for r in content.split("\n\n") if r.strip()]
    merged = []
    for row in rows:
        if row.startswith("(các tín chỉ") or re.fullmatch(r"[\d.,]+", row):
            merged[-1] += "\n" + row
        else:
            merged.append(row)
    lines = []
    for row in merged:
        cells = [c.strip() for c in row.splitlines() if c.strip()]
        if cells[0].isdigit():
            cells.pop(0)  # Source serial number, not a fee.
        label = cells.pop(0)
        if cells and cells[0].startswith("(các tín chỉ"):
            label += " " + cells.pop(0)
        if "37 tín chỉ" in label or "60 tín chỉ" in label:
            annual, credit = "không nêu", cells[0]
        else:
            annual = cells[0]
            credit = cells[1] if len(cells) > 1 else "không nêu"
        lines.append(f"- {label}: niên chế {annual}; tín chỉ {credit}.")
    formatted.append("## " + heading + "\n\n"
        + "Đơn vị theo tiêu đề bảng gốc: niên chế (triệu đ/năm); tín chỉ* (1.000đ/năm).\n\n"
        + "\n".join(lines) + note)
body = intro + "\n\n".join(formatted)
front += '\nextraction_note: "Chỉ lấy nội dung HTML; chưa trích tài liệu nhúng. Giữ nguyên đơn vị tín chỉ của bảng gốc; không tự sửa đơn vị. Không nêu nghĩa là ô trống trong nguồn."'
path.write_text(front + "\n---\n\n" + title + "\n\n" + body.strip() + "\n", encoding="utf-8")

path, front, title, body = clean(
    "thu-hoc-phi-hk2-2025-2026.md",
    "USTH thông báo thu học phí học kỳ II",
    "Chia sẻ",
)
start = body.index("Đối tượng\n")
end = body.index("## 3.", start)
table = body[start:end]
rows = table.split("\n\n")[1:]
lines = []
for row in rows:
    cells = [c.strip() for c in row.splitlines() if c.strip()]
    if not cells:
        continue
    assert len(cells) == 3, cells
    lines.append(f"- {cells[0]}: sinh viên Việt Nam {cells[1]}; sinh viên quốc tế {cells[2]}.")
body = body[:start] + "Đơn vị: triệu đồng/học kỳ.\n\n" + "\n".join(lines) + "\n\n" + body[end:]
front += '\nextraction_note: "Chỉ lấy nội dung HTML; chưa trích tài liệu nhúng. Thông báo áp dụng học kỳ II năm học 2025-2026, không áp dụng thay cho năm 2026-2027."'
front += '\nfee_basis: "Quyết định số 563/QĐ-ĐHKHCN ngày 01/07/2025"'
path.write_text(front + "\n---\n\n" + title + "\n\n" + body.strip() + "\n", encoding="utf-8")

manifest = ROOT / "sources.csv"
with manifest.open(encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    records = list(reader)
for record in records:
    record["file_path"] = record["file_path"].replace("\\", "/")
with manifest.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(records)
print("Cleaned two USTH documents; normalized manifest paths.")
