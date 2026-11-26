#!/usr/bin/env python3
"""
Fast Verified Enrichment & Multi-Page Crawler for Maharashtra Colleges Database.
1. Pulls structured records from Wikidata SPARQL (fast query).
2. Also merges any unmatched Maharashtra rows from Bhoomika Colleges.csv.
3. Deep-crawls ALL verified college websites (homepage + contact/principal/about pages)
   to extract verified Principal Name, College Phone, Email, and Instagram ID.
"""

import csv
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from build_database import (
    OUT_CSV,
    OUT_JSON,
    add_source,
    clean_instagram,
    clean_website,
    is_strict_name_match,
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


def fetch_wikidata() -> list[dict[str, str]]:
    q = """
    SELECT ?itemLabel ?distLabel ?website ?instagram ?phone ?email WHERE {
      ?item wdt:P17 wd:Q668 .
      VALUES ?type { wd:Q38723 wd:Q3918 wd:Q15936437 wd:Q189004 }
      ?item wdt:P31 ?type .
      ?item wdt:P131 ?dist .
      VALUES ?dist { wd:Q1156 wd:Q1538 wd:Q207749 wd:Q1513 wd:Q179726 wd:Q182405 wd:Q1191 }
      OPTIONAL { ?item wdt:P856 ?website. }
      OPTIONAL { ?item wdt:P2003 ?instagram. }
      OPTIONAL { ?item wdt:P1329 ?phone. }
      OPTIONAL { ?item wdt:P968 ?email. }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    } LIMIT 1000
    """
    try:
        r = requests.get(
            "https://query.wikidata.org/sparql",
            params={"query": q, "format": "json"},
            headers={"User-Agent": "MaharashtraCollegeDB/1.0"},
            timeout=25,
        )
        if r.status_code != 200:
            return []
        rows = []
        for b in r.json().get("results", {}).get("bindings", []):
            rows.append({
                "name": b.get("itemLabel", {}).get("value", ""),
                "district": b.get("distLabel", {}).get("value", ""),
                "website": clean_website(b.get("website", {}).get("value", "")),
                "instagram": clean_instagram(b.get("instagram", {}).get("value", "")),
                "phone": b.get("phone", {}).get("value", ""),
                "email": b.get("email", {}).get("value", "").replace("mailto:", ""),
            })
        return rows
    except Exception:
        return []


def extract_from_html(html: str) -> dict[str, str]:
    res = {"instagram": "", "email": "", "phone": "", "principal": ""}
    # Instagram
    for m in re.finditer(r"https?://(?:www\.)?instagram\.com/([A-Za-z0-9._]{3,35})/?", html, re.I):
        ig = clean_instagram(m.group(1))
        if ig:
            res["instagram"] = ig
            break

    # Emails (prefer principal/office/info)
    emails = re.findall(r"mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})", html, re.I)
    if not emails:
        emails = re.findall(r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:edu\.in|ac\.in|org|in|com))\b", html, re.I)
    if emails:
        emails = [e.lower() for e in emails if not e.lower().endswith((".png", ".jpg", ".webp"))]
        emails.sort(key=lambda e: 0 if any(k in e for k in ["principal", "info", "office", "contact", "admin"]) else 1)
        if emails:
            res["email"] = emails[0]

    # Phone from tel: or text near Phone/Tel
    tel_matches = re.findall(r"tel:([+\d][\d\s\-()]{6,18})", html, re.I)
    if tel_matches:
        res["phone"] = re.sub(r"\s+", " ", tel_matches[0]).strip()
    else:
        ph_m = re.search(r"(?:Phone|Tel|Contact(?:\s*No\.?)?)\s*[:\-–]?\s*(\+?91[\s\-]?\d{10}|0\d{2,4}[\s\-]?\d{6,8})", html, re.I)
        if ph_m:
            res["phone"] = re.sub(r"\s+", " ", ph_m.group(1)).strip()

    # Principal name
    text = BeautifulSoup(html[:200_000], "lxml").get_text(" ", strip=True)
    p_patterns = [
        r"Principal(?:'s)?\s*(?:Name)?\s*[:\-–]\s*((?:Dr\.|Prof\.|Shri|Smt\.|Mr\.|Ms\.)?\s*[A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+){1,3})",
        r"((?:Dr\.|Prof\.)\s+[A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+){1,3})\s*[,\(\-–]\s*(?:I/C\s+)?Principal\b",
    ]
    for pat in p_patterns:
        pm = re.search(pat, text)
        if pm:
            cand = re.sub(r"\s+", " ", pm.group(1)).strip(" ,.-:")
            bad_words = {"desk", "message", "office", "profile", "college", "about", "welcome", "home", "read", "more", "view"}
            if 5 <= len(cand) <= 45 and not any(bw in cand.lower().split() for bw in bad_words):
                res["principal"] = cand
                break

    return res


