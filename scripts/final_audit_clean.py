#!/usr/bin/env python3
"""
Final Quality Audit & Normalization Script:
1. Merges duplicate college rows (same website in same district, or normalized name match),
   combining AISHE + DTE codes, affiliation, and all verified contacts.
2. Fixes PDF line-wrap artifacts in names, principals, emails, and addresses.
3. Maps Instagram IDs cleanly (removes third-party handles like @teepublic, @thelanguagesphere).
4. Normalizes all phone numbers across College Phone, Principal Phone, and Faculty/Personal Mobile (+91):
   - Standardizes STD codes with leading 0 (e.g. 022-XXXXXXXX)
   - Cleans extensions (Ext. 123)
   - Drops truncated 9-digit / invalid numbers
   - Ensures Faculty / Personal Mobile (+91) contains ONLY valid +91 10-digit mobiles.
"""

import csv
import json
import re
from collections import Counter, defaultdict
from typing import Any
from urllib.parse import urlparse

from build_database import (
    OUT_CSV,
    OUT_JSON,
    add_source,
    is_strict_name_match,
    norm_text,
    same_district_group,
)

BAD_IG_HANDLES = {
    "@teepublic", "@thelanguagesphere", "@yourprofile", "@yourusername",
    "@instagram", "@facebook", "@twitter", "@youtube", "@linkedin",
    "@wix", "@wordpress", "@google", "@gmail", "@example", "@official",
    "@handle", "@test", "@demo", "@user", "@username",
}

MULTI_CAMPUS_HOSTS = {
    "somaiya.edu", "sinhgad.edu", "met.edu", "mes.ac.in", "sandipfoundation.org",
    "bharatividyapeeth.edu", "dypatil.edu", "mitpune.edu.in",
}

PDF_WRAP_FIXES = [
    (r"\bARCHITECTUR\s+E\b", "ARCHITECTURE"),
    (r"\bGOVERNMEN\s+T\b", "GOVERNMENT"),
    (r"\bRATNAGIR\s+I\b", "RATNAGIRI"),
    (r"\bBHATTACHARY\s+YA\b", "BHATTACHARYYA"),
    (r"\bNAVINCHAND\b", "NAVINCHANDRA"),
    (r"\bMANAGEMEN\s+T\b", "MANAGEMENT"),
    (r"\bTECHNOLOG\s+Y\b", "TECHNOLOGY"),
    (r"\bENGINEERIN\s+G\b", "ENGINEERING"),
    (r"\bINSTITUT\s+E\b", "INSTITUTE"),
]


def fix_pdf_wraps(s: str) -> str:
    s = norm_text(s)
    for pat, rep in PDF_WRAP_FIXES:
        s = re.sub(pat, rep, s)
    return s


def clean_principal_name(p: str) -> str:
    p = fix_pdf_wraps(p)
    if not p:
        return ""
    # Remove role suffixes/prefixes
    p = re.sub(r",?\s*(?:Former\s+)?(?:I/C\s+|Incharge\s+)?(?:Principal|Director|H\.?O\.?D\.?)\b.*$", "", p, flags=re.I)
    p = re.sub(r"^(?:I/C|Incharge|Director|Principal)\s+", "", p, flags=re.I)
    p = re.sub(r"\(\s*(?:I/C\s*)?(?:Principal|Director|Registrar)\s*\)", "", p, flags=re.I)
    p = re.sub(r"\s+", " ", p).strip(" ,.-:")
    if len(p) < 4:
        return ""
    return p


def format_mobile(digits: str) -> str:
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    elif len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    if len(digits) == 10 and digits[0] in "6789":
        return f"+91 {digits}"
    return ""


