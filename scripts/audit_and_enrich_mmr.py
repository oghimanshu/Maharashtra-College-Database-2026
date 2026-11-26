#!/usr/bin/env python3
"""
MMR Audit, JDTE Mumbai PDF Parser, +91 Mobile Extractor & Deep Crawler.
1. Audits and fixes existing records (strips DTE code prefixes, cleans '//' phone artifacts,
   removes verified false-positive website/IG mismatches, formats +91 mobile numbers).
2. Parses all 8 official JDTE Mumbai Region PDFs (2025) for Principal Name, Principal +91 Mobile,
   Official Website, Email, Address, Status, and DTE Code across Mumbai, Suburban, Thane, Raigad, Palghar.
3. Deep-crawls all MMR websites for Instagram IDs and +91 Faculty/Personal/Principal mobile numbers.
4. Adds `faculty_mobile` ("Faculty / Personal Mobile (+91)") column to JSON & CSV.
"""

import csv
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import pdfplumber
import requests
from bs4 import BeautifulSoup

from build_database import (
    OUT_CSV,
    OUT_JSON,
    add_source,
    classify_category,
    clean_instagram,
    clean_website,
    is_strict_name_match,
    norm_text,
    same_district_group,
)

PDF_DIR = Path("/tmp/jdte_pdfs")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

JDTE_DIST_MAP = {
    "mumbai": "Mumbai City",
    "mumbai city": "Mumbai City",
    "mumbai sub": "Mumbai Suburban",
    "mumbai suburban": "Mumbai Suburban",
    "thane": "Thane",
    "raigad": "Raigad",
    "palghar": "Palghar",
    "ratnagiri": "Ratnagiri",
    "sindhudurg": "Sindhudurg",
}

FALSE_POSITIVE_FIXES = {
    "International institute for population studies": {"website", "instagram_id", "college_phone"},
    "K J Somaiya College of Arts & Commerce Vidyanagar, Vidyavihar, Mumbai": {"website", "instagram_id"},
    "B R HARNE SCHOOL OF NURSING KARAV VANGANI TAL AMBARNATH": {"website", "instagram_id", "principal_name", "college_phone", "principal_phone"},
}


def format_indian_mobile(raw: str) -> str:
    """Extract and format valid Indian 10-digit mobile numbers (+91 XXXXXXXXXX)."""
    if not raw:
        return ""
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    elif len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    if len(digits) == 10 and digits[0] in "6789":
        return f"+91 {digits}"
    return ""


def extract_all_indian_mobiles(text: str) -> list[str]:
    """Find all unique valid +91 10-digit mobile numbers in arbitrary text."""
    found = []
    for m in re.finditer(r"(?:\+91[\s\-]?|0)?([6-9]\d{9})\b", text):
        num = f"+91 {m.group(1)}"
        if num not in found:
            found.append(num)
    return found


def clean_phone_field(p: str) -> str:
    p = norm_text(p)
    if not p:
        return ""
    # Replace // separators and clean trailing //
    parts = [x.strip() for x in re.split(r"//+", p) if x.strip() and x.strip() not in {"0", "0 Ext.- 0", "-"}]
    cleaned = []
    for part in parts:
        mob = format_indian_mobile(part)
        cleaned.append(mob if mob else part)
    return ", ".join(dict.fromkeys(cleaned))


