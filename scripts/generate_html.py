#!/usr/bin/env python3
"""
Generate a polished, self-contained GitHub Pages web app (docs/index.html) with:
- Light & Dark mode toggle (persisted in localStorage)
- Hero header with live stats, dynamic GitHub Excel link & Export Filtered CSV
- Typo-tolerant fuzzy search across all 17 fields ('/' shortcut + shareable URLs)
- Quick MMR / Region pills, District & Category dropdowns, and Contact chips
- Star / Shortlist bookmarks (persisted in localStorage) + WhatsApp direct chat links
- Collapsible live Analytics Strip (Top Districts & Categories for current results)
- Table View & Card Grid View toggle
- Slide-over Detail Drawer with Prev/Next ('←'/'→') navigation & one-click Copy
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
IN_JSON = BASE_DIR / "data" / "maharashtra_colleges.json"
OUT_HTML = BASE_DIR / "docs" / "index.html"

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Maharashtra College Database (2026) — Fuzzy Search Directory</title>
<meta name="description" content="Search 10,448 colleges across Mumbai, MMR, and Maharashtra with Principal names, +91 mobile numbers, Instagram IDs, websites, and affiliations." />
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎓</text></svg>" />
<style>
  :root {
    --bg: #f8fafc;
    --surface: #ffffff;
    --surface-2: #f1f5f9;
    --border: #e2e8f0;
    --text: #0f172a;
    --muted: #64748b;
    --accent: #2563eb;
    --accent-soft: rgba(37, 99, 235, 0.1);
    --accent-2: #4f46e5;
    --green: #059669;
    --green-soft: rgba(5, 150, 105, 0.12);
    --pink: #db2777;
    --pink-soft: rgba(219, 39, 119, 0.1);
    --amber: #d97706;
    --amber-soft: rgba(217, 119, 6, 0.12);
    --shadow: 0 1px 3px rgba(15, 23, 42, 0.06), 0 4px 16px rgba(15, 23, 42, 0.04);
    --shadow-lg: 0 12px 40px rgba(15, 23, 42, 0.14);
    --mark-bg: #fef08a;
    --mark-text: #0f172a;
  }
  [data-theme="dark"] {
    --bg: #0b1120;
    --surface: #131c31;
    --surface-2: #1c2842;
    --border: #263554;
    --text: #f1f5f9;
    --muted: #94a3b8;
    --accent: #38bdf8;
    --accent-soft: rgba(56, 189, 248, 0.14);
    --accent-2: #818cf8;
    --green: #34d399;
    --green-soft: rgba(52, 211, 153, 0.14);
    --pink: #f472b6;
    --pink-soft: rgba(244, 114, 182, 0.14);
    --amber: #fbbf24;
    --amber-soft: rgba(251, 191, 36, 0.14);
    --shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
    --shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.6);
    --mark-bg: rgba(56, 189, 248, 0.28);
    --mark-text: #ffffff;
  }

  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.5;
    transition: background .2s ease, color .2s ease;
  }

  .hero {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.09), rgba(79, 70, 229, 0.06), transparent);
    border-bottom: 1px solid var(--border);
    padding: 22px 0 18px;
  }
  .container { max-width: 1420px; margin: 0 auto; padding: 0 20px; }

  .hero-top {
    display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 16px;
  }
  .brand { display: flex; align-items: center; gap: 12px; }
  .logo-box {
    width: 44px; height: 44px; border-radius: 12px;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    display: grid; place-items: center; font-size: 1.35rem; color: #fff;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.25);
  }
  h1 { margin: 0; font-size: 1.55rem; font-weight: 750; letter-spacing: -0.025em; }
  .subtitle { color: var(--muted); font-size: 0.9rem; margin-top: 2px; }

  .hero-actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
  .btn {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 13px; border-radius: 9px; font-size: 0.84rem; font-weight: 600;
    border: 1px solid var(--border); background: var(--surface); color: var(--text);
    cursor: pointer; text-decoration: none; transition: all .15s ease;
  }
  .btn:hover { border-color: var(--accent); transform: translateY(-1px); text-decoration: none; }
  .btn-primary {
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    color: #fff; border: none;
  }
  .btn-primary:hover { filter: brightness(1.08); color: #fff; }

  .stats-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
  .stat-pill {
    background: var(--surface); border: 1px solid var(--border);
    padding: 5px 12px; border-radius: 999px; font-size: 0.8rem; color: var(--muted);
    box-shadow: var(--shadow);
  }
  .stat-pill strong { color: var(--text); font-weight: 700; }

  .main { padding: 18px 0 44px; }

  .controls-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 16px; box-shadow: var(--shadow);
    display: grid; gap: 12px; margin-bottom: 14px;
  }
  .search-row {
    display: grid; grid-template-columns: 1fr auto auto auto; gap: 10px; align-items: center;
  }
  .search-wrap { position: relative; display: flex; align-items: center; }
  .search-wrap input {
    width: 100%; padding: 11px 38px 11px 40px;
    background: var(--bg); border: 1px solid var(--border); border-radius: 10px;
    color: var(--text); font-size: 0.95rem; outline: none; transition: border-color .15s;
  }
  .search-wrap input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
  .search-icon { position: absolute; left: 13px; color: var(--muted); pointer-events: none; }
  .clear-btn {
    position: absolute; right: 10px; background: transparent; border: none;
    color: var(--muted); font-size: 1.1rem; cursor: pointer; display: none; padding: 2px 6px;
  }
  .clear-btn.visible { display: block; }

  select {
    background: var(--bg); color: var(--text); border: 1px solid var(--border);
    border-radius: 10px; padding: 9px 12px; font-size: 0.85rem; cursor: pointer;
  }
  select:focus { outline: none; border-color: var(--accent); }

  .view-toggle {
    display: inline-flex; background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px; padding: 3px;
  }
  .view-toggle button {
    border: none; background: transparent; color: var(--muted);
    padding: 6px 11px; border-radius: 7px; font-size: 0.82rem; font-weight: 600; cursor: pointer;
  }
  .view-toggle button.active {
    background: var(--surface); color: var(--accent); box-shadow: var(--shadow);
  }

  .pills-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
  .pill-label { font-size: 0.76rem; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin-right: 2px; }
  .chip {
    display: inline-flex; align-items: center; gap: 5px;
    background: var(--bg); border: 1px solid var(--border);
    padding: 5px 11px; border-radius: 999px; font-size: 0.8rem; font-weight: 500;
    cursor: pointer; user-select: none; color: var(--muted); transition: all .15s;
  }
  .chip:hover { border-color: var(--accent); color: var(--text); }
  .chip.active {
    background: var(--accent-soft); border-color: var(--accent); color: var(--accent); font-weight: 600;
  }
  .chip-star.active {
    background: var(--amber-soft); border-color: var(--amber); color: var(--amber);
  }

  /* Collapsible Analytics Strip */
  .analytics-panel {
    background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
    padding: 14px 16px; margin-bottom: 14px; box-shadow: var(--shadow);
    display: none;
  }
  .analytics-panel.open { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .ana-col h3 { margin: 0 0 10px; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }
  .ana-row {
    display: grid; grid-template-columns: 160px 1fr 48px; gap: 10px; align-items: center;
    margin-bottom: 7px; font-size: 0.8rem; cursor: pointer;
  }
  .ana-row:hover .ana-name { color: var(--accent); }
  .ana-name { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500; }
  .ana-bar-bg { height: 8px; background: var(--surface-2); border-radius: 999px; overflow: hidden; }
  .ana-bar-fill { height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); border-radius: 999px; }
  .ana-count { text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }

  /* Table View */
  .table-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; overflow: hidden; box-shadow: var(--shadow);
  }
  .table-scroll { overflow-x: auto; max-height: 68vh; }
  table { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
  thead th {
    position: sticky; top: 0; z-index: 2;
    background: var(--surface-2); color: var(--muted);
    text-align: left; padding: 11px 12px; border-bottom: 1px solid var(--border);
    font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.04em; white-space: nowrap;
  }
  tbody tr { border-bottom: 1px solid var(--border); cursor: pointer; transition: background .12s; }
  tbody tr:hover { background: var(--surface-2); }
  tbody td { padding: 11px 12px; vertical-align: top; }
  .col-star { width: 42px; text-align: center; }
  .col-sr { width: 58px; color: var(--muted); font-variant-numeric: tabular-nums; }
  .college-title { font-weight: 650; color: var(--text); font-size: 0.9rem; }
  .college-sub { font-size: 0.78rem; color: var(--muted); margin-top: 2px; }

  .star-btn {
    background: transparent; border: none; font-size: 1.15rem; cursor: pointer;
    color: var(--muted); padding: 0 4px; line-height: 1; transition: transform .12s;
  }
  .star-btn:hover { transform: scale(1.18); }
  .star-btn.starred { color: var(--amber); }

  .badge {
    display: inline-block; padding: 2px 8px; border-radius: 6px;
    font-size: 0.74rem; font-weight: 600; background: var(--accent-soft); color: var(--accent);
    white-space: nowrap;
  }
  .badge-green { background: var(--green-soft); color: var(--green); }
  .wa-pill {
    display: inline-flex; align-items: center; gap: 3px;
    padding: 1px 6px; border-radius: 5px; font-size: 0.71rem; font-weight: 600;
    background: var(--green-soft); color: var(--green); margin-left: 5px; text-decoration: none;
  }
  .wa-pill:hover { filter: brightness(0.95); text-decoration: none; }

  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  .ig-link { color: var(--pink); font-weight: 600; }
  .mob-link { color: var(--green); font-weight: 600; font-variant-numeric: tabular-nums; }
  .muted { color: var(--muted); }
  mark { background: var(--mark-bg); color: var(--mark-text); padding: 0 2px; border-radius: 3px; }

  /* Card Grid View */
  .cards-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 14px;
  }
  .college-card {
    background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
    padding: 16px; box-shadow: var(--shadow); cursor: pointer;
    display: flex; flex-direction: column; gap: 10px; transition: transform .15s, border-color .15s;
  }
  .college-card:hover { transform: translateY(-2px); border-color: var(--accent); }
  .card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
  .card-meta { display: grid; gap: 6px; font-size: 0.83rem; }
  .card-row { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .card-footer {
    margin-top: auto; padding-top: 10px; border-top: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: center; gap: 8px; font-size: 0.78rem;
  }

  .copy-mini {
    background: var(--surface-2); border: 1px solid var(--border); color: var(--muted);
    border-radius: 5px; padding: 1px 6px; font-size: 0.71rem; cursor: pointer; margin-left: 4px;
  }
  .copy-mini:hover { color: var(--text); border-color: var(--accent); }

  .pagination {
    display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;
    margin-top: 16px; gap: 12px; font-size: 0.85rem; color: var(--muted);
  }
  .page-btns { display: flex; gap: 6px; align-items: center; }
  .page-btns button:disabled { opacity: 0.45; cursor: not-allowed; }

  /* Slide-over Detail Drawer */
  .drawer-backdrop {
    position: fixed; inset: 0; background: rgba(15, 23, 42, 0.5);
    backdrop-filter: blur(2px); z-index: 50; display: none; justify-content: flex-end;
  }
  .drawer-backdrop.open { display: flex; }
  .drawer {
    width: min(540px, 100vw); height: 100%; background: var(--surface);
    border-left: 1px solid var(--border); box-shadow: var(--shadow-lg);
    overflow-y: auto; padding: 22px; display: flex; flex-direction: column; gap: 14px;
  }
  .drawer-nav { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
  .drawer-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
  .drawer-close {
    background: var(--surface-2); border: 1px solid var(--border); color: var(--text);
    width: 34px; height: 34px; border-radius: 8px; font-size: 1.1rem; cursor: pointer;
  }
  .detail-list { display: grid; gap: 9px; }
  .detail-item {
    background: var(--bg); border: 1px solid var(--border); border-radius: 10px;
    padding: 10px 12px; display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;
  }
  .detail-label { font-size: 0.73rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
  .detail-val { font-size: 0.88rem; font-weight: 500; word-break: break-word; margin-top: 2px; }

  @media (max-width: 900px) {
    .search-row { grid-template-columns: 1fr; }
    .cards-grid { grid-template-columns: 1fr; }
    .analytics-panel.open { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
  <header class="hero">
    <div class="container">
      <div class="hero-top">
        <div class="brand">
          <div class="logo-box">&#127891;</div>
          <div>
            <h1>Maharashtra College Database</h1>
            <div class="subtitle">Fuzzy search across 10,448 colleges — Mumbai, MMR &amp; all of Maharashtra</div>
          </div>
        </div>
        <div class="hero-actions">
          <button class="btn" id="analyticsBtn">&#128200; Insights</button>
          <button class="btn" id="themeBtn" title="Toggle Light / Dark mode">&#127769; Dark Mode</button>
          <a class="btn" href="../data/maharashtra_colleges.xlsx" id="excelLink" download>&#128202; Excel (.xlsx)</a>
          <button class="btn btn-primary" id="exportBtn">&#11015; Export CSV</button>
        </div>
      </div>
      <div class="stats-grid" id="statsBar"></div>
    </div>
  </header>

  <main class="main">
    <div class="container">
      <section class="controls-card">
        <div class="search-row">
          <div class="search-wrap">
            <span class="search-icon">&#128269;</span>
            <input id="searchInput" type="text" placeholder="Press '/' to search... e.g. 'xaviers mumbai', 'vjti', 'ruia', principal name, '+91', or '@handle'" autocomplete="off" />
            <button class="clear-btn" id="clearSearchBtn" title="Clear search">&times;</button>
          </div>
          <select id="districtFilter"><option value="">All Districts (Maharashtra)</option></select>
          <select id="categoryFilter"><option value="">All Categories</option></select>
          <div class="view-toggle">
            <button id="tableViewBtn" class="active">Table</button>
            <button id="cardViewBtn">Cards</button>
          </div>
        </div>

        <div class="pills-row">
          <span class="pill-label">Region:</span>
          <span class="chip active" data-region="all">All Maharashtra</span>
          <span class="chip" data-region="mmr">Mumbai &amp; MMR</span>
          <span class="chip" data-region="Mumbai City">Mumbai City</span>
          <span class="chip" data-region="Mumbai Suburban">Mumbai Suburban</span>
          <span class="chip" data-region="Thane">Thane</span>
          <span class="chip" data-region="Pune">Pune</span>
          <span class="chip" data-region="Nagpur">Nagpur</span>
          <span class="chip" data-region="Nashik">Nashik</span>
        </div>

        <div class="pills-row">
          <span class="pill-label">Filter:</span>
          <span class="chip chip-star" id="shortlistChip">&#9733; Shortlisted (<span id="shortlistCount">0</span>)</span>
          <span class="chip" data-flag="principal">Principal Name</span>
          <span class="chip" data-flag="faculty_mobile">+91 Mobile</span>
          <span class="chip" data-flag="phone">Any Phone</span>
          <span class="chip" data-flag="instagram">Instagram ID</span>
          <span class="chip" data-flag="website">Website</span>
          <select id="sortSelect" style="margin-left:auto;padding:5px 10px;font-size:0.8rem;">
            <option value="relevance">Sort: Relevance / Enriched First</option>
            <option value="name">Sort: Name (A–Z)</option>
            <option value="district">Sort: District (A–Z)</option>
          </select>
          <button class="btn" id="resetBtn" style="padding:5px 10px;font-size:0.8rem;">Reset</button>
        </div>
      </section>

      <section class="analytics-panel" id="analyticsPanel"></section>

      <div id="resultsContainer"></div>

      <div class="pagination">
        <div id="resultInfo">Showing 0 results</div>
        <div class="page-btns">
          <select id="pageSizeSelect">
            <option value="48">48 / page</option>
            <option value="96" selected>96 / page</option>
            <option value="240">240 / page</option>
          </select>
          <button class="btn" id="prevBtn">Prev</button>
          <span id="pageLabel">Page 1</span>
          <button class="btn" id="nextBtn">Next</button>
        </div>
      </div>
    </div>
  </main>

  <div class="drawer-backdrop" id="drawerBackdrop">
    <aside class="drawer" id="drawerPanel">
      <div class="drawer-nav">
        <div style="display:flex;gap:6px;">
          <button class="btn" id="drawerPrev" style="padding:5px 10px;font-size:0.8rem;">&larr; Prev</button>
          <button class="btn" id="drawerNext" style="padding:5px 10px;font-size:0.8rem;">Next &rarr;</button>
        </div>
        <div style="display:flex;gap:8px;align-items:center;">
          <button class="btn" id="drawerStar" style="padding:5px 10px;font-size:0.8rem;">&#9734; Shortlist</button>
          <button class="drawer-close" id="drawerClose">&times;</button>
        </div>
      </div>
      <div class="drawer-header">
        <div>
          <span class="badge" id="drawerCategory"></span>
          <h2 id="drawerTitle" style="margin:6px 0 2px;font-size:1.18rem;"></h2>
          <div id="drawerSub" class="muted" style="font-size:0.84rem;"></div>
        </div>
      </div>
      <div class="detail-list" id="drawerBody"></div>
    </aside>
  </div>

<script>
const COLLEGES = __DATA_JSON__;
const MMR_DISTS = new Set(["Mumbai City", "Mumbai Suburban", "Thane", "Raigad", "Palghar"]);

for (const c of COLLEGES) {
  c._id = (c.aishe_code || "") + "::" + c.name;
  c._blob = [
    c.name, c.principal_name, c.college_phone, c.principal_phone, c.faculty_mobile,
    c.instagram_id, c.district, c.city, c.category, c.affiliation,
    c.management_type, c.email, c.address, c.aishe_code
  ].join(" ").toLowerCase();
  c._nameL = (c.name || "").toLowerCase();
}

function editDistanceAtMost2(a, b) {
  if (Math.abs(a.length - b.length) > 2) return 99;
  const n = a.length, m = b.length;
  let prev = Array.from({length: m + 1}, (_, j) => j);
  for (let i = 1; i <= n; i++) {
    const curr = [i];
    let rowMin = i;
    for (let j = 1; j <= m; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      const val = Math.min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost);
      curr.push(val);
      if (val < rowMin) rowMin = val;
    }
    if (rowMin > 2) return 99;
    prev = curr;
  }
  return prev[m];
}

function subsequenceScore(query, target) {
  let qi = 0, gaps = 0;
  for (let ti = 0; ti < target.length && qi < query.length; ti++) {
    if (target[ti] === query[qi]) qi++;
    else if (qi > 0) gaps++;
  }
  if (qi < query.length) return 0;
  return Math.max(5, 40 - Math.min(35, gaps));
}

function fuzzyScore(item, tokens) {
  if (!tokens.length) return 1;
  let total = 0;
  const words = item._blob.split(/[^a-z0-9+]+/).filter(Boolean);
  for (const tok of tokens) {
    if (item._nameL.includes(tok)) {
      total += item._nameL.startsWith(tok) ? 120 : 90;
    } else if (item._blob.includes(tok)) {
      total += 60;
    } else if (tok.length >= 3) {
      let bestFuzzy = 0;
      for (const w of words) {
        if (Math.abs(w.length - tok.length) <= 2) {
          const d = editDistanceAtMost2(tok, w);
          if (d === 1) { bestFuzzy = Math.max(bestFuzzy, 42); break; }
          if (d === 2 && tok.length >= 5) { bestFuzzy = Math.max(bestFuzzy, 25); }
        }
      }
      if (!bestFuzzy) bestFuzzy = subsequenceScore(tok, item._nameL);
      if (!bestFuzzy) return 0;
      total += bestFuzzy;
    } else {
      return 0;
    }
  }
  return total;
}

function esc(s) {
  return String(s || "").replace(/[&<>"']/g, ch => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[ch]));
}

function highlight(text, tokens) {
  const safe = esc(text);
  if (!tokens.length || !safe) return safe;
  let out = safe;
  for (const tok of tokens) {
    if (tok.length < 2) continue;
    const re = new RegExp(`(${tok.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "ig");
    out = out.replace(re, "<mark>$1</mark>");
  }
  return out;
}

function waLink(mobStr) {
  const first = (mobStr || "").split(",")[0].replace(/\D/g, "");
  if (first.length === 12 && first.startsWith("91")) return `https://wa.me/${first}`;
  if (first.length === 10) return `https://wa.me/91${first}`;
  return "";
}

const state = {
  query: "",
  region: "all",
  district: "",
  category: "",
  sort: "relevance",
  view: window.innerWidth < 820 ? "cards" : "table",
  shortlistOnly: false,
  analyticsOpen: false,
  flags: new Set(),
  shortlist: new Set(JSON.parse(localStorage.getItem("mh_college_shortlist") || "[]")),
  page: 1,
  pageSize: 96,
  filtered: COLLEGES,
  drawerSrNo: null,
};

function saveShortlist() {
  localStorage.setItem("mh_college_shortlist", JSON.stringify([...state.shortlist]));
  document.getElementById("shortlistCount").textContent = state.shortlist.size;
}

function toggleStar(id, ev) {
  if (ev) ev.stopPropagation();
  if (state.shortlist.has(id)) state.shortlist.delete(id);
  else state.shortlist.add(id);
  saveShortlist();
  if (state.shortlistOnly) applyFilters();
  else renderResults();
  if (state.drawerSrNo !== null) {
    const cur = COLLEGES.find(x => x.sr_no === state.drawerSrNo);
    if (cur) updateDrawerStarBtn(cur);
  }
}

function initTheme() {
  const saved = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", saved);
  updateThemeBtn(saved);
}
function updateThemeBtn(t) {
  document.getElementById("themeBtn").innerHTML = t === "dark" ? "&#9728;&#65039; Light Mode" : "&#127769; Dark Mode";
}
document.getElementById("themeBtn").addEventListener("click", () => {
  const cur = document.documentElement.getAttribute("data-theme");
  const next = cur === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("theme", next);
  updateThemeBtn(next);
});

// Dynamic GitHub Pages Excel download link
(function resolveExcelUrl() {
  const link = document.getElementById("excelLink");
  if (location.hostname.endsWith(".github.io")) {
    const user = location.hostname.split(".")[0];
    const repo = location.pathname.split("/").filter(Boolean)[0] || "Maharashtra-College-Database-2026";
    link.href = `https://raw.githubusercontent.com/${user}/${repo}/main/data/maharashtra_colleges.xlsx`;
  } else if (location.protocol === "file:") {
    link.href = "../data/maharashtra_colleges.xlsx";
  }
})();

function syncUrlParams() {
  if (location.protocol === "file:") return;
  const p = new URLSearchParams();
  if (state.query) p.set("q", state.query);
  if (state.region !== "all") p.set("region", state.region);
  if (state.district) p.set("district", state.district);
  if (state.category) p.set("category", state.category);
  if (state.shortlistOnly) p.set("shortlist", "1");
  if (state.flags.size) p.set("flags", [...state.flags].join(","));
  const qs = p.toString();
  history.replaceState(null, "", qs ? `?${qs}` : location.pathname);
}

function loadUrlParams() {
  const p = new URLSearchParams(location.search);
  if (p.get("q")) {
    state.query = p.get("q");
    document.getElementById("searchInput").value = state.query;
    document.getElementById("clearSearchBtn").classList.add("visible");
  }
  if (p.get("region")) {
    state.region = p.get("region");
    document.querySelectorAll(".chip[data-region]").forEach(x => x.classList.toggle("active", x.dataset.region === state.region));
  }
  if (p.get("district")) {
    state.district = p.get("district");
    document.getElementById("districtFilter").value = state.district;
  }
  if (p.get("category")) {
    state.category = p.get("category");
    document.getElementById("categoryFilter").value = state.category;
  }
  if (p.get("shortlist") === "1") {
    state.shortlistOnly = true;
    document.getElementById("shortlistChip").classList.add("active");
  }
  if (p.get("flags")) {
    for (const f of p.get("flags").split(",")) {
      state.flags.add(f);
      const el = document.querySelector(`.chip[data-flag="${f}"]`);
      if (el) el.classList.add("active");
    }
  }
}

function initFilters() {
  const distCounts = {};
  const catCounts = {};
  let pCount = 0, mobCount = 0, igCount = 0, webCount = 0;

  for (const c of COLLEGES) {
    if (c.district) distCounts[c.district] = (distCounts[c.district] || 0) + 1;
    if (c.category) catCounts[c.category] = (catCounts[c.category] || 0) + 1;
    if (c.principal_name) pCount++;
    if (c.faculty_mobile) mobCount++;
    if (c.instagram_id) igCount++;
    if (c.website) webCount++;
  }

  document.getElementById("statsBar").innerHTML = `
    <span class="stat-pill">Total: <strong>${COLLEGES.length.toLocaleString()}</strong></span>
    <span class="stat-pill">Districts: <strong>${Object.keys(distCounts).length}</strong></span>
    <span class="stat-pill">Principals: <strong>${pCount.toLocaleString()}</strong></span>
    <span class="stat-pill">+91 Mobiles: <strong>${mobCount.toLocaleString()}</strong></span>
    <span class="stat-pill">Instagram: <strong>${igCount.toLocaleString()}</strong></span>
    <span class="stat-pill">Websites: <strong>${webCount.toLocaleString()}</strong></span>
  `;

  const distSel = document.getElementById("districtFilter");
  Object.entries(distCounts).sort((a, b) => a[0].localeCompare(b[0])).forEach(([d, n]) => {
    const opt = document.createElement("option");
    opt.value = d;
    opt.textContent = `${d} (${n})`;
    distSel.appendChild(opt);
  });

  const catSel = document.getElementById("categoryFilter");
  Object.entries(catCounts).sort((a, b) => b[1] - a[1]).forEach(([cat, n]) => {
    const opt = document.createElement("option");
    opt.value = cat;
    opt.textContent = `${cat} (${n})`;
    catSel.appendChild(opt);
  });

  saveShortlist();
  updateViewButtons();
}

function updateViewButtons() {
  document.getElementById("tableViewBtn").classList.toggle("active", state.view === "table");
  document.getElementById("cardViewBtn").classList.toggle("active", state.view === "cards");
}

function renderAnalytics() {
  const panel = document.getElementById("analyticsPanel");
  if (!state.analyticsOpen) { panel.classList.remove("open"); return; }
  panel.classList.add("open");

  const dCounts = {}, cCounts = {};
  for (const c of state.filtered) {
    if (c.district) dCounts[c.district] = (dCounts[c.district] || 0) + 1;
    if (c.category) cCounts[c.category] = (cCounts[c.category] || 0) + 1;
  }
  const topD = Object.entries(dCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);
  const topC = Object.entries(cCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);
  const maxD = topD[0]?.[1] || 1;
  const maxC = topC[0]?.[1] || 1;

  panel.innerHTML = `
    <div class="ana-col">
      <h3>Top Districts (Current Results)</h3>
      ${topD.map(([name, cnt]) => `<div class="ana-row" onclick="quickFilterDist('${esc(name)}')">
        <span class="ana-name">${esc(name)}</span>
        <div class="ana-bar-bg"><div class="ana-bar-fill" style="width:${Math.round(cnt / maxD * 100)}%"></div></div>
        <span class="ana-count">${cnt}</span>
      </div>`).join("") || '<span class="muted">No data</span>'}
    </div>
    <div class="ana-col">
      <h3>Top Categories (Current Results)</h3>
      ${topC.map(([name, cnt]) => `<div class="ana-row" onclick="quickFilterCat('${esc(name)}')">
        <span class="ana-name">${esc(name)}</span>
        <div class="ana-bar-bg"><div class="ana-bar-fill" style="width:${Math.round(cnt / maxC * 100)}%"></div></div>
        <span class="ana-count">${cnt}</span>
      </div>`).join("") || '<span class="muted">No data</span>'}
    </div>
  `;
}

function quickFilterDist(d) {
  state.district = d;
  document.getElementById("districtFilter").value = d;
  applyFilters();
}
function quickFilterCat(cat) {
  state.category = cat;
  document.getElementById("categoryFilter").value = cat;
  applyFilters();
}

function applyFilters() {
  const tokens = state.query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  const res = [];

  for (const c of COLLEGES) {
    if (state.shortlistOnly && !state.shortlist.has(c._id)) continue;
    if (state.region === "mmr" && !MMR_DISTS.has(c.district)) continue;
    if (state.region !== "all" && state.region !== "mmr" && c.district !== state.region) continue;
    if (state.district && c.district !== state.district) continue;
    if (state.category && c.category !== state.category) continue;
    if (state.flags.has("principal") && !c.principal_name) continue;
    if (state.flags.has("faculty_mobile") && !c.faculty_mobile) continue;
    if (state.flags.has("phone") && !c.college_phone && !c.principal_phone && !c.faculty_mobile) continue;
    if (state.flags.has("instagram") && !c.instagram_id) continue;
    if (state.flags.has("website") && !c.website) continue;

    const score = fuzzyScore(c, tokens);
    if (score > 0) res.push({ item: c, score });
  }

  if (state.sort === "name") {
    res.sort((a, b) => a.item.name.localeCompare(b.item.name));
  } else if (state.sort === "district") {
    res.sort((a, b) => a.item.district.localeCompare(b.item.district) || a.item.name.localeCompare(b.item.name));
  } else if (tokens.length) {
    res.sort((a, b) => b.score - a.score || a.item.sr_no - b.item.sr_no);
  }

  state.filtered = res.map(x => x.item);
  state.page = 1;
  syncUrlParams();
  renderAnalytics();
  renderResults(tokens);
}

function copyText(txt, btn, ev) {
  if (ev) ev.stopPropagation();
  navigator.clipboard.writeText(txt).then(() => {
    const old = btn.textContent;
    btn.textContent = "Copied!";
    setTimeout(() => { btn.textContent = old; }, 1000);
  });
}

function updateDrawerStarBtn(c) {
  const btn = document.getElementById("drawerStar");
  const starred = state.shortlist.has(c._id);
  btn.innerHTML = starred ? "&#9733; Shortlisted" : "&#9734; Shortlist";
  btn.style.borderColor = starred ? "var(--amber)" : "";
  btn.style.color = starred ? "var(--amber)" : "";
}

function openDrawer(srNo) {
  const idx = state.filtered.findIndex(x => x.sr_no === srNo);
  const c = idx >= 0 ? state.filtered[idx] : COLLEGES.find(x => x.sr_no === srNo);
  if (!c) return;
  state.drawerSrNo = c.sr_no;

  document.getElementById("drawerPrev").disabled = idx <= 0;
  document.getElementById("drawerNext").disabled = idx < 0 || idx >= state.filtered.length - 1;
  updateDrawerStarBtn(c);

  document.getElementById("drawerCategory").textContent = c.category || "Institution";
  document.getElementById("drawerTitle").textContent = c.name;
  document.getElementById("drawerSub").textContent = `${c.city || c.district} • ${c.district} ${c.aishe_code ? "• " + c.aishe_code : ""}`;

  const fields = [
    ["Principal Name", c.principal_name],
    ["Faculty / Personal Mobile (+91)", c.faculty_mobile],
    ["Principal Phone", c.principal_phone],
    ["College Phone", c.college_phone],
    ["Instagram ID", c.instagram_id],
    ["Official Website", c.website],
    ["Official Email ID", c.email],
    ["University / Board Affiliation", c.affiliation],
    ["Management Type", c.management_type],
    ["Full Address & Pincode", c.address],
    ["AISHE / DTE Code", c.aishe_code],
    ["Data Source / Verification", c.verification_source],
  ];

  document.getElementById("drawerBody").innerHTML = fields.map(([label, val]) => {
    let valHtml = val ? esc(val) : '<span class="muted">Not listed</span>';
    if (val && label === "Official Website") valHtml = `<a href="${esc(val)}" target="_blank" rel="noopener">${esc(val)}</a>`;
    if (val && label === "Official Email ID") valHtml = `<a href="mailto:${esc(val)}">${esc(val)}</a>`;
    if (val && label === "Instagram ID") valHtml = `<a class="ig-link" href="https://www.instagram.com/${esc(val.replace(/^@/, ''))}/" target="_blank" rel="noopener">${esc(val)}</a>`;
    if (val && label.includes("Mobile")) {
      const wa = waLink(val);
      valHtml = `<a class="mob-link" href="tel:${esc(val.split(',')[0].trim())}">${esc(val)}</a>` + (wa ? `<a class="wa-pill" href="${wa}" target="_blank" rel="noopener">WhatsApp &#8599;</a>` : "");
    }

    return `<div class="detail-item">
      <div>
        <div class="detail-label">${esc(label)}</div>
        <div class="detail-val">${valHtml}</div>
      </div>
      ${val ? `<button class="copy-mini" onclick="copyText('${esc(val)}', this, event)">Copy</button>` : ""}
    </div>`;
  }).join("");

  document.getElementById("drawerBackdrop").classList.add("open");
}

function stepDrawer(delta) {
  if (state.drawerSrNo === null) return;
  const idx = state.filtered.findIndex(x => x.sr_no === state.drawerSrNo);
  if (idx < 0) return;
  const next = state.filtered[idx + delta];
  if (next) openDrawer(next.sr_no);
}

function renderResults(tokens = state.query.trim().toLowerCase().split(/\s+/).filter(Boolean)) {
  const container = document.getElementById("resultsContainer");
  const total = state.filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / state.pageSize));
  if (state.page > totalPages) state.page = totalPages;

  const start = (state.page - 1) * state.pageSize;
  const slice = state.filtered.slice(start, start + state.pageSize);

  if (!slice.length) {
    container.innerHTML = `<div class="table-card" style="padding:48px;text-align:center;color:var(--muted);">No matching colleges found. Try a broader search or reset filters.</div>`;
  } else if (state.view === "cards") {
    container.innerHTML = `<div class="cards-grid">` + slice.map(c => {
      const ig = (c.instagram_id || "").replace(/^@/, "");
      const mob = c.faculty_mobile || "";
      const wa = waLink(mob);
      const phone = c.college_phone || c.principal_phone || "";
      const starred = state.shortlist.has(c._id);
      return `<article class="college-card" onclick="openDrawer(${c.sr_no})">
        <div class="card-top">
          <div>
            <div class="college-title">${highlight(c.name, tokens)}</div>
            <div class="college-sub">${highlight(c.district, tokens)}${c.city && c.city !== c.district ? " • " + highlight(c.city, tokens) : ""}</div>
          </div>
          <div style="display:flex;align-items:center;gap:4px;">
            <button class="star-btn ${starred ? 'starred' : ''}" onclick="toggleStar('${esc(c._id)}', event)" title="Shortlist">${starred ? "&#9733;" : "&#9734;"}</button>
            <span class="badge">${esc(c.category.split(" ")[0])}</span>
          </div>
        </div>
        <div class="card-meta">
          ${c.principal_name ? `<div class="card-row"><span class="muted">Principal:</span> <strong>${highlight(c.principal_name, tokens)}</strong></div>` : ""}
          ${mob ? `<div class="card-row"><span class="badge badge-green">${highlight(mob, tokens)}</span>${wa ? `<a class="wa-pill" href="${wa}" target="_blank" rel="noopener" onclick="event.stopPropagation()">WA &#8599;</a>` : ""}<button class="copy-mini" onclick="copyText('${esc(mob)}', this, event)">Copy</button></div>` : (phone ? `<div class="card-row"><span class="muted">Tel:</span> ${highlight(phone, tokens)}</div>` : "")}
          ${ig ? `<div class="card-row"><a class="ig-link" href="https://www.instagram.com/${esc(ig)}/" target="_blank" rel="noopener" onclick="event.stopPropagation()">@${highlight(ig, tokens)}</a></div>` : ""}
        </div>
        <div class="card-footer">
          <span class="muted">${esc(c.aishe_code || "Details")}</span>
          ${c.website ? `<a href="${esc(c.website)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">Website &#8599;</a>` : `<span style="color:var(--accent)">View Details &rarr;</span>`}
        </div>
      </article>`;
    }).join("") + `</div>`;
  } else {
    const rows = slice.map(c => {
      const ig = (c.instagram_id || "").replace(/^@/, "");
      const mob = c.faculty_mobile || "";
      const wa = waLink(mob);
      const tel = c.college_phone || c.principal_phone || "";
      const starred = state.shortlist.has(c._id);
      return `<tr onclick="openDrawer(${c.sr_no})">
        <td class="col-star"><button class="star-btn ${starred ? 'starred' : ''}" onclick="toggleStar('${esc(c._id)}', event)" title="Shortlist">${starred ? "&#9733;" : "&#9734;"}</button></td>
        <td class="col-sr">${c.sr_no}</td>
        <td>
          <div class="college-title">${highlight(c.name, tokens)}</div>
          <div class="college-sub">${highlight(c.district, tokens)}${c.city && c.city !== c.district ? " • " + highlight(c.city, tokens) : ""}${c.affiliation ? " • " + highlight(c.affiliation, tokens) : ""}</div>
        </td>
        <td>${c.principal_name ? highlight(c.principal_name, tokens) : '<span class="muted">—</span>'}</td>
        <td>
          ${mob ? `<div><a class="mob-link" href="tel:${esc(mob.split(',')[0].trim())}" onclick="event.stopPropagation()">${highlight(mob, tokens)}</a>${wa ? `<a class="wa-pill" href="${wa}" target="_blank" rel="noopener" onclick="event.stopPropagation()">WA</a>` : ""}<button class="copy-mini" onclick="copyText('${esc(mob)}', this, event)">Copy</button></div>` : ""}
          ${tel ? `<div style="font-size:0.8rem;color:var(--muted);margin-top:2px;">${highlight(tel, tokens)}</div>` : (!mob ? '<span class="muted">—</span>' : "")}
        </td>
        <td>${ig ? `<a class="ig-link" href="https://www.instagram.com/${esc(ig)}/" target="_blank" rel="noopener" onclick="event.stopPropagation()">@${highlight(ig, tokens)}</a>` : '<span class="muted">—</span>'}</td>
        <td><span class="badge">${esc(c.category)}</span></td>
        <td>${c.website ? `<a href="${esc(c.website)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">Visit &#8599;</a>` : '<span class="muted">Details</span>'}</td>
      </tr>`;
    }).join("");

    container.innerHTML = `<div class="table-card"><div class="table-scroll">
      <table>
        <thead><tr>
          <th class="col-star">&#9733;</th>
          <th class="col-sr">#</th>
          <th>College &amp; Location</th>
          <th>Principal</th>
          <th>+91 Mobile &amp; Phone</th>
          <th>Instagram</th>
          <th>Category</th>
          <th>Site</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div></div>`;
  }

  document.getElementById("resultInfo").textContent =
    total ? `Showing ${(start + 1).toLocaleString()}–${Math.min(start + state.pageSize, total).toLocaleString()} of ${total.toLocaleString()} colleges` : "0 results";
  document.getElementById("pageLabel").textContent = `Page ${state.page} of ${totalPages}`;
  document.getElementById("prevBtn").disabled = state.page <= 1;
  document.getElementById("nextBtn").disabled = state.page >= totalPages;
}

function exportFilteredCsv() {
  const headers = [
    "Sr. No.", "Name of the College", "Principal Name", "Phone Number of the College",
    "Phone Number of the Principal", "Faculty / Personal Mobile (+91)", "Instagram ID",
    "District", "City / Area", "Category / Stream", "University / Board Affiliation",
    "Management Type", "Official Email ID", "Official Website", "Full Address & Pincode",
    "AISHE / DTE Code", "Data Source / Verification"
  ];
  const keys = [
    "sr_no", "name", "principal_name", "college_phone", "principal_phone", "faculty_mobile",
    "instagram_id", "district", "city", "category", "affiliation", "management_type",
    "email", "website", "address", "aishe_code", "verification_source"
  ];
  const rows = [headers.join(",")];
  for (const c of state.filtered) {
    rows.push(keys.map(k => `"${String(c[k] || "").replace(/"/g, '""')}"`).join(","));
  }
  const blob = new Blob(["\uFEFF" + rows.join("\n")], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = state.shortlistOnly ? "maharashtra_colleges_shortlist.csv" : "maharashtra_colleges_filtered.csv";
  a.click();
}

let debounceTimer;
const searchEl = document.getElementById("searchInput");
const clearBtn = document.getElementById("clearSearchBtn");
searchEl.addEventListener("input", e => {
  clearBtn.classList.toggle("visible", !!e.target.value);
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => { state.query = e.target.value; applyFilters(); }, 100);
});
clearBtn.addEventListener("click", () => {
  searchEl.value = ""; clearBtn.classList.remove("visible"); state.query = ""; applyFilters(); searchEl.focus();
});

document.addEventListener("keydown", e => {
  if (e.key === "/" && document.activeElement !== searchEl) { e.preventDefault(); searchEl.focus(); }
  const drawerOpen = document.getElementById("drawerBackdrop").classList.contains("open");
  if (drawerOpen) {
    if (e.key === "Escape") { document.getElementById("drawerBackdrop").classList.remove("open"); state.drawerSrNo = null; }
    if (e.key === "ArrowLeft") stepDrawer(-1);
    if (e.key === "ArrowRight") stepDrawer(1);
  }
});

document.getElementById("drawerClose").addEventListener("click", () => { document.getElementById("drawerBackdrop").classList.remove("open"); state.drawerSrNo = null; });
document.getElementById("drawerBackdrop").addEventListener("click", e => {
  if (e.target.id === "drawerBackdrop") { document.getElementById("drawerBackdrop").classList.remove("open"); state.drawerSrNo = null; }
});
document.getElementById("drawerPrev").addEventListener("click", () => stepDrawer(-1));
document.getElementById("drawerNext").addEventListener("click", () => stepDrawer(1));
document.getElementById("drawerStar").addEventListener("click", () => {
  const c = COLLEGES.find(x => x.sr_no === state.drawerSrNo);
  if (c) toggleStar(c._id);
});

document.getElementById("analyticsBtn").addEventListener("click", () => {
  state.analyticsOpen = !state.analyticsOpen;
  document.getElementById("analyticsBtn").style.borderColor = state.analyticsOpen ? "var(--accent)" : "";
  renderAnalytics();
});

document.getElementById("shortlistChip").addEventListener("click", () => {
  state.shortlistOnly = !state.shortlistOnly;
  document.getElementById("shortlistChip").classList.toggle("active", state.shortlistOnly);
  applyFilters();
});

document.getElementById("districtFilter").addEventListener("change", e => { state.district = e.target.value; applyFilters(); });
document.getElementById("categoryFilter").addEventListener("change", e => { state.category = e.target.value; applyFilters(); });
document.getElementById("sortSelect").addEventListener("change", e => { state.sort = e.target.value; applyFilters(); });
document.getElementById("pageSizeSelect").addEventListener("change", e => { state.pageSize = Number(e.target.value); state.page = 1; renderResults(); });
document.getElementById("prevBtn").addEventListener("click", () => { if (state.page > 1) { state.page--; renderResults(); window.scrollTo({top: 0, behavior: "smooth"}); } });
document.getElementById("nextBtn").addEventListener("click", () => { state.page++; renderResults(); window.scrollTo({top: 0, behavior: "smooth"}); });
document.getElementById("exportBtn").addEventListener("click", exportFilteredCsv);
document.getElementById("tableViewBtn").addEventListener("click", () => { state.view = "table"; updateViewButtons(); renderResults(); });
document.getElementById("cardViewBtn").addEventListener("click", () => { state.view = "cards"; updateViewButtons(); renderResults(); });

document.querySelectorAll(".chip[data-region]").forEach(ch => {
  ch.addEventListener("click", () => {
    document.querySelectorAll(".chip[data-region]").forEach(x => x.classList.remove("active"));
    ch.classList.add("active");
    state.region = ch.dataset.region;
    applyFilters();
  });
});

document.querySelectorAll(".chip[data-flag]").forEach(ch => {
  ch.addEventListener("click", () => {
    const f = ch.dataset.flag;
    if (state.flags.has(f)) { state.flags.delete(f); ch.classList.remove("active"); }
    else { state.flags.add(f); ch.classList.add("active"); }
    applyFilters();
  });
});

document.getElementById("resetBtn").addEventListener("click", () => {
  state.query = ""; state.region = "all"; state.district = ""; state.category = ""; state.sort = "relevance";
  state.shortlistOnly = false; state.flags.clear();
  searchEl.value = ""; clearBtn.classList.remove("visible");
  document.getElementById("districtFilter").value = "";
  document.getElementById("categoryFilter").value = "";
  document.getElementById("sortSelect").value = "relevance";
  document.getElementById("shortlistChip").classList.remove("active");
  document.querySelectorAll(".chip[data-flag]").forEach(x => x.classList.remove("active"));
  document.querySelectorAll(".chip[data-region]").forEach(x => x.classList.toggle("active", x.dataset.region === "all"));
  applyFilters();
});

initTheme();
initFilters();
loadUrlParams();
applyFilters();
</script>
</body>
</html>
"""


def main() -> None:
    with open(IN_JSON, encoding="utf-8") as f:
        data = json.load(f)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")
    html = HTML_TEMPLATE.replace("__DATA_JSON__", payload)
    OUT_HTML.write_text(html, encoding="utf-8")
    size_mb = OUT_HTML.stat().st_size / (1024 * 1024)
    print(f"Saved {OUT_HTML.name} ({size_mb:.2f} MB) with {len(data)} colleges.")


if __name__ == "__main__":
    main()
