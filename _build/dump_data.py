# -*- coding: utf-8 -*-
"""读取 13005软件工程.xlsx 全量数据并落盘 JSON。"""
import json
from openpyxl import load_workbook

SRC = r"F:\syncthing\考试\自考\13005软件工程\13005软件工程.xlsx"
OUT = r"F:\syncthing\考试\自考\13005软件工程\_build\rows.json"

wb = load_workbook(SRC, data_only=True, read_only=True)
ws = wb["Sheet1"]

rows = []
for i, row in enumerate(ws.iter_rows(min_row=1, max_col=7, values_only=True), start=1):
    def s(v):
        return str(v) if v is not None else ""
    rows.append({
        "excel_row": i,
        "chapter": s(row[0]),
        "requirement": s(row[1]),
        "summary": s(row[2]),
        "knowledge": s(row[3]),
        "desc": s(row[4]),
        "seq": row[5],
        "page": row[6],
    })
wb.close()

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)

total = len(rows)
has_k = sum(1 for r in rows if r["knowledge"].strip())
has_e = sum(1 for r in rows if r["desc"].strip())
has_page = sum(1 for r in rows if r["page"] is not None)
chapters, reqs, summaries = [], [], []
for r in rows:
    ch = r["chapter"].strip()
    if ch and ch not in chapters:
        chapters.append(ch)
    q = r["requirement"].strip()
    if q and q not in reqs:
        reqs.append(q)
    s = r["summary"].strip()
    if s and s not in summaries:
        summaries.append(s)
lens = [len(r["desc"]) for r in rows if r["desc"].strip()]
print("总行数:", total)
print("含知识点D:", has_k, "含描述E:", has_e, "含页码G:", has_page)
print("章节数:", len(chapters), chapters)
print("要求B取值:", reqs)
print("小结C数量:", len(summaries))
print("E长度: min=%d max=%d avg=%.1f" % (min(lens), max(lens), sum(lens) / len(lens)))
# 仅含 D 无 E 的行
no_e = [(r["excel_row"], r["knowledge"][:40]) for r in rows if r["knowledge"].strip() and not r["desc"].strip()]
print("有D无E行数:", len(no_e), no_e[:15])
# 含页码行但 G 列缺失情况
no_page = [(r["excel_row"], r["knowledge"][:40]) for r in rows if r["knowledge"].strip() and r["page"] is None]
print("有D无页码行数:", len(no_page), no_page[:15])