def parse_jdte_pdfs() -> dict[str, dict[str, Any]]:
    """Parse Govt, Aided, Unaided, and District PDFs keyed by 4-digit DTE code."""
    by_dte: dict[str, dict[str, Any]] = {}

    def clean_cell(val: Any) -> str:
        if not val:
            return ""
        return re.sub(r"\s+", " ", str(val)).strip()

    # 1. District PDFs (Address + Status + Course Type)
    dist_files = [
        ("mumbai-city.pdf", "Mumbai City"),
        ("mumbai-sub.pdf", "Mumbai Suburban"),
        ("Thane-District.pdf", "Thane"),
        ("raigad-district.pdf", "Raigad"),
        ("palghar-district.pdf", "Palghar"),
    ]
    for fname, dist_name in dist_files:
        fpath = PDF_DIR / fname
        if not fpath.exists():
            continue
        with pdfplumber.open(fpath) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables() or []:
                    for row in table:
                        if not row or len(row) < 6:
                            continue
                        dte = clean_cell(row[1])
                        if not re.fullmatch(r"\d{4}", dte):
                            continue
                        by_dte[dte] = {
                            "dte_code": dte,
                            "name": clean_cell(row[2]),
                            "course": clean_cell(row[3]),
                            "status": clean_cell(row[4]),
                            "address": clean_cell(row[5]),
                            "district": dist_name,
                            "principal": "",
                            "mobile": "",
                            "email": "",
                            "website": "",
                        }

    # 2. Govt & Aided PDFs (10 columns)
    for fname, status_default in [("govt.pdf", "Government"), ("aided.pdf", "Government Aided")]:
        fpath = PDF_DIR / fname
        if not fpath.exists():
            continue
        with pdfplumber.open(fpath) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables() or []:
                    for row in table:
                        if not row or len(row) < 10:
                            continue
                        dte = clean_cell(row[1])
                        if not re.fullmatch(r"\d{4}", dte):
                            continue
                        dist_raw = clean_cell(row[4]).lower()
                        dist = JDTE_DIST_MAP.get(dist_raw, clean_cell(row[4]).title())
                        entry = by_dte.setdefault(dte, {
                            "dte_code": dte, "name": clean_cell(row[2]), "course": clean_cell(row[3]),
                            "status": status_default, "address": clean_cell(row[5]), "district": dist,
                            "principal": "", "mobile": "", "email": "", "website": "",
                        })
                        if clean_cell(row[6]):
                            entry["principal"] = clean_cell(row[6])
                        if clean_cell(row[7]):
                            entry["mobile"] = format_indian_mobile(clean_cell(row[7])) or clean_cell(row[7])
                        if clean_cell(row[8]) and "@" in clean_cell(row[8]):
                            entry["email"] = clean_cell(row[8]).replace(" ", "").lower()
                        if clean_cell(row[9]):
                            entry["website"] = clean_website(clean_cell(row[9]).replace(" ", ""))

    # 3. Unaided PDF (8 columns, 14 pages!)
    unaided_path = PDF_DIR / "unaided.pdf"
    if unaided_path.exists():
        with pdfplumber.open(unaided_path) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables() or []:
                    for row in table:
                        if not row or len(row) < 8:
                            continue
                        dte = clean_cell(row[1])
                        if not re.fullmatch(r"\d{4}", dte):
                            continue
                        dist_raw = clean_cell(row[4]).lower()
                        dist = JDTE_DIST_MAP.get(dist_raw, clean_cell(row[4]).title())
                        entry = by_dte.setdefault(dte, {
                            "dte_code": dte, "name": clean_cell(row[2]), "course": clean_cell(row[3]),
                            "status": "Unaided", "address": "", "district": dist,
                            "principal": "", "mobile": "", "email": "", "website": "",
                        })
                        if clean_cell(row[5]) and not entry["principal"]:
                            entry["principal"] = clean_cell(row[5])
                        if clean_cell(row[6]) and not entry["mobile"]:
                            entry["mobile"] = format_indian_mobile(clean_cell(row[6])) or clean_cell(row[6])
                        if clean_cell(row[7]) and not entry["website"]:
                            entry["website"] = clean_website(clean_cell(row[7]).replace(" ", ""))

    return by_dte


