#!/usr/bin/env python3
"""
Upgrade Mumbai/MMR Degree, Junior, Law & Medical Colleges + Live Principal Refresh + Name Deduplication.
"""

import csv
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from audit_and_enrich_mmr import crawl_for_mmr_details
from build_database import (
    OUT_CSV,
    OUT_JSON,
    add_source,
    distinctive_tokens,
    norm_text,
    same_district_group,
)
from final_audit_clean import (
    BAD_IG_HANDLES,
    clean_principal_name,
    fix_pdf_wraps,
    merge_records,
    normalize_phone_list,
)

# Verified official websites for major Mumbai / MMR Degree, Junior, Law & Medical colleges
MMR_FLAGSHIP_SITES = [
    ("St. Xavier's College", "Mumbai City", "https://xaviers.edu/"),
    ("Jai Hind College", "Mumbai City", "https://jaihindcollege.com/"),
    ("Ramnarain Ruia", "Mumbai City", "https://www.ruiacollege.edu/"),
    ("Mithibai College", "Mumbai Suburban", "https://mithibai.ac.in/"),
    ("H.R. College of Commerce", "Mumbai City", "https://www.hrcollege.edu/"),
    ("Kishinchand Chellaram College", "Mumbai City", "https://kccollege.edu.in/"),
    ("R. A. Podar College", "Mumbai City", "https://www.rapodar.ac.in/"),
    ("D. G. Ruparel College", "Mumbai City", "https://www.ruparel.edu/"),
    ("Wilson College", "Mumbai City", "https://www.wilsoncollege.edu/"),
    ("Elphinstone College", "Mumbai City", "https://www.elphinstone.ac.in/"),
    ("Sathaye College", "Mumbai Suburban", "https://www.sathayecollege.edu.in/"),
    ("Patkar", "Mumbai Suburban", "https://patkarvardecollege.edu.in/"),
    ("Mulund College of Commerce", "Mumbai Suburban", "https://www.mccmulund.ac.in/"),
    ("Narsee Monjee College of Commerce", "Mumbai Suburban", "https://nmcollege.in/"),
    ("S.I.E.S. College of Arts, Science", "Mumbai City", "https://siesascs.edu.in/"),
    ("Vivekanand Education Society's College of Arts", "Mumbai Suburban", "https://main.ves.ac.in/vesasc/"),
    ("Thakur College of Science", "Mumbai Suburban", "https://www.tcsc.edu.in/"),
    ("Rizvi College of Arts, Science", "Mumbai Suburban", "https://www.rizvicollege.edu.in/"),
    ("V. G. Vaze College", "Mumbai Suburban", "http://vazecollege.net/"),
    ("Joshi Bedekar", "Thane", "https://joshibedekar.org/"),
    ("B. K. Birla College", "Thane", "https://bkbck.edu.in/"),
    ("Ramniranjan Jhunjhunwala College", "Mumbai Suburban", "https://www.rjcollege.edu.in/"),
    ("Bhavan's College", "Mumbai Suburban", "https://bhavans.ac.in/"),
    ("Guru Nanak Khalsa College", "Mumbai City", "https://gnkhalsa.edu.in/"),
    ("Sydenham College of Commerce", "Mumbai City", "https://www.sydenham.ac.in/"),
    ("Maharshi Dayanand College", "Mumbai City", "https://mdcollege.in/"),
    ("St. Andrew's College", "Mumbai Suburban", "https://standrewscollege.ac.in/"),
    ("R. D. National College", "Mumbai Suburban", "https://rdnational.ac.in/"),
    ("Nagindas Khandwala College", "Mumbai Suburban", "https://www.nkc.ac.in/"),
    ("Prahladrai Dalmia Lions College", "Mumbai Suburban", "https://dalmialionscollege.ac.in/"),
    ("M. L. Dahanukar College", "Mumbai Suburban", "https://www.mldcc.com/"),
    ("K. J. Somaiya College of Science and Commerce", "Mumbai Suburban", "https://kjssc.somaiya.edu/"),
    ("B. N. Bandodkar College of Science", "Thane", "https://bandodkarcollege.org/"),
    ("Smt. Chandibai Himathmal Mansukhani", "Thane", "https://www.chmcollege.in/"),
    ("K. V. Pendharkar College", "Thane", "https://www.kvpendharkarcollege.org/"),
    ("Government Law College", "Mumbai City", "https://www.glcmumbai.com/"),
    ("Seth G. S. Medical College", "Mumbai City", "https://www.kem.edu/"),
    ("Grant Government Medical College", "Mumbai City", "https://gmcjjh.edu.in/"),
    ("Lokmanya Tilak Municipal Medical College", "Mumbai City", "https://www.ltmgh.com/"),
    ("Topiwala National Medical College", "Mumbai City", "https://tnmcnair.edu.in/"),
]


