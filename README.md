# Maharashtra College Database (2026)

A comprehensive, audited directory of **10,448 colleges and higher-education institutions across Maharashtra** (covering Degree, Engineering, Polytechnic, Architecture, Medical, Dental, Pharmacy, Management, Law, Junior Colleges, and Universities), with a strong focus on **Mumbai & the Mumbai Metropolitan Region (MMR)**.

Includes a **multi-sheet Excel workbook**, **CSV/JSON datasets**, and an **offline-ready fuzzy-search web interface** (`docs/index.html`, ready for GitHub Pages).

---

## Key Features

- **10,448 Unique Institutions** across all 36+ districts of Maharashtra (deduplicated across AISHE, University affiliation records, and 2025 JDTE Mumbai Region PDFs).
- **17 Structured Columns:**
  - `Sr. No.`
  - `Name of the College`
  - `Principal Name`
  - `Phone Number of the College`
  - `Phone Number of the Principal`
  - `Faculty / Personal Mobile (+91)` *(strictly validated `+91 [6-9]XXXXXXXXX`)*
  - `Instagram ID` *(verified official handles)*
  - `District` & `City / Area`
  - `Category / Stream`
  - `University / Board Affiliation`
  - `Management Type`
  - `Official Email ID`
  - `Official Website`
  - `Full Address & Pincode`
  - `AISHE / DTE Code`
  - `Data Source / Verification`
- **Multi-Sheet Excel Workbook (`data/maharashtra_colleges.xlsx`):**
  - `Summary` dashboard with live `COUNTA` / `COUNTIF` formulas
  - `All Colleges` master sheet + category-specific tabs (`Degree Colleges`, `Engineering & Tech`, `Medical & Pharmacy`, `Management & Law`, `Junior Colleges`, `Universities & Others`)
  - Frozen headers, auto-filters, and clickable Website, Email, and Instagram hyperlinks.
- **Zero-Dependency Fuzzy Search Web App (`docs/index.html`):**
  - Works completely offline (double-click `docs/index.html`) or hosted directly via **GitHub Pages** (`docs/`).
  - Typo-tolerant fuzzy search across all fields with match highlighting, District/Category/Contact filters, pagination, one-click phone copy, and **Export Filtered CSV**.

---

## Dataset Coverage Summary

| Field | Verified Records |
| --- | ---: |
| **Total Unique Institutions** | **10,448** |
| University / Board Affiliation | 5,372 |
| Official Website | 655 |
| Principal Name | 556 |
| Official Email ID | 541 |
| Full Address & Pincode | 521 |
| Phone Number of the Principal | 483 |
| Phone Number of the College | 472 |
| Faculty / Personal Mobile (`+91`) | 388 |
| Verified Instagram ID | 209 |

> Unavailable fields are intentionally left blank rather than guessed or fabricated.

---

## Repository Structure

```text
Maharashtra-College-Database-2026/
├── data/
│   ├── maharashtra_colleges.xlsx   # Styled 8-sheet Excel workbook
│   ├── maharashtra_colleges.csv    # UTF-8 BOM CSV for universal import
│   └── maharashtra_colleges.json   # Clean structured JSON
├── docs/
│   └── index.html                  # Self-contained fuzzy-search web app (GitHub Pages ready)
├── scripts/
│   ├── build_database.py           # Base AISHE + University + DTE merge
│   ├── enrich_colleges.py          # Wikidata + multi-page website crawler
│   ├── audit_and_enrich_mmr.py     # 2025 JDTE Mumbai PDF parser & MMR +91 crawler
│   ├── final_audit_clean.py        # Deduplication, phone/IG normalization
│   ├── upgrade_mmr_and_dedup.py    # Flagship Mumbai/MMR Degree/Junior/Law/Medical pass
│   ├── generate_excel.py           # Excel (.xlsx) generator
│   └── generate_html.py            # Self-contained HTML generator
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Quick Start

### 1. Use the Data Directly
- **Excel:** Open `data/maharashtra_colleges.xlsx`.
- **Fuzzy Search UI:** Open `docs/index.html` in any browser (or enable **GitHub Pages** from `Settings -> Pages -> Deploy from branch -> /docs`).

### 2. Regenerate Excel & HTML from JSON
If you edit or add records in `data/maharashtra_colleges.json`, regenerate both outputs with:

```bash
pip install -r requirements.txt
python3 scripts/generate_excel.py
python3 scripts/generate_html.py
```

---

## Data Sources & Disclaimer

All institutional names, codes, addresses, websites, official contact numbers, and social handles in this repository are compiled exclusively from **publicly available sources**, including:
- **AISHE** (All India Survey on Higher Education) public institution directories
- **JDTE Mumbai Region (2025)** public Government, Aided, Unaided, and District institute PDFs (`jdteromumbai.org.in`)
- **DTE Maharashtra** public institute lists
- **Wikidata** & **Official College Websites**

This dataset is provided for **educational, research, and institutional outreach purposes**. If any institution wishes to update, correct, or request removal of a contact entry, please open an issue or pull request.

---

## Author & License

Made by **Himanshu Gaur** ([`@oghimanshu`](https://github.com/oghimanshu) • `wtfhimanshu@outlook.com`).

Licensed under the [MIT License](LICENSE).