def normalize_single_phone(raw: str) -> str:
    """Normalize a single phone token into either '+91 XXXXXXXXXX' or '0STD-NUMBER (Ext. X)'."""
    s = norm_text(raw)
    if not s:
        return ""

    # Handle extension
    ext = ""
    m_ext = re.search(r"(?:Ext\.?[-:\s]*|Extension[-:\s]*)(\d+)", s, re.I)
    if m_ext:
        if m_ext.group(1) not in {"0", "00"}:
            ext = f" (Ext. {m_ext.group(1)})"
        s = s[:m_ext.start()].strip(" ,-")

    # Strip trailing Ext.- with no number
    s = re.sub(r"\s*Ext\.?[-:\s]*$", "", s, flags=re.I).strip()
    if not s:
        return ""

    digits = re.sub(r"\D", "", s)
    if not digits or set(digits) == {"0"}:
        return ""

    # Check if valid Indian mobile (10 digits starting with 6-9, or 0+10, or 91+10)
    mob = format_mobile(digits)
    if mob:
        return mob

    # Reject truncated 9-digit mobile numbers (e.g. 976917771, 986985566)
    if len(digits) == 9 and digits[0] in "6789":
        return ""

    # Check STD-number format like 22-25973737 or 251-2910190 or 022-25973737
    m_std = re.match(r"^0?(\d{2,4})[\s\-]+(\d{6,8})$", s)
    if m_std:
        std, num = m_std.group(1), m_std.group(2)
        return f"0{std}-{num}{ext}"

    # Pure digits 10-11 starting with non-mobile (landline with STD)
    if 10 <= len(digits) <= 11:
        if not digits.startswith("0"):
            digits = "0" + digits
        if digits.startswith(("011", "020", "022", "033", "040", "044", "079", "080")):
            return f"{digits[:3]}-{digits[3:]}{ext}"
        return f"{digits[:4]}-{digits[4:]}{ext}"

    # 6-8 digit local landline
    if 6 <= len(digits) <= 8:
        return f"{digits}{ext}"

    return ""


def normalize_phone_list(raw: str, mobiles_only: bool = False) -> str:
    if not raw:
        return ""
    parts = [x.strip() for x in re.split(r"[,;/]+", raw) if x.strip()]
    out = []
    for p in parts:
        norm = normalize_single_phone(p)
        if not norm:
            continue
        if mobiles_only and not norm.startswith("+91 "):
            continue
        if norm not in out:
            out.append(norm)
    return ", ".join(out[:3])


def get_site_key(url: str) -> str:
    if not url:
        return ""
    try:
        p = urlparse(url)
        host = p.netloc.lower().lstrip("www.")
        if host in MULTI_CAMPUS_HOSTS:
            path = p.path.strip("/").split("/")[0] if p.path.strip("/") else ""
            return f"{host}/{path}" if path else host
        return host
    except Exception:
        return ""