def match_flagship(records: list[dict[str, Any]], query_name: str, dist: str) -> dict[str, Any] | None:
    q_low = query_name.lower()
    q_toks = distinctive_tokens(query_name)
    best = None
    best_score = 0
    for rec in records:
        if not same_district_group(rec["district"], dist):
            continue
        r_low = rec["name"].lower()
        if q_low in r_low:
            return rec
        r_toks = distinctive_tokens(rec["name"])
        if q_toks and r_toks:
            inter = len(q_toks & r_toks)
            if inter >= min(2, len(q_toks)) and inter > best_score:
                best = rec
                best_score = inter
    return best


def main() -> None:
    with open(OUT_JSON, encoding="utf-8") as f:
        records: list[dict[str, Any]] = json.load(f)

    print(f"Loaded {len(records)} records.")

    # 1. Attach verified flagship Mumbai/MMR websites
    newly_mapped = []
    for name_q, dist, url in MMR_FLAGSHIP_SITES:
        rec = match_flagship(records, name_q, dist)
        if rec:
            if not rec.get("website"):
                rec["website"] = url
                newly_mapped.append(rec)
            elif url not in rec["website"]:
                newly_mapped.append(rec)
            add_source(rec, "Verified Website")

    print(f"1. Mapped {len(newly_mapped)} flagship Mumbai/MMR Degree, Junior, Law & Medical websites.")

    # 2. Deep-crawl all flagship newly mapped + all non-JDTE-2025 websites to refresh stale Principals & get +91/IG
    to_crawl = [
        r for r in records
        if r.get("website") and (
            r in newly_mapped
            or ("JDTE Mumbai (2025)" not in r.get("verification_source", "") and (not r.get("principal_name") or not r.get("instagram_id") or not r.get("faculty_mobile")))
        )
    ]
    print(f"2. Deep-crawling {len(to_crawl)} official college websites (refreshing Principals, +91 mobiles, Instagram)...")
    ig_new = 0
    pr_new = 0
    mob_new = 0
    with ThreadPoolExecutor(max_workers=20) as pool:
        futs = {pool.submit(crawl_for_mmr_details, r["website"]): r for r in to_crawl}
        for fut in as_completed(futs):
            rec = futs[fut]
            try:
                info = fut.result()
                changed = False
                if info["instagram"] and not rec.get("instagram_id"):
                    ig = info["instagram"].lower()
                    if ig not in BAD_IG_HANDLES:
                        rec["instagram_id"] = ig
                        ig_new += 1
                        changed = True
                if info["principal"]:
                    cp = clean_principal_name(info["principal"])
                    if cp and (not rec.get("principal_name") or "JDTE Mumbai (2025)" not in rec.get("verification_source", "")):
                        if cp != rec.get("principal_name"):
                            rec["principal_name"] = cp
                            pr_new += 1
                            changed = True
                if info["phone"] and not rec.get("college_phone"):
                    rec["college_phone"] = info["phone"]
                    changed = True
                if info["email"] and not rec.get("email"):
                    rec["email"] = info["email"]
                    changed = True
                if info["mobiles"]:
                    raw = ", ".join(filter(None, [rec.get("faculty_mobile", "")] + info["mobiles"]))
                    new_mobs = normalize_phone_list(raw, mobiles_only=True)
                    if new_mobs != rec.get("faculty_mobile", ""):
                        rec["faculty_mobile"] = new_mobs
                        mob_new += 1
                        changed = True
                if changed:
                    add_source(rec, "Official Website")
            except Exception:
                pass
    print(f"   Crawl results -> +{ig_new} Instagram, +{pr_new} Principals refreshed/added, +{mob_new} +91 Mobiles.")

    # 3. Strict name-only deduplication within same district group
    print("3. Running strict name-based deduplication across all records...")
    deduped: list[dict[str, Any]] = []
    name_key_map: dict[tuple[str, str], int] = {}
    name_dups = 0
    for rec in records:
        rec["name"] = fix_pdf_wraps(rec["name"])
        rec["principal_name"] = clean_principal_name(rec.get("principal_name", ""))
        rec["college_phone"] = normalize_phone_list(rec.get("college_phone", ""), mobiles_only=False)
        rec["principal_phone"] = normalize_phone_list(rec.get("principal_phone", ""), mobiles_only=False)
        raw_mobs = ", ".join(filter(None, [rec.get("faculty_mobile", ""), rec.get("principal_phone", ""), rec.get("college_phone", "")]))
        rec["faculty_mobile"] = normalize_phone_list(raw_mobs, mobiles_only=True)

        dist_g = "mumbai" if "mumbai" in rec["district"].lower() else rec["district"].lower()
        nkey = re.sub(r"[^a-z0-9]", "", rec["name"].lower())
        if nkey and (nkey, dist_g) in name_key_map:
            idx = name_key_map[(nkey, dist_g)]
            deduped[idx] = merge_records(deduped[idx], rec)
            name_dups += 1
        else:
            idx = len(deduped)
            deduped.append(rec)
            if nkey:
                name_key_map[(nkey, dist_g)] = idx

    print(f"   Merged {name_dups} exact-name duplicates -> {len(deduped)} unique institutions.")

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

    with open(OUT_JSON, "w", encoding="utf-8") as f:
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

    print(f"Saved final {len(deduped)} records.")


if __name__ == "__main__":
    main()