def crawl_for_mmr_details(base_url: str) -> dict[str, Any]:
    """Deep-crawl MMR website for Instagram, Principal, College Phone, Email, and +91 Mobiles."""
    merged: dict[str, Any] = {"instagram": "", "email": "", "phone": "", "principal": "", "mobiles": []}
    visited = set()

    for candidate in ([base_url, base_url.replace("https://", "http://", 1)] if base_url.startswith("https://") else [base_url]):
        try:
            r = requests.get(candidate, headers=HEADERS, timeout=5, allow_redirects=True)
            if r.status_code >= 400 or not r.text:
                continue
            visited.add(r.url)
            pages = [r.text]

            soup = BeautifulSoup(r.text[:250_000], "lxml")
            base_host = urlparse(r.url).netloc.lower()
            sub_links = []
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                label = a.get_text(" ", strip=True).lower()
                if any(kw in (href.lower() + " " + label) for kw in ["contact", "principal", "faculty", "staff", "about", "tpo", "placement", "administration"]):
                    full = urljoin(r.url, href)
                    if urlparse(full).netloc.lower() == base_host and full not in visited and not full.lower().endswith(".pdf"):
                        sub_links.append(full)

            sub_links.sort(key=lambda u: 0 if "principal" in u.lower() else (1 if "contact" in u.lower() else (2 if "faculty" in u.lower() else 3)))
            for link in list(dict.fromkeys(sub_links))[:4]:
                try:
                    sr = requests.get(link, headers=HEADERS, timeout=4, allow_redirects=True)
                    if sr.status_code < 400 and sr.text:
                        pages.append(sr.text)
                except Exception:
                    continue

            for html in pages:
                if not merged["instagram"]:
                    for m in re.finditer(r"https?://(?:www\.)?instagram\.com/([A-Za-z0-9._]{3,35})/?", html, re.I):
                        ig = clean_instagram(m.group(1))
                        if ig:
                            merged["instagram"] = ig
                            break
                if not merged["email"]:
                    emails = re.findall(r"mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})", html, re.I)
                    if emails:
                        emails = [e.lower() for e in emails if not e.lower().endswith((".png", ".jpg", ".webp"))]
                        emails.sort(key=lambda e: 0 if any(k in e for k in ["principal", "info", "office", "contact"]) else 1)
                        if emails:
                            merged["email"] = emails[0]
                text = BeautifulSoup(html[:200_000], "lxml").get_text(" ", strip=True)
                for mob in extract_all_indian_mobiles(text):
                    if mob not in merged["mobiles"]:
                        merged["mobiles"].append(mob)
                if not merged["phone"]:
                    tel = re.findall(r"tel:([+\d][\d\s\-()]{6,18})", html, re.I)
                    if tel:
                        merged["phone"] = re.sub(r"\s+", " ", tel[0]).strip()
                if not merged["principal"]:
                    pm = re.search(r"Principal(?:'s)?\s*(?:Name)?\s*[:\-–]\s*((?:Dr\.|Prof\.|Shri|Smt\.|Mr\.|Ms\.)?\s*[A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+){1,3})", text)
                    if pm:
                        cand = re.sub(r"\s+", " ", pm.group(1)).strip(" ,.-:")
                        bad = {"desk", "message", "office", "profile", "college", "about", "welcome", "home", "read", "more"}
                        if 5 <= len(cand) <= 45 and not any(bw in cand.lower().split() for bw in bad):
                            merged["principal"] = cand
            break
        except Exception:
            continue
    return merged


