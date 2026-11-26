#!/usr/bin/env python3
"""
Maharashtra Colleges Database Builder (Strict Verification Edition)
Merges AISHE, University/Affiliation, DTE Maharashtra, and College Contact datasets
using strict distinctive-token matching to prevent false-positive merges.
"""

import csv
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
AISHE_PATH = Path("/tmp/aishe_institutions.json")
JACOB_PATH = Path("/tmp/jacobsamro_colleges.csv")
DTE_PATH = Path("/tmp/dte_institutes.csv")
BHOOMIKA_PATH = Path("/tmp/bhoomika_colleges.csv")

OUT_JSON = DATA_DIR / "maharashtra_colleges.json"
OUT_CSV = DATA_DIR / "maharashtra_colleges.csv"

DISTRICT_ALIASES = {
    "ahmadnagar": "Ahmednagar",
    "ahilyanagar": "Ahmednagar",
    "aurangabad": "Chhatrapati Sambhajinagar",
    "chhatrapati sambhajinagar": "Chhatrapati Sambhajinagar",
    "osmanabad": "Dharashiv",
    "dharashiv": "Dharashiv",
    "mumbai": "Mumbai City",
    "mumbai city": "Mumbai City",
    "mumbai suburban": "Mumbai Suburban",
    "suburban mumbai": "Mumbai Suburban",
    "raigarh": "Raigad",
    "raigad": "Raigad",
    "buldana": "Buldhana",
    "buldhana": "Buldhana",
    "gondiya": "Gondia",
    "gondia": "Gondia",
    "bid": "Beed",
    "beed": "Beed",
}

GENERIC_WORDS = {
    "of", "and", "the", "for", "in", "at", "s", "shri", "smt", "late", "dr",
    "college", "institute", "institution", "technology", "engineering", "management",
    "education", "educational", "society", "trust", "mandal", "sanstha", "samiti",
    "mahavidyalaya", "vidyalaya", "school", "junior", "senior", "degree",
    "arts", "science", "commerce", "law", "pharmacy", "medical", "polytechnic",
    "research", "centre", "center", "campus", "group", "institutions",
    "maharashtra", "mumbai", "pune", "nagpur", "nashik", "thane", "aurangabad",
    "kolhapur", "solapur", "amravati", "sangli", "satara", "jalgaon", "nanded",
    "latur", "akola", "ahmednagar", "raigad", "palghar", "navi",
}

INVALID_IG_HANDLES = {
    "p", "reel", "reels", "explore", "accounts", "stories", "tv", "share",
    "sharer", "intent", "hashtag", "direct", "about", "developer", "legal",
    "privacy", "terms", "blog", "directory", "yourprofile", "yourusername",
    "username", "user", "instagram", "official", "example", "handle", "test",
    "demo", "college", "school", "profile",
}


def norm_text(val: Any) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    s = str(val).strip()
    if s.lower() in {"nan", "none", "null", "na", "n/a", "-", "--", "ext.-"}:
        return ""
    return re.sub(r"\s+", " ", s)


def norm_district(d: str) -> str:
    d = norm_text(d)
    if not d:
        return ""
    key = d.lower()
    return DISTRICT_ALIASES.get(key, d.title() if d.isupper() else d)


def norm_name_key(name: str) -> str:
    s = name.lower()
    s = re.sub(r"\(id:\s*[cusrd]-\d+\)", "", s)
    s = re.sub(r"address:.*$", "", s)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    stop = {"of", "and", "the", "for", "in", "at", "s"}
    return " ".join(t for t in s.split() if t not in stop)


def distinctive_tokens(name: str) -> set[str]:
    s = norm_name_key(name)
    return {t for t in s.split() if len(t) >= 2 and t not in GENERIC_WORDS}


def is_strict_name_match(name_a: str, name_b: str) -> bool:
    ka, kb = norm_name_key(name_a), norm_name_key(name_b)
    if not ka or not kb:
        return False
    if ka == kb:
        return True
    da, db = distinctive_tokens(name_a), distinctive_tokens(name_b)
    if len(da) < 2 or len(db) < 2:
        return False
    inter = da & db
    union = da | db
    jaccard = len(inter) / len(union)
    return len(inter) >= 2 and jaccard >= 0.65