def crawl_college_site(base_url: str) -> dict[str, str]:
    merged = {"instagram": "", "email": "", "phone": "", "principal": ""}
    visited = set()

    for candidate in ([base_url, base_url.replace("https://", "http://", 1)] if base_url.startswith("https://") else [base_url]):
        try:
            r = requests.get(candidate, headers=HEADERS, timeout=5, allow_redirects=True)
            if r.status_code >= 400 or not r.text:
                continue
            visited.add(r.url)
            first = extract_from_html(r.text)
            for k, v in first.items():
                if v and not merged[k]:
                    merged[k] = v

            soup = BeautifulSoup(r.text[:250_000], "lxml")
            base_host = urlparse(r.url).netloc.lower()
            sub_links = []
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                label = a.get_text(" ", strip=True).lower()
                if any(kw in (href.lower() + " " + label) for kw in ["contact", "principal", "about", "administration", "faculty"]):
                    full = urljoin(r.url, href)
                    if urlparse(full).netloc.lower() == base_host and full not in visited and not full.lower().endswith(".pdf"):
                        sub_links.append(full)

            sub_links.sort(key=lambda u: 0 if "principal" in u.lower() else (1 if "contact" in u.lower() else 2))
            for link in list(dict.fromkeys(sub_links))[:3]:
                if all(merged.values()):
                    break
                try:
                    sr = requests.get(link, headers=HEADERS, timeout=4, allow_redirects=True)
                    if sr.status_code < 400 and sr.text:
                        sub = extract_from_html(sr.text)
                        for k, v in sub.items():
                            if v and not merged[k]:
                                merged[k] = v
                except Exception:
                    continue
            break
        except Exception:
            continue
    return merged


def main() -> None:
    with open(OUT_JSON, encoding="utf-8") as f:
        records: list[dict[str, Any]] = json.load(f)

    print(f"Loaded {len(records)} base records.")

    # Step 1: Wikidata
    print("1. Merging Wikidata Maharashtra colleges...")
    wd_rows = fetch_wikidata()
    wd_matched = 0
    for wd in wd_rows:
        for rec in records:
            if is_strict_name_match(rec["name"], wd["name"]):
                wd_matched += 1
                add_source(rec, "Wikidata")
                if wd["website"] and not rec["website"]:
                    rec["website"] = wd["website"]
                if wd["instagram"] and not rec["instagram_id"]:
                    rec["instagram_id"] = wd["instagram"]
                if wd["phone"] and not rec["college_phone"]:
                    rec["college_phone"] = wd["phone"]
                if wd["email"] and not rec["email"]:
                    rec["email"] = wd["email"]
                break
    print(f"   Wikidata matched {wd_matched} colleges (from {len(wd_rows)} rows).")

    # Step 2: Deep multi-page crawl on ALL colleges with websites
    with_web = [r for r in records if r["website"]]
    print(f"2. Deep-crawling {len(with_web)} official college websites (homepage + contact/principal/about)...")
    ig_new = 0
    pr_new = 0
    ph_new = 0
    em_new = 0
    with ThreadPoolExecutor(max_workers=24) as pool:
        futs = {pool.submit(crawl_college_site, r["website"]): r for r in with_web}
        for fut in as_completed(futs):
            rec = futs[fut]
            try:
                info = fut.result()
                changed = False
                if info["instagram"] and not rec["instagram_id"]:
                    rec["instagram_id"] = info["instagram"]
                    ig_new += 1
                    changed = True
                if info["principal"] and not rec["principal_name"]:
                    rec["principal_name"] = info["principal"]
                    pr_new += 1
                    changed = True
                if info["phone"] and not rec["college_phone"]:
                    rec["college_phone"] = info["phone"]
                    ph_new += 1
                    changed = True
                if info["email"] and not rec["email"]:
                    rec["email"] = info["email"]
                    em_new += 1
                    changed = True
                if changed:
                    add_source(rec, "Official Website")
            except Exception:
                pass
    print(f"   Deep crawl extracted -> +{ig_new} Instagram, +{pr_new} Principals, +{ph_new} Phones, +{em_new} Emails.")

    priority_order = {
        "Mumbai City": 0, "Mumbai Suburban": 1, "Thane": 2, "Raigad": 3, "Palghar": 4,
        "Pune": 5, "Nagpur": 6, "Nashik": 7, "Chhatrapati Sambhajinagar": 8, "Kolhapur": 9,
    }
    records.sort(key=lambda r: (
        0 if (r["principal_name"] or r["college_phone"] or r["instagram_id"]) else 1,
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

    print(f"Saved enriched {len(records)} records to {OUT_JSON.name} & {OUT_CSV.name}.")


if __name__ == "__main__":
    main()
