<div align="center">

# 🎓 Maharashtra College Database (2026)

**A curated, audited directory of 10,249 colleges & universities across Mumbai, MMR, and Maharashtra**  
*Principals • Direct `+91` Mobiles • Verified Instagram IDs • Official Websites • Fuzzy Search*

[![Live Directory](https://img.shields.io/badge/Live_Web_App-GitHub_Pages-2563eb?style=for-the-badge&logo=github)](https://oghimanshu.github.io/Maharashtra-College-Database-2026/)
[![Institutions](https://img.shields.io/badge/Colleges-10%2C249-10b981?style=for-the-badge)](#dataset-coverage)
[![Excel Ready](https://img.shields.io/badge/Format-XLSX_%7C_CSV_%7C_JSON-6366f1?style=for-the-badge)](#repository-structure)
[![License: MIT](https://img.shields.io/badge/License-MIT-f472b6?style=for-the-badge)](LICENSE)

</div>

---

## ✨ Highlights

- **10,249 Verified Teaching Institutions** across all **36+ districts** of Maharashtra (non-college labs/hospitals removed, duplicates merged, ALL-CAPS names normalized, and 2,331+ localities extracted).
- **Interactive GitHub Pages Web App (`docs/index.html`):**
  - **Animated Aurora & Glassmorphic UI** with high-contrast typography and smooth micro-interactions.
  - **Typo-Tolerant Fuzzy Search** (`/` shortcut + shareable URL parameters) across college names, principals, `+91` mobiles, Instagram handles, cities, affiliations, and AISHE/DTE codes.
  - **Outreach Toolkit:** Star/Shortlist (`★`) colleges in `localStorage`, launch direct **WhatsApp (`wa.me`)** chats from `+91` numbers, copy contacts in one click, and export filtered/shortlisted CSVs.
  - **Table & Card Grid Views** + **Slide-Over Detail Drawer** (`←` / `→` keyboard navigation) + **Collapsible Insights Bar**.
- **8-Sheet Styled Excel Workbook (`data/maharashtra_colleges.xlsx`):**
  - Live `Summary` dashboard with `COUNTA` / `COUNTIF` formulas, `All Colleges` master sheet, and category-specific tabs with frozen headers, auto-filters, and clickable hyperlinks.

---

## 📊 Dataset Coverage

| Metric | Verified Count |
| --- | ---: |
| **Total Unique Colleges & Universities** | **10,249** |
| University / Board Affiliation | 5,271 |
| Official Website | 651 |
| Principal Name | 554 |
| Official Email ID | 538 |
| Full Address & Pincode | 519 |
| Phone Number of the Principal | 482 |
| Phone Number of the College | 470 |
| Faculty / Personal Mobile (`+91`) | 386 |
| Verified Instagram ID | 207 |

<details>
<summary><strong>📂 Category Breakdown (10,249 Institutions)</strong></summary>

| Category / Stream | Count |
| --- | ---: |
| Degree College (Arts / Science / Commerce) | 3,278 |
| Medical, Dental & Pharmacy | 2,507 |
| Education & Training | 1,586 |
| Management & Law | 1,262 |
| Engineering, Polytechnic & Architecture | 1,256 |
| Junior College | 150 |
| Agriculture & Allied | 123 |
| University | 106 |

</details>

> Unavailable fields are intentionally left blank rather than guessed or fabricated.

---

## 🗂️ Schema (17 Columns)

| # | Column | Notes |
| :-: | --- | --- |
| 1 | `Sr. No.` | Priority-sorted (enriched MMR & Maharashtra first) |
| 2 | `Name of the College` | Title-cased with preserved acronyms (`VJTI`, `SIES`, `NMIMS`) |
| 3 | `Principal Name` | Verified from JDTE 2025 PDFs & official websites |
| 4 | `Phone Number of the College` | Standardized `0STD-NUMBER` & `(Ext. X)` |
| 5 | `Phone Number of the Principal` | Direct desk or `+91` mobile |
| 6 | `Faculty / Personal Mobile (+91)` | Strictly validated `+91 [6-9]XXXXXXXXX` |
| 7 | `Instagram ID` | Verified official `@handle` |
| 8 | `District` | Standardized Maharashtra districts |
| 9 | `City / Area` | Suburb / locality / taluka (`Dadar`, `Vashi`, `Kothrud`, etc.) |
| 10 | `Category / Stream` | Degree, Engineering, Medical, Management/Law, Junior, etc. |
| 11 | `University / Board Affiliation` | University of Mumbai, SPPU, DTE, etc. |
| 12 | `Management Type` | Government, Aided, Unaided, Autonomous, University |
| 13 | `Official Email ID` | Verified institutional/principal email |
| 14 | `Official Website` | Verified official URL |
| 15 | `Full Address & Pincode` | Campus address & 6-digit PIN |
| 16 | `AISHE / DTE Code` | Official `C-xxxxx` / `DTE-xxxx` identifier |
| 17 | `Data Source / Verification` | Provenance trail (`AISHE`, `JDTE Mumbai (2025)`, `Official Website`, etc.) |

---

## 📁 Repository Structure

```text
Maharashtra-College-Database-2026/
├── data/
│   ├── maharashtra_colleges.xlsx      # Styled 8-sheet Excel workbook
│   ├── maharashtra_colleges.csv       # UTF-8 BOM CSV
│   └── maharashtra_colleges.json      # Structured JSON (10,249 records)
├── docs/
│   ├── .nojekyll                      # Instant GitHub Pages serving
│   └── index.html                     # Self-contained fuzzy-search web app
├── scripts/
│   ├── build_database.py              # Base AISHE + University + DTE merge
│   ├── enrich_colleges.py             # Wikidata + multi-page website crawler
│   ├── audit_and_enrich_mmr.py        # 2025 JDTE Mumbai PDFs & MMR +91 crawler
│   ├── final_audit_clean.py           # Deduplication, phone/IG normalization
│   ├── upgrade_mmr_and_dedup.py       # Flagship Mumbai/MMR Degree/Junior/Law/Medical pass
│   ├── refine_data.py                 # Title-casing, locality parsing & category cleanup
│   ├── clean_dedup_strict.py          # Non-college removal & strict dedup
│   ├── generate_excel.py              # Excel (.xlsx) generator
│   └── generate_html.py               # GitHub Pages HTML generator
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start

### Use Immediately
- **Live Web App:** Open `docs/index.html` locally in any browser, or host via **GitHub Pages** (`Settings → Pages → Deploy from branch → main /docs`).
- **Excel:** Open [`data/maharashtra_colleges.xlsx`](data/maharashtra_colleges.xlsx).

### Regenerate Outputs from JSON
```bash
pip install -r requirements.txt
python3 scripts/generate_excel.py
python3 scripts/generate_html.py
```

---

## 📜 Data Sources & Disclaimer

Compiled exclusively from publicly available sources: **AISHE** institution directories, **JDTE Mumbai Region (2025)** Government/Aided/Unaided/District PDFs (`jdteromumbai.org.in`), **DTE Maharashtra** institute lists, **Wikidata**, and **official college websites**. Provided for educational, research, and institutional outreach purposes—open an issue or PR for any corrections or removal requests.

---

<div align="center">

Made by **Himanshu Gaur** • [`@oghimanshu`](https://github.com/oghimanshu) • `wtfhimanshu@outlook.com`  
Licensed under the [MIT License](LICENSE)

</div>