def same_district_group(d1: str, d2: str) -> bool:
    d1, d2 = d1.lower(), d2.lower()
    if d1 == d2:
        return True
    mumbai_set = {"mumbai city", "mumbai suburban", "mumbai"}
    return d1 in mumbai_set and d2 in mumbai_set


def clean_phone(phone: str, std_code: str = "") -> str:
    p = norm_text(phone)
    if not p or p in {"Ext.-", "Ext.- ", "0", "-"}:
        return ""
    p = re.sub(r"\s*Ext\.-\s*$", "", p).strip()
    if not p or p in {"0", "-"}:
        return ""
    std = norm_text(std_code)
    if std and std.isdigit() and not p.startswith("0") and len(re.sub(r"\D", "", p)) <= 8:
        p = f"{std}-{p}"
    return p


def clean_website(url: str) -> str:
    u = norm_text(url)
    if not u or u.lower() in {"http://", "https://", "www.", "nil", "no"}:
        return ""
    if not u.startswith(("http://", "https://")):
        u = "https://" + u
    return u


def clean_instagram(handle: str) -> str:
    h = norm_text(handle).lstrip("@").strip("/").lower()
    if not h or h in INVALID_IG_HANDLES or len(h) < 3:
        return ""
    if h.endswith((".js", ".css", ".png", ".jpg", ".svg")):
        return ""
    return "@" + h


def classify_category(name: str, aishe_code: str = "") -> str:
    n = name.lower()
    if aishe_code.startswith("U-") or ("university" in n and "college" not in n and "institute" not in n):
        return "University"
    if any(k in n for k in ["junior college", "jr. college", "jr college", "higher secondary", "11th", "hsc"]):
        return "Junior College"
    if any(k in n for k in ["engineering", "polytechnic", "architecture", "institute of technology", "coe ", "college of tech", "ict "]):
        return "Engineering, Polytechnic & Architecture"
    if any(k in n for k in ["medical", "dental", "pharmacy", "pharmaceutical", "ayurved", "homoeopath", "homeopath", "nursing", "physiotherapy", "unani", "health science"]):
        return "Medical, Dental & Pharmacy"
    if any(k in n for k in ["management", "mba", "mms", "business school", "law college", "college of law", "legal"]):
        return "Management & Law"
    if any(k in n for k in ["b.ed", "d.ed", "education", "teacher", "shikshan", "adhyapak", "physical education"]):
        return "Education & Training"
    if any(k in n for k in ["agriculture", "veterinary", "fisheries", "horticulture", "forestry"]):
        return "Agriculture & Allied"
    return "Degree College (Arts / Science / Commerce)"


def infer_management(name: str, college_type: str = "") -> str:
    n = name.lower()
    if "autonomous" in n:
        return "Autonomous"
    if any(k in n for k in ["government", "govt.", "govt ", "national institute", "indian institute", "iit ", "vnit"]):
        return "Government"
    if "deemed" in n or "university" in college_type.lower():
        return "University / Constituent"
    return norm_text(college_type) or "Affiliated / Private / Aided"


def extract_city_from_name_or_addr(name: str, address: str, district: str) -> str:
    if "," in name:
        tail = norm_text(name.split(",")[-1])
        if 2 <= len(tail) <= 35 and not any(w in tail.lower() for w in ["college", "institute", "mahavidyalaya", "trust", "society"]):
            return tail
    if address:
        parts = [norm_text(p) for p in address.split(",") if norm_text(p)]
        for p in reversed(parts):
            p_clean = re.sub(r"\b\d{6}\b", "", p).strip(" -")
            if 2 <= len(p_clean) <= 30 and "maharashtra" not in p_clean.lower():
                return p_clean
    return district


def add_source(rec: dict[str, Any], source_label: str) -> None:
    existing = [s.strip() for s in rec.get("verification_source", "").split("+") if s.strip()]
    if source_label not in existing:
        existing.append(source_label)
    rec["verification_source"] = " + ".join(existing)


