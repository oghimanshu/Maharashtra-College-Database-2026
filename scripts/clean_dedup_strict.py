#!/usr/bin/env python3
"""
Strict Cleanup & Deduplication Pass:
1. Removes non-college entities ('Research & Hospitals': labs, hospitals, regulatory boards).
2. Scrubs fake/placeholder phone numbers (repeated/sequential digits) and dummy emails.
3. Merges true remaining duplicates (ignoring trailing ', <District>/<City>' suffixes)
   while preserving distinct programs/streams (B.Pharm vs D.Pharm, Engg vs Pharmacy, etc.).
"""

import csv
import json
import re
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IN_JSON = DATA_DIR / "maharashtra_colleges.json"
OUT_CSV = DATA_DIR / "maharashtra_colleges.csv"

FAKE_PHONES = {
    "9999999999", "8888888888", "7777777777", "6666666666", "0000000000",
    "9876543210", "1234567890", "9898989898", "9988776655", "12345678",
}

FAKE_EMAIL_PARTS = {
    "example.com", "domain.com", "test.com", "email.com", "yoursite.com",
    "test@", "example@", "yourname@", "noreply@", "donotreply@",
}

PROGRAM_MARKERS = [
    "b pharm", "d pharm", "b.pharm", "d.pharm", "b.ed", "d.ed", "m.ed",
    "polytechnic", "engineering", "pharmacy", "management", "law", "nursing",
    "architecture", "junior", "senior", "medical", "dental", "ayurved",
]


def is_fake_phone(p: str) -> bool:
    digits = re.sub(r"\D", "", p)
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if digits in FAKE_PHONES:
        return True
    if len(digits) >= 7 and len(set(digits)) <= 2:
        return True
    return False


def normalize_phone_list(raw: str, mobiles_only: bool = False) -> str:
    if not raw:
        return ""
    out = []
    for p in re.split(r"[,;/]+", raw):
        p = p.strip()
        if not p:
            continue
        if mobiles_only and not p.startswith("+91 "):
            continue
        if p not in out:
            out.append(p)
    return ", ".join(out[:3])


def merge_records(primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    c1, c2 = (primary.get("aishe_code") or "").strip(), (secondary.get("aishe_code") or "").strip()
    if c1 and c2 and c1 != c2:
        codes = []
        for c in (c1.split(" / ") + c2.split(" / ")):
            if c and c not in codes:
                codes.append(c)
        primary["aishe_code"] = " / ".join(codes)
    elif c2 and not c1:
        primary["aishe_code"] = c2
    for fld in ["principal_name", "college_phone", "principal_phone", "faculty_mobile", "instagram_id", "email", "website", "address", "affiliation"]:
        v1, v2 = (primary.get(fld) or "").strip(), (secondary.get(fld) or "").strip()
        if v2 and not v1:
            primary[fld] = v2
    srcs = [s.strip() for s in (primary.get("verification_source", "") + "+" + secondary.get("verification_source", "")).split("+") if s.strip()]
    primary["verification_source"] = " + ".join(dict.fromkeys(srcs))
    return primary


def scrub_phones(raw: str, mobiles_only: bool = False) -> str:
    norm = normalize_phone_list(raw, mobiles_only=mobiles_only)
    if not norm:
        return ""
    kept = [p.strip() for p in norm.split(",") if p.strip() and not is_fake_phone(p)]
    return ", ".join(kept)


def scrub_email(em: str) -> str:
    em = (em or "").strip().lower()
    if not em or "@" not in em:
        return ""
    if any(fp in em for fp in FAKE_EMAIL_PARTS):
        return ""
    return em


def canonical_dedup_key(name: str, district: str) -> str:
    s = name.lower()
    # Strip trailing ', <District>' or ', Mumbai' etc.
    s = re.sub(r",?\s*\b(?:mumbai|mumbai city|mumbai suburban|thane|pune|nagpur|nashik|raigad|palghar|navi mumbai|maharashtra)\b\s*$", "", s)
    s = s.replace("&", " and ")
    # Extract any explicit program marker so B.Pharm and D.Pharm never merge
    markers = [m for m in PROGRAM_MARKERS if re.search(rf"\b{re.escape(m)}\b", s)]
    s = re.sub(r"[^a-z0-9]", "", s)
    return f"{s}::{'|'.join(markers)}"


def main() -> None:
    with open(IN_JSON, encoding="utf-8") as f:
        records: list[dict[str, Any]] = json.load(f)

    initial_count = len(records)

    # 1. Remove non-college Research & Hospitals
    colleges = [r for r in records if r.get("category") != "Research & Hospitals"]
    removed_non_college = initial_count - len(colleges)

    # 2. Scrub fake phones & emails
    fake_phones_scrubbed = 0
    fake_emails_scrubbed = 0
    for r in colleges:
        for fld, mob_only in [("college_phone", False), ("principal_phone", False), ("faculty_mobile", True)]:
            old_v = r.get(fld, "")
            new_v = scrub_phones(old_v, mobiles_only=mob_only)
            if old_v and new_v != old_v:
                fake_phones_scrubbed += 1
            r[fld] = new_v

        old_em = r.get("email", "")
        new_em = scrub_email(old_em)
        if old_em and not new_em:
            fake_emails_scrubbed += 1
        r["email"] = new_em

    # 3. Strict deduplication ignoring trailing district/city
    deduped: list[dict[str, Any]] = []
    key_map: dict[tuple[str, str], int] = {}
    dups_merged = 0

    for r in colleges:
        dg = "mumbai" if "mumbai" in r["district"].lower() else r["district"].lower()
        ck = canonical_dedup_key(r["name"], r["district"])
        if ck and (ck, dg) in key_map:
            idx = key_map[(ck, dg)]
            deduped[idx] = merge_records(deduped[idx], r)
            dups_merged += 1
        else:
            idx = len(deduped)
            deduped.append(r)
            if ck:
                key_map[(ck, dg)] = idx

    priority_order = {
        "Mumbai City": 0, "Mumbai Suburban": 1, "Thane": 2, "Raigad": 3, "Palghar": 4,
        "Pune": 5, "Nagpur": 6, "Nashik": 7, "Chhatrapati Sambhajinagar": 8, "Kolhapur": 9,
    }
    deduped.sort(key=lambda r: (
        0 if (r["principal_name"] or r["faculty_mobile"] or r["college_phone"] or r["instagram_id"]) else 1,
        priority_order.get(r["district"], 99),
        r["district"],
        r["name"],
    ))
    for idx, rec in enumerate(deduped, start=1):
        rec["sr_no"] = idx

    with open(IN_JSON, "w", encoding="utf-8") as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)

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
        for rec in deduped:
            writer.writerow([rec.get(key, "") for key, _ in field_map])

    print(f"Initial: {initial_count}")
    print(f"Removed non-college Research & Hospitals: {removed_non_college}")
    print(f"Scrubbed fake/placeholder phones: {fake_phones_scrubbed} | emails: {fake_emails_scrubbed}")
    print(f"Merged true remaining duplicates: {dups_merged}")
    print(f"Final clean colleges: {len(deduped)}")


if __name__ == "__main__":
    main()
