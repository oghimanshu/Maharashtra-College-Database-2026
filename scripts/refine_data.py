#!/usr/bin/env python3
"""
Data Refinement Pass:
1. Smart Title-Case normalization for ALL-CAPS college names and Principal names,
   preserving academic/institutional acronyms (VJTI, SIES, NMIMS, IIT, GLC, etc.).
2. Re-tag non-college research labs, hospitals, and regulatory boards into
   'Research & Hospitals' so college categories stay clean.
3. Extract real Suburb / Locality / Taluka into 'City / Area' from names & addresses.
"""

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IN_JSON = DATA_DIR / "maharashtra_colleges.json"
OUT_CSV = DATA_DIR / "maharashtra_colleges.csv"

KEEP_UPPER = {
    "VJTI", "SIES", "NMIMS", "IIT", "NIT", "VNIT", "ICT", "GLC", "DJ", "KJ", "KC",
    "HR", "NM", "RA", "DG", "VG", "BN", "KV", "CHM", "MES", "VES", "VESASC", "AI",
    "MIT", "COEP", "SPIT", "SPCE", "DBIT", "FCRIT", "SAKEC", "TCET", "VCET", "TSEC",
    "RAIT", "PCE", "PIIT", "DMCE", "APSIT", "SLRTCE", "DTE", "AICTE", "UGC", "HSC",
    "MBA", "MMS", "MCA", "LLB", "LLM", "PHD", "PG", "UG", "I/C", "II", "III", "IV",
    "VI", "VII", "VIII", "IX", "X", "TCSC", "NKC", "MCC", "RJ", "MD", "RD", "SH",
    "SNDT", "MUHS", "SPPU", "BAMU", "SRTMU", "SGBAU", "RTMNU", "DBATU", "ICMR",
    "ICAR", "BARC", "TIFR", "IIPS", "TISS", "IGIDR", "NITIE", "IIM", "IIIT", "DY",
    "MGM", "BV", "SVKM", "KJSCE", "KJSSC", "KJSIEIT", "SIMSREE", "JBIMS", "LTMMC",
    "TNMC", "KEM", "JJ", "BYL", "GSMC", "MH", "MMR", "IT", "CS", "AI'S", "DR",
}

LOWER_WORDS = {"of", "and", "for", "in", "at", "to", "the", "on", "by", "with", "from", "de"}

NON_COLLEGE_KEYWORDS = [
    "hospital", "research centre", "research center", "research institute",
    "research laboratory", "laboratory", "regulatory board", "atomic energy",
    "cancer institute", "forensic science", "haffkine", "icmr", "icar",
    "blood bank", "medical centre", "medical center",
]

TEACHING_ALLOWLIST = [
    "college", "university", "vidyalaya", "mahavidyalaya", "polytechnic",
    "institute of technology", "institute of management", "school of nursing",
    "school of", "academy", "shikshan", "shiksha",
]

LOCALITIES = [
    # Mumbai City & South/Central
    "Colaba", "Nariman Point", "Churchgate", "Cuffe Parade", "Fort", "Marine Lines",
    "Kalbadevi", "Girgaon", "Charni Road", "Grant Road", "Tardeo", "Malabar Hill",
    "Mumbai Central", "Byculla", "Mazgaon", "Worli", "Prabhadevi", "Lower Parel",
    "Parel", "Sewri", "Dadar", "Matunga", "Sion", "Wadala", "Mahim", "Dharavi",
    # Mumbai Western Suburbs
    "Bandra", "Khar", "Santacruz", "Vile Parle", "Andheri", "Jogeshwari",
    "Goregaon", "Malad", "Kandivali", "Borivali", "Dahisar", "Versova", "Juhu",
    # Mumbai Eastern Suburbs
    "Kurla", "Vidyavihar", "Ghatkopar", "Vikhroli", "Kanjurmarg", "Bhandup",
    "Mulund", "Chembur", "Trombay", "Govandi", "Mankhurd", "Powai", "Chandivali",
    # Navi Mumbai & Thane & Palghar & Raigad
    "Vashi", "Nerul", "Belapur", "CBD Belapur", "Kharghar", "Kamothe", "Panvel",
    "Kalamboli", "Airoli", "Ghansoli", "Koparkhairane", "Kopar Khairane", "Sanpada",
    "Turbhe", "Seawoods", "Ulwe", "Taloja", "Thane", "Mira Road", "Bhayandar",
    "Vasai", "Virar", "Nallasopara", "Palghar", "Boisar", "Dahanu", "Wada",
    "Kalyan", "Dombivli", "Ulhasnagar", "Ambernath", "Badlapur", "Bhiwandi",
    "Shahapur", "Murbad", "Karjat", "Alibag", "Pen", "Roha", "Lonere", "Khopoli",
    "Mahad", "Mangaon", "Uran", "Rasayani",
    # Pune & Rest of Maharashtra
    "Kothrud", "Shivajinagar", "Deccan", "Hinjewadi", "Wakad", "Pimpri", "Chinchwad",
    "Akurdi", "Alandi", "Baramati", "Lonavala", "Talegaon", "Hadapsar", "Katraj",
    "Kondhwa", "Viman Nagar", "Kharadi", "Baner", "Aundh", "Warje", "Bavdhan",
    "Chakan", "Junnar", "Indapur", "Daund", "Shirur", "Saswad", "Bhor",
    "Karad", "Miraj", "Ichalkaranji", "Pandharpur", "Malegaon", "Igatpuri",
    "Sinnar", "Kamptee", "Shegaon", "Bhusawal", "Shirdi", "Sangamner", "Kopargaon",
    "Chiplun", "Kudal", "Sawantwadi", "Shrirampur", "Rahuri", "Barshi",
]