def merge_records(primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    """Merge secondary college record into primary without losing any verified data."""
    # Combine AISHE & DTE codes
    c1, c2 = norm_text(primary.get("aishe_code")), norm_text(secondary.get("aishe_code"))
    if c1 and c2 and c1 != c2:
        codes = []
        for c in (c1.split(" / ") + c2.split(" / ")):
            if c and c not in codes:
                codes.append(c)
        primary["aishe_code"] = " / ".join(codes)
    elif c2 and not c1:
        primary["aishe_code"] = c2

    # Prefer non-empty fields; prefer longer/cleaner affiliation & address
    for fld in ["principal_name", "college_phone", "principal_phone", "faculty_mobile", "instagram_id", "email", "website", "address", "affiliation"]:
        v1, v2 = norm_text(primary.get(fld)), norm_text(secondary.get(fld))
        if v2 and not v1:
            primary[fld] = v2
        elif fld in {"address", "affiliation"} and len(v2) > len(v1) and "dte maharashtra" not in v2.lower():
            primary[fld] = v2

    # Combine verification sources
    for src in secondary.get("verification_source", "").split("+"):
        if src.strip():
            add_source(primary, src.strip())

    # Prefer cleaner name (without DTE prefix or all-caps if mixed-case exists)
    n1, n2 = primary["name"], secondary["name"]
    if n1.isupper() and not n2.isupper():
        primary["name"] = n2

    return primary


def main() -> None:
    with open(OUT_JSON, encoding="utf-8") as f:
        records: list[dict[str, Any]] = json.load(f)

    print(f"Starting audit on {len(records)} records...")

    # Pass 1: Clean text, names, Instagram, and phones on each record
    for rec in records:
        rec["name"] = fix_pdf_wraps(rec["name"])
        rec["principal_name"] = clean_principal_name(rec.get("principal_name", ""))
        rec["address"] = fix_pdf_wraps(rec.get("address", ""))
        rec["email"] = norm_text(rec.get("email", "")).replace(" ", "").lower()

        ig = norm_text(rec.get("instagram_id", "")).lower()
        if ig in BAD_IG_HANDLES or (ig and len(ig) < 4):
            ig = ""
        rec["instagram_id"] = ig

        rec["college_phone"] = normalize_phone_list(rec.get("college_phone", ""), mobiles_only=False)
        rec["principal_phone"] = normalize_phone_list(rec.get("principal_phone", ""), mobiles_only=False)

        # Build strict +91-only Faculty / Personal Mobile
        raw_mobs = ", ".join(filter(None, [rec.get("faculty_mobile", ""), rec.get("principal_phone", ""), rec.get("college_phone", "")]))
        rec["faculty_mobile"] = normalize_phone_list(raw_mobs, mobiles_only=True)

    # Pass 2: Deduplicate & Merge records sharing the same official website (and district group) or strict name
    merged_list: list[dict[str, Any]] = []
    site_index: dict[tuple[str, str], int] = {}

    # Sort so AISHE-coded records come first as primary, or richest record first
    records.sort(key=lambda r: (
        0 if r.get("aishe_code", "").startswith(("C-", "U-", "S-", "R-")) else 1,
        -sum(1 for k in ["principal_name", "college_phone", "principal_phone", "faculty_mobile", "website", "instagram_id"] if r.get(k)),
    ))

    dups_merged = 0
    for rec in records:
        dist_group = "mumbai" if "mumbai" in rec["district"].lower() else rec["district"].lower()
        skey = get_site_key(rec.get("website", ""))

        merged_idx = None
        if skey and (skey, dist_group) in site_index:
            cand_idx = site_index[(skey, dist_group)]
            # Only merge on same site if names are compatible OR same campus/acronym
            if is_strict_name_match(merged_list[cand_idx]["name"], rec["name"]) or skey not in MULTI_CAMPUS_HOSTS:
                merged_idx = cand_idx

        if merged_idx is not None:
            merged_list[merged_idx] = merge_records(merged_list[merged_idx], rec)
            dups_merged += 1
        else:
            idx = len(merged_list)
            merged_list.append(rec)
            if skey:
                site_index[(skey, dist_group)] = idx

    print(f"Merged {dups_merged} duplicate college rows -> {len(merged_list)} unique institutions.")

    # Pass 3: Re-normalize merged phone fields & verify Instagram uniqueness
    for rec in merged_list:
        rec["college_phone"] = normalize_phone_list(rec.get("college_phone", ""), mobiles_only=False)
        rec["principal_phone"] = normalize_phone_list(rec.get("principal_phone", ""), mobiles_only=False)
        raw_mobs = ", ".join(filter(None, [rec.get("faculty_mobile", ""), rec.get("principal_phone", ""), rec.get("college_phone", "")]))
        rec["faculty_mobile"] = normalize_phone_list(raw_mobs, mobiles_only=True)

    # Sort priority: MMR enriched first, then Maharashtra enriched, then rest
    priority_order = {
        "Mumbai City": 0, "Mumbai Suburban": 1, "Thane": 2, "Raigad": 3, "Palghar": 4,
        "Pune": 5, "Nagpur": 6, "Nashik": 7, "Chhatrapati Sambhajinagar": 8, "Kolhapur": 9,
    }
    merged_list.sort(key=lambda r: (
        0 if (r["principal_name"] or r["faculty_mobile"] or r["college_phone"] or r["instagram_id"]) else 1,
        priority_order.get(r["district"], 99),
        r["district"],
        r["name"],
    ))
    for idx, rec in enumerate(merged_list, start=1):
        rec["sr_no"] = idx

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(merged_list, f, ensure_ascii=False, indent=2)

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
        for rec in merged_list:
            writer.writerow([rec.get(key, "") for key, _ in field_map])

    igs = [r["instagram_id"] for r in merged_list if r.get("instagram_id")]
    print("Instagram total:", len(igs), "| Unique:", len(set(igs)))
    print("Remaining dup IGs:", {k: v for k, v in Counter(igs).items() if v > 1})


if __name__ == "__main__":
    main()