def find_strict_match(name: str, dist: str, records_by_code: dict[str, dict[str, Any]], exact_index: dict[tuple[str, str], str]) -> str | None:
    nk = norm_name_key(name)
    if (nk, dist.lower()) in exact_index:
        return exact_index[(nk, dist.lower())]
    for k, rec in records_by_code.items():
        if same_district_group(rec["district"], dist) and is_strict_name_match(rec["name"], name):
            return k
    return None


def main() -> None:
    print("1. Loading AISHE institutions...")
    with open(AISHE_PATH, encoding="utf-8") as f:
        aishe_raw = json.load(f)

    records_by_code: dict[str, dict[str, Any]] = {}
    exact_index: dict[tuple[str, str], str] = {}

    for item in aishe_raw:
        if norm_text(item.get("state")).lower() != "maharashtra":
            continue
        code = norm_text(item.get("aishe_code"))
        name = norm_text(item.get("name"))
        dist = norm_district(item.get("district", ""))
        if not name:
            continue
        rec = {
            "aishe_code": code,
            "name": name,
            "principal_name": "",
            "college_phone": "",
            "principal_phone": "",
            "instagram_id": "",
            "district": dist,
            "city": extract_city_from_name_or_addr(name, "", dist),
            "category": classify_category(name, code),
            "affiliation": "",
            "management_type": infer_management(name),
            "email": "",
            "website": "",
            "address": "",
            "verification_source": "AISHE",
        }
        key = code or f"NO_CODE_{len(records_by_code)}"
        records_by_code[key] = rec
        exact_index[(norm_name_key(name), dist.lower())] = key

    print(f"   Loaded {len(records_by_code)} Maharashtra AISHE institutions.")

    print("2. Merging University Affiliation from JacobSamro AISHE dataset...")
    j_df = pd.read_csv(JACOB_PATH, header=None, encoding="latin1", on_bad_lines="skip")
    j_mh = j_df[j_df[4].astype(str).str.strip().str.lower() == "maharashtra"]
    matched_j = 0
    for _, row in j_mh.iterrows():
        univ = re.sub(r"\s*\(Id:\s*U-\d+\)", "", norm_text(row[1])).strip()
        cname_raw = norm_text(row[2])
        m_code = re.search(r"\(Id:\s*([CUSR]-\d+)\)", cname_raw)
        cname = re.sub(r"\s*\(Id:\s*[CUSR]-\d+\)", "", cname_raw).strip()
        ctype = norm_text(row[3])
        dist = norm_district(row[5])

        target_key = None
        if m_code and m_code.group(1) in records_by_code:
            target_key = m_code.group(1)
        elif (norm_name_key(cname), dist.lower()) in exact_index:
            target_key = exact_index[(norm_name_key(cname), dist.lower())]

        if target_key:
            matched_j += 1
            rec = records_by_code[target_key]
            if univ and not rec["affiliation"]:
                rec["affiliation"] = univ
            if ctype:
                rec["management_type"] = infer_management(rec["name"], ctype)
        else:
            code = m_code.group(1) if m_code else f"J_{len(records_by_code)}"
            rec = {
                "aishe_code": code if m_code else "",
                "name": cname,
                "principal_name": "",
                "college_phone": "",
                "principal_phone": "",
                "instagram_id": "",
                "district": dist,
                "city": extract_city_from_name_or_addr(cname, "", dist),
                "category": classify_category(cname, code),
                "affiliation": univ,
                "management_type": infer_management(cname, ctype),
                "email": "",
                "website": "",
                "address": "",
                "verification_source": "AISHE University List",
            }
            records_by_code[code] = rec
            exact_index[(norm_name_key(cname), dist.lower())] = code
    print(f"   Matched {matched_j} records; total now {len(records_by_code)}.")

    print("3. Merging DTE Maharashtra (strict matching)...")
    dte_df = pd.read_csv(DTE_PATH, encoding="latin1", on_bad_lines="skip")
    matched_dte = 0
    added_dte = 0
    for _, row in dte_df.iterrows():
        name = norm_text(row.get("Institute Name"))
        dist = norm_district(row.get("District", ""))
        taluka = norm_text(row.get("Taluka", ""))
        addr = norm_text(row.get("Address", ""))
        pin = norm_text(row.get("Pincode", "")).replace(".0", "")
        full_addr = f"{addr}, {dist} - {pin}".strip(" ,-") if pin else addr
        std = norm_text(row.get("Std Code", "")).replace(".0", "")
        web = clean_website(row.get("Website", ""))
        email = norm_text(row.get("Email", "")).lower()
        head = norm_text(row.get("Head Name", ""))
        off_ph = clean_phone(row.get("Office Number", ""), std)
        per_ph = clean_phone(row.get("Personal Number", ""), std)

        target_key = find_strict_match(name, dist, records_by_code, exact_index)
        if target_key:
            matched_dte += 1
            rec = records_by_code[target_key]
        else:
            added_dte += 1
            target_key = f"DTE_{len(records_by_code)}"
            rec = {
                "aishe_code": "",
                "name": name,
                "principal_name": "",
                "college_phone": "",
                "principal_phone": "",
                "instagram_id": "",
                "district": dist,
                "city": taluka or extract_city_from_name_or_addr(name, addr, dist),
                "category": classify_category(name),
                "affiliation": "DTE Maharashtra",
                "management_type": infer_management(name),
                "email": "",
                "website": "",
                "address": "",
                "verification_source": "",
            }
            records_by_code[target_key] = rec
            exact_index[(norm_name_key(name), dist.lower())] = target_key

        add_source(rec, "DTE Maharashtra")
        if head and not rec["principal_name"]:
            rec["principal_name"] = head
        if off_ph and not rec["college_phone"]:
            rec["college_phone"] = off_ph
        if per_ph and not rec["principal_phone"]:
            rec["principal_phone"] = per_ph
        if email and not rec["email"]:
            rec["email"] = email
        if web and not rec["website"]:
            rec["website"] = web
        if full_addr and not rec["address"]:
            rec["address"] = full_addr
        if taluka:
            rec["city"] = taluka
    print(f"   Strict-matched {matched_dte} DTE records, added {added_dte} new; total {len(records_by_code)}.")

    print("4. Merging Bhoomika Maharashtra College contacts (strict matching)...")
    b_df = pd.read_csv(BHOOMIKA_PATH, encoding="latin1", on_bad_lines="skip")
    b_mh = b_df[b_df["STATE"].astype(str).str.strip().str.lower() == "maharashtra"]
    matched_b = 0
    for _, row in b_mh.iterrows():
        name = norm_text(row.get("COLLEGE_NAME"))
        dist = norm_district(row.get("DISTRICT", ""))
        addr = norm_text(row.get("ADDRESS", "")).replace("|", ",")
        ph = clean_phone(row.get("OFFICE_NUMBER", ""))
        email = norm_text(row.get("EMAIl", "")).lower()
        web = clean_website(row.get("WEBSITE_LINK", ""))
        if not name or name.lower().startswith("campus"):
            continue
        target_key = find_strict_match(name, dist, records_by_code, exact_index)
        if target_key:
            matched_b += 1
            rec = records_by_code[target_key]
            add_source(rec, "College Directory")
            if ph and not rec["college_phone"]:
                rec["college_phone"] = ph
            if email and not rec["email"]:
                rec["email"] = email
            if web and not rec["website"]:
                rec["website"] = web
            if addr and not rec["address"]:
                rec["address"] = addr
    print(f"   Strict-matched {matched_b} Bhoomika records.")

    priority_districts = {"Mumbai City": 0, "Mumbai Suburban": 1, "Thane": 2, "Pune": 3, "Nagpur": 4, "Nashik": 5}
    all_records = sorted(
        records_by_code.values(),
        key=lambda r: (
            0 if (r["principal_name"] or r["college_phone"] or r["instagram_id"]) else 1,
            priority_districts.get(r["district"], 99),
            r["district"],
            r["name"],
        ),
    )
    for idx, rec in enumerate(all_records, start=1):
        rec["sr_no"] = idx

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"Saved clean base dataset: {len(all_records)} records -> {OUT_JSON.name}")


if __name__ == "__main__":
    main()