# Precompile locality regexes (longest first so 'CBD Belapur' beats 'Belapur')
LOCALITY_PATTERNS = [
    (loc, re.compile(rf"\b{re.escape(loc)}\b", re.I))
    for loc in sorted(LOCALITIES, key=len, reverse=True)
]


def smart_title_case(s: str) -> str:
    if not s:
        return ""
    # Only transform if predominantly uppercase (avoid breaking already-clean mixed-case names)
    letters = [c for c in s if c.isalpha()]
    if not letters or sum(1 for c in letters if c.isupper()) / len(letters) < 0.72:
        return s

    words = s.split(" ")
    out = []
    for i, w in enumerate(words):
        if not w:
            continue
        clean_w = re.sub(r"[^A-Za-z0-9/']", "", w).upper()
        if clean_w in KEEP_UPPER:
            out.append(w.upper())
        elif re.fullmatch(r"(?:[A-Z]\.){2,}[A-Z]?\.?", w.upper()):
            out.append(w.upper())
        elif i > 0 and w.lower() in LOWER_WORDS:
            out.append(w.lower())
        elif "-" in w:
            parts = [p.upper() if p.upper() in KEEP_UPPER else p.capitalize() for p in w.split("-")]
            out.append("-".join(parts))
        else:
            out.append(w.capitalize())
    return " ".join(out)


def is_non_college(rec: dict[str, Any]) -> bool:
    n = rec["name"].lower()
    if any(allow in n for allow in TEACHING_ALLOWLIST):
        return False
    return any(kw in n for kw in NON_COLLEGE_KEYWORDS)


def detect_locality(rec: dict[str, Any]) -> str:
    cur_city = rec.get("city", "").strip()
    dist = rec.get("district", "").strip()
    if cur_city and cur_city.lower() != dist.lower() and "mumbai" not in cur_city.lower():
        return smart_title_case(cur_city)

    haystack = f"{rec.get('name', '')} {rec.get('address', '')}"
    for loc, pat in LOCALITY_PATTERNS:
        if pat.search(haystack):
            # Normalize Koparkhairane spelling
            if loc.lower() in {"koparkhairane", "kopar khairane"}:
                return "Kopar Khairane"
            return loc
    return smart_title_case(cur_city) if cur_city else dist


def main() -> None:
    with open(IN_JSON, encoding="utf-8") as f:
        records: list[dict[str, Any]] = json.load(f)

    title_fixed = 0
    retagged = 0
    loc_improved = 0

    for rec in records:
        old_name = rec["name"]
        new_name = smart_title_case(old_name)
        if new_name != old_name:
            rec["name"] = new_name
            title_fixed += 1

        if rec.get("principal_name"):
            rec["principal_name"] = smart_title_case(rec["principal_name"])
        if rec.get("address"):
            rec["address"] = smart_title_case(rec["address"])

        if is_non_college(rec) and rec.get("category") != "Research & Hospitals":
            rec["category"] = "Research & Hospitals"
            retagged += 1

        old_city = rec.get("city", "")
        new_city = detect_locality(rec)
        if new_city and new_city != old_city:
            rec["city"] = new_city
            loc_improved += 1

    with open(IN_JSON, "w", encoding="utf-8") as f:
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

    print(f"Title-cased {title_fixed} ALL-CAPS names.")
    print(f"Re-tagged {retagged} non-college labs/hospitals -> 'Research & Hospitals'.")
    print(f"Refined {loc_improved} City / Area localities.")
    print("Categories:", Counter(r["category"] for r in records))


if __name__ == "__main__":
    main()
