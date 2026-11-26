#!/usr/bin/env python3
"""
Generate styled Maharashtra Colleges Excel Workbook (.xlsx)
Includes:
- Summary dashboard tab with live Excel formulas
- All Colleges master tab (frozen header, auto-filter, clickable links)
- Category-specific tabs
"""

import json
from collections import Counter
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IN_JSON = DATA_DIR / "maharashtra_colleges.json"
OUT_XLSX = DATA_DIR / "maharashtra_colleges.xlsx"

COLUMNS = [
    ("sr_no", "Sr. No.", 9),
    ("name", "Name of the College", 44),
    ("principal_name", "Principal Name", 26),
    ("college_phone", "Phone Number of the College", 22),
    ("principal_phone", "Phone Number of the Principal", 22),
    ("faculty_mobile", "Faculty / Personal Mobile (+91)", 24),
    ("instagram_id", "Instagram ID", 22),
    ("district", "District", 20),
    ("city", "City / Area", 20),
    ("category", "Category / Stream", 30),
    ("affiliation", "University / Board Affiliation", 34),
    ("management_type", "Management Type", 24),
    ("email", "Official Email ID", 30),
    ("website", "Official Website", 32),
    ("address", "Full Address & Pincode", 44),
    ("aishe_code", "AISHE / DTE Code", 16),
    ("verification_source", "Data Source / Verification", 30),
]

CATEGORY_TABS = [
    ("Degree Colleges", "Degree College (Arts / Science / Commerce)"),
    ("Engineering & Tech", "Engineering, Polytechnic & Architecture"),
    ("Medical & Pharmacy", "Medical, Dental & Pharmacy"),
    ("Management & Law", "Management & Law"),
    ("Junior Colleges", "Junior College"),
    ("Universities & Others", None),
]

HEADER_FILL = PatternFill("solid", fgColor="1E3A5F")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
ZEBRA_FILL = PatternFill("solid", fgColor="F4F7FA")
WHITE_FILL = PatternFill("solid", fgColor="FFFFFF")
LINK_FONT = Font(name="Calibri", size=10, color="0563C1", underline="single")
BODY_FONT = Font(name="Calibri", size=10, color="1F2937")
BOLD_FONT = Font(name="Calibri", size=10, bold=True, color="1F2937")
TITLE_FONT = Font(name="Calibri", size=16, bold=True, color="1E3A5F")
SUBTITLE_FONT = Font(name="Calibri", size=11, bold=True, color="334155")
THIN_BORDER = Border(
    left=Side(style="thin", color="E2E8F0"),
    right=Side(style="thin", color="E2E8F0"),
    top=Side(style="thin", color="E2E8F0"),
    bottom=Side(style="thin", color="E2E8F0"),
)


def populate_college_sheet(ws, rows: list[dict], reindex: bool = False) -> None:
    ws.freeze_panes = "A2"
    ws.views.sheetView[0].showGridLines = True

    # Header
    for col_idx, (_, label, width) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=label)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
        ws.column_dimensions[get_column_letter(col_idx)].width = width
    ws.row_dimensions[1].height = 28

    # Rows
    for row_offset, rec in enumerate(rows, start=2):
        fill = ZEBRA_FILL if row_offset % 2 == 0 else WHITE_FILL
        for col_idx, (key, _, _) in enumerate(COLUMNS, start=1):
            val = (row_offset - 1) if (reindex and key == "sr_no") else rec.get(key, "")
            cell = ws.cell(row=row_offset, column=col_idx, value=val)
            cell.fill = fill
            cell.font = BODY_FONT
            cell.border = THIN_BORDER
            cell.alignment = Alignment(
                horizontal="center" if key in {"sr_no", "aishe_code"} else "left",
                vertical="center",
                wrap_text=True,
            )

            # Clickable hyperlinks
            if key == "website" and val:
                cell.hyperlink = val
                cell.font = LINK_FONT
            elif key == "email" and val and "@" in str(val):
                cell.hyperlink = f"mailto:{val}"
                cell.font = LINK_FONT
            elif key == "instagram_id" and val:
                handle = str(val).lstrip("@").strip()
                if handle:
                    cell.hyperlink = f"https://www.instagram.com/{handle}/"
                    cell.font = LINK_FONT

    if rows:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(COLUMNS))}{len(rows) + 1}"