def main() -> None:
    with open(OUT_JSON, encoding="utf-8") as f:
        records: list[dict[str, Any]] = json.load(f)

    print(f"1. Auditing {len(records)} existing records...")
    for rec in records:
        rec.setdefault("faculty_mobile", "")

        # Strip leading 4-digit DTE prefix (e.g. '3006-Government...')
        m_pref = re.match(r"^(\d{4})\s*-\s*(.+)$", rec["name"])
        if m_pref:
            if not rec["aishe_code"]:
                rec["aishe_code"] = f"DTE-{m_pref.group(1)}"
            rec["name"] = m_pref.group(2).strip()

        # Apply specific false-positive fixes caught during audit
        for bad_name, fields in FALSE_POSITIVE_FIXES.items():
            if rec["name"].lower().startswith(bad_name[:35].lower()):
                for fld in fields:
                    rec[fld] = ""

        if rec.get("instagram_id") == "@thelanguagesphere":
            rec["instagram_id"] = ""

        # Clean phone fields & extract +91 mobile numbers
        rec["college_phone"] = clean_phone_field(rec.get("college_phone", ""))
        rec["principal_phone"] = clean_phone_field(rec.get("principal_phone", ""))

        mobs = []
        for fld in ["principal_phone", "college_phone"]:
            for m in extract_all_indian_mobiles(rec.get(fld, "")):
                if m not in mobs:
                    mobs.append(m)
        if mobs:
            rec["faculty_mobile"] = ", ".join(mobs[:3])

    print("2. Parsing 8 official JDTE Mumbai Region PDFs (2025)...")
    jdte_map = parse_jdte_pdfs()
    print(f"   Parsed {len(jdte_map)} DTE institutes with MMR details.")

    matched_jdte = 0
    added_jdte = 0
    for dte_code, item in jdte_map.items():
        target = None
        # Match by existing DTE code or strict name + district
        for rec in records:
            if rec.get("aishe_code") == f"DTE-{dte_code}":
                target = rec
                break
        if not target:
            for rec in records:
                if same_district_group(rec["district"], item["district"]) and is_strict_name_match(rec["name"], item["name"]):
                    target = rec
                    break

        if target:
            matched_jdte += 1
            if not target["aishe_code"]:
                target["aishe_code"] = f"DTE-{dte_code}"
        else:
            added_jdte += 1
            target = {
                "aishe_code": f"DTE-{dte_code}",
                "name": item["name"],
                "principal_name": "",
                "college_phone": "",
                "principal_phone": "",
                "faculty_mobile": "",
                "instagram_id": "",
                "district": item["district"],
                "city": item["district"],
                "category": classify_category(item["name"] + " " + item["course"]),
                "affiliation": "DTE Maharashtra / University of Mumbai",
                "management_type": item["status"] or "Unaided",
                "email": "",
                "website": "",
                "address": "",
                "verification_source": "",
            }
            records.append(target)

        add_source(target, "JDTE Mumbai (2025)")
        if item["principal"]:
            target["principal_name"] = item["principal"]
        if item["mobile"]:
            target["principal_phone"] = item["mobile"]
            existing_mobs = [x.strip() for x in target["faculty_mobile"].split(",") if x.strip()]
            if item["mobile"] not in existing_mobs:
                existing_mobs.insert(0, item["mobile"])
            target["faculty_mobile"] = ", ".join(existing_mobs[:3])
        if item["email"] and not target["email"]:
            target["email"] = item["email"]
        if item["website"] and not target["website"]:
            target["website"] = item["website"]
        if item["address"] and not target["address"]:
            target["address"] = item["address"]
        if item["status"]:
            target["management_type"] = item["status"]

    print(f"   JDTE Mumbai: matched {matched_jdte}, added {added_jdte} new institutes.")

    # Step 3: Deep-crawl ALL MMR colleges with websites for +91 mobiles & Instagram
    mmr_dists = {"Mumbai City", "Mumbai Suburban", "Thane", "Raigad", "Palghar"}
    mmr_with_web = [r for r in records if r["district"] in mmr_dists and r["website"]]
    print(f"3. Deep-crawling {len(mmr_with_web)} MMR college websites for +91 mobiles, Principal & Instagram...")
    mob_added = 0
    ig_added = 0
    with ThreadPoolExecutor(max_workers=20) as pool:
        futs = {pool.submit(crawl_for_mmr_details, r["website"]): r for r in mmr_with_web}
        for fut in as_completed(futs):
            rec = futs[fut]
            try:
                info = fut.result()
                changed = False
                if info["instagram"] and not rec["instagram_id"]:
                    rec["instagram_id"] = info["instagram"]
                    ig_added += 1
                    changed = True
                if info["principal"] and not rec["principal_name"]:
                    rec["principal_name"] = info["principal"]
                    changed = True
                if info["phone"] and not rec["college_phone"]:
                    rec["college_phone"] = clean_phone_field(info["phone"])
                    changed = True
                if info["email"] and not rec["email"]:
                    rec["email"] = info["email"]
                    changed = True
                if info["mobiles"]:
                    existing = [x.strip() for x in rec["faculty_mobile"].split(",") if x.strip()]
                    for m in info["mobiles"]:
                        if m not in existing:
                            existing.append(m)
                    new_val = ", ".join(existing[:3])
                    if new_val != rec["faculty_mobile"]:
                        rec["faculty_mobile"] = new_val
                        mob_added += 1
                        changed = True
                if changed:
                    add_source(rec, "Official Website")
            except Exception:
                pass
    print(f"   MMR deep crawl -> +{ig_added} Instagram, +{mob_added} colleges with +91 Faculty/Personal Mobiles.")

    priority_order = {
        "Mumbai City": 0, "Mumbai Suburban": 1, "Thane": 2, "Raigad": 3, "Palghar": 4,
        "Pune": 5, "Nagpur": 6, "Nashik": 7, "Chhatrapati Sambhajinagar": 8, "Kolhapur": 9,
    }
    records.sort(key=lambda r: (
        0 if (r["principal_name"] or r["faculty_mobile"] or r["college_phone"] or r["instagram_id"]) else 1,
        priority_order.get(r["district"], 99),
        r["district"],
        r["name"],
    ))
    for idx, rec in enumerate(records, start=1):
        rec["sr_no"] = idx

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    field_map = [
        ("sr_no", "Sr. No."),
        ("name", "Name of the College"),
        ("principal_name", "Principal Name"),
        ("college_phone", "Phone Number of the College"),
        ("principal_phone", "Phone Number of the Principal"),
        ("faculty_mobile", "Faculty / Personal Mobile (+91)"),
        ("instagram_id", "Instagram ID"),
        ("district", "District"),
        ("city", "City / Area"),
        ("category", "Category / Stream"),
        ("affiliation", "University / Board Affiliation"),
        ("management_type", "Management Type"),
        ("email", "Official Email ID"),
        ("website", "Official Website"),
        ("address", "Full Address & Pincode"),
        ("aishe_code", "AISHE / DTE Code"),
        ("verification_source", "Data Source / Verification"),
    ]
    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([label for _, label in field_map])
        for rec in records:
            writer.writerow([rec.get(key, "") for key, _ in field_map])

    print(f"Saved audited & MMR-enriched {len(records)} records.")


if __name__ == "__main__":
    main()