def build_summary_sheet(ws, records: list[dict]) -> None:
    ws.views.sheetView[0].showGridLines = True
    ws["A1"] = "Maharashtra Colleges & Institutions Database — Summary"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = "Compiled from AISHE, University Affiliation Records, DTE Maharashtra & Verified College Websites"
    ws["A2"].font = Font(name="Calibri", size=10, italic=True, color="64748B")

    total_rows = len(records) + 1  # last row index in 'All Colleges'
    kpis = [
        ("Total Institutions", f"=COUNTA('All Colleges'!B2:B{total_rows})"),
        ("With Principal Name", f"=COUNTIF('All Colleges'!C2:C{total_rows}, \"?*\")"),
        ("With College Phone", f"=COUNTIF('All Colleges'!D2:D{total_rows}, \"?*\")"),
        ("With Principal Phone", f"=COUNTIF('All Colleges'!E2:E{total_rows}, \"?*\")"),
        ("With +91 Personal/Faculty Mobile", f"=COUNTIF('All Colleges'!F2:F{total_rows}, \"?*\")"),
        ("With Instagram ID", f"=COUNTIF('All Colleges'!G2:G{total_rows}, \"?*\")"),
        ("With Official Website", f"=COUNTIF('All Colleges'!N2:N{total_rows}, \"?*\")"),
        ("With Official Email", f"=COUNTIF('All Colleges'!M2:M{total_rows}, \"?*\")"),
    ]

    ws["A4"] = "Database Coverage Metrics"
    ws["A4"].font = SUBTITLE_FONT
    for idx, (label, formula) in enumerate(kpis, start=5):
        c1 = ws.cell(row=idx, column=1, value=label)
        c2 = ws.cell(row=idx, column=2, value=formula)
        c1.font = BOLD_FONT
        c2.font = BODY_FONT
        c2.number_format = "#,##0"
        c1.fill = ZEBRA_FILL if idx % 2 == 0 else WHITE_FILL
        c2.fill = ZEBRA_FILL if idx % 2 == 0 else WHITE_FILL
        c1.border = THIN_BORDER
        c2.border = THIN_BORDER

    # Category breakdown
    ws["D4"] = "By Category / Stream"
    ws["D4"].font = SUBTITLE_FONT
    for col_i, title in [(4, "Category / Stream"), (5, "Count")]:
        c = ws.cell(row=5, column=col_i, value=title)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.border = THIN_BORDER

    cats = sorted(Counter(r["category"] for r in records).items(), key=lambda x: -x[1])
    for offset, (cat_name, _) in enumerate(cats, start=6):
        c1 = ws.cell(row=offset, column=4, value=cat_name)
        c2 = ws.cell(row=offset, column=5, value=f"=COUNTIF('All Colleges'!J2:J{total_rows}, D{offset})")
        c1.font = BODY_FONT
        c2.font = BODY_FONT
        c2.number_format = "#,##0"
        c1.border = THIN_BORDER
        c2.border = THIN_BORDER

    # District breakdown
    ws["G4"] = "By District (All Maharashtra)"
    ws["G4"].font = SUBTITLE_FONT
    for col_i, title in [(7, "District"), (8, "Count")]:
        c = ws.cell(row=5, column=col_i, value=title)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.border = THIN_BORDER

    dists = sorted(Counter(r["district"] for r in records if r["district"]).items(), key=lambda x: -x[1])
    for offset, (dist_name, _) in enumerate(dists, start=6):
        c1 = ws.cell(row=offset, column=7, value=dist_name)
        c2 = ws.cell(row=offset, column=8, value=f"=COUNTIF('All Colleges'!H2:H{total_rows}, G{offset})")
        c1.font = BODY_FONT
        c2.font = BODY_FONT
        c2.number_format = "#,##0"
        c1.border = THIN_BORDER
        c2.border = THIN_BORDER

    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 4
    ws.column_dimensions["D"].width = 40
    ws.column_dimensions["E"].width = 12
    ws.column_dimensions["F"].width = 4
    ws.column_dimensions["G"].width = 28
    ws.column_dimensions["H"].width = 12


def main() -> None:
    with open(IN_JSON, encoding="utf-8") as f:
        records = json.load(f)

    wb = Workbook()
    ws_summary = wb.active
    ws_summary.title = "Summary"

    ws_all = wb.create_sheet("All Colleges")
    populate_college_sheet(ws_all, records, reindex=False)

    build_summary_sheet(ws_summary, records)

    known_cats = {cat for _, cat in CATEGORY_TABS if cat is not None}
    for tab_name, cat_filter in CATEGORY_TABS:
        if cat_filter is not None:
            subset = [r for r in records if r.get("category") == cat_filter]
        else:
            subset = [r for r in records if r.get("category") not in known_cats]
        if subset:
            ws_cat = wb.create_sheet(tab_name)
            populate_college_sheet(ws_cat, subset, reindex=True)

    wb.save(OUT_XLSX)
    print(f"Saved {OUT_XLSX.name} with {len(records)} records across {len(wb.sheetnames)} sheets.")


if __name__ == "__main__":
    main()
