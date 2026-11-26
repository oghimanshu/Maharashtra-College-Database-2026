#!/usr/bin/env python3
"""
Generate the GitHub Pages web app (docs/index.html) inspired by the PostNew
achromatic gallery design system:
- 5-token grayscale palette (#1a1a1a, #242424, #5d5d5d, #fafafa, #000000)
- 0px border-radius everywhere, flat surface hierarchy (zero shadows, zero gradients)
- Inter Tight (500) at 18px/22px for editorial display + system-ui (400) at 12px for chrome
- Centered minimalist Top Nav Bar, Left-Edge Scroll Position Dots, Bottom-Center Floating View Toggle
- Full functionality: fuzzy search, URL state, Shortlist, WhatsApp/IG/Website links,
  Insights strip, and Slide-over Detail Drawer with Prev/Next & Copy.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
IN_JSON = BASE_DIR / "data" / "maharashtra_colleges.json"
OUT_HTML = BASE_DIR / "docs" / "index.html"

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Maharashtra College Database (2026) — Index</title>
<meta name="description" content="Curated directory of 10,448 colleges across Mumbai, MMR, and Maharashtra with Principal names, +91 mobiles, Instagram IDs, and affiliations." />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500&display=swap" rel="stylesheet" />
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%231a1a1a'/><text x='50' y='66' font-size='52' text-anchor='middle' fill='%23fafafa' font-family='sans-serif'>M</text></svg>" />
<style>
  :root {
    --color-canvas-black: #1a1a1a;
    --color-bone-white: #fafafa;
    --color-slate-surface: #242424;
    --color-ash: #5d5d5d;
    --color-absolute-black: #000000;

    --font-display: 'ABC Diatype Medium', 'Inter Tight', ui-sans-serif, system-ui, -apple-system, sans-serif;
    --font-chrome: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;

    --spacing-5: 5px;
    --spacing-7: 7px;
    --spacing-8: 8px;
    --spacing-10: 10px;
    --spacing-12: 12px;
    --spacing-13: 13px;
    --spacing-14: 14px;
    --spacing-50: 50px;
  }

  * { box-sizing: border-box; border-radius: 0px !important; box-shadow: none !important; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0;
    background: var(--color-canvas-black);
    color: var(--color-bone-white);
    font-family: var(--font-chrome);
    font-size: 12px;
    font-weight: 400;
    line-height: 1.2;
    -webkit-font-smoothing: antialiased;
  }

  a { color: var(--color-bone-white); text-decoration: none; }
  a:hover { text-decoration: underline; }

  .container {
    width: 100%;
    max-width: 1320px;
    margin: 0 auto;
    padding: 0 24px;
  }

  /* PostNew Centered Top Nav Bar */
  .top-nav {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    padding: 22px 24px 0;
  }
  .top-nav a, .top-nav button {
    background: transparent;
    border: none;
    color: var(--color-bone-white);
    font-family: var(--font-chrome);
    font-size: 12px;
    font-weight: 400;
    line-height: 1.2;
    letter-spacing: 0px;
    padding: 0;
    cursor: pointer;
    opacity: 0.78;
    transition: opacity .15s;
  }
  .top-nav a:hover, .top-nav button:hover, .top-nav .nav-active {
    opacity: 1;
    text-decoration: underline;
    text-underline-offset: 4px;
  }

  /* PostNew Left-Edge Scroll Position Indicator */
  .scroll-dots {
    position: fixed;
    left: 28px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    flex-direction: column;
    gap: 5px;
    z-index: 20;
  }
  .scroll-dot {
    width: 4px;
    height: 4px;
    background: var(--color-ash);
    transition: background .15s;
  }
  .scroll-dot.active { background: var(--color-bone-white); }

  /* Vitrine Header */
  .vitrine-header {
    padding: var(--spacing-50) 0 36px;
    border-bottom: 1px solid var(--color-absolute-black);
  }
  .header-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: flex-end;
    gap: 24px;
  }
  .editorial-h1 {
    font-family: var(--font-display);
    font-weight: 500;
    font-size: 22px;
    line-height: 1.15;
    letter-spacing: -0.55px;
    margin: 0 0 8px;
    color: var(--color-bone-white);
    font-feature-settings: "blwf", "cv03", "cv04", "cv09", "cv11", "ss09", "ss10";
  }
  .editorial-lead {
    font-family: var(--font-display);
    font-weight: 500;
    font-size: 18px;
    line-height: 1.13;
    letter-spacing: -0.45px;
    color: var(--color-ash);
    margin: 0;
    max-width: 680px;
    font-feature-settings: "blwf", "cv03", "cv04", "cv09", "cv11", "ss09", "ss10";
  }

  .header-actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-10);
    align-items: center;
  }

  /* Ghost & Slate Buttons */
  .btn-ghost {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    background: var(--color-slate-surface);
    color: var(--color-bone-white);
    border: 1px solid var(--color-absolute-black);
    font-family: var(--font-chrome);
    font-size: 12px;
    font-weight: 400;
    line-height: 1.2;
    cursor: pointer;
    text-decoration: none;
  }
  .btn-ghost:hover {
    background: var(--color-bone-white);
    color: var(--color-canvas-black);
    text-decoration: none;
  }
  .btn-ghost:disabled { opacity: 0.35; cursor: not-allowed; }
  .btn-ghost:disabled:hover { background: var(--color-slate-surface); color: var(--color-bone-white); }

  .stats-strip {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-10);
    margin-top: 24px;
  }
  .stat-cell {
    background: var(--color-slate-surface);
    border: 1px solid var(--color-absolute-black);
    padding: 8px 12px;
    color: var(--color-ash);
  }
  .stat-cell strong {
    color: var(--color-bone-white);
    font-weight: 400;
    margin-left: 4px;
  }

  /* Main Section */
  .gallery-main { padding: 36px 0 96px; }

  .controls-vitrine {
    background: var(--color-slate-surface);
    border: 1px solid var(--color-absolute-black);
    padding: var(--spacing-12);
    display: grid;
    gap: var(--spacing-10);
    margin-bottom: var(--spacing-50);
  }
  .search-row {
    display: grid;
    grid-template-columns: 1fr auto auto auto;
    gap: var(--spacing-10);
    align-items: center;
  }
  .search-wrap { position: relative; display: flex; align-items: center; }
  .search-wrap input {
    width: 100%;
    padding: 10px 32px 10px 12px;
    background: var(--color-canvas-black);
    border: 1px solid var(--color-absolute-black);
    color: var(--color-bone-white);
    font-family: var(--font-chrome);
    font-size: 12px;
    outline: none;
  }
  .search-wrap input::placeholder { color: var(--color-ash); }
  .search-wrap input:focus { border-color: var(--color-bone-white); }
  .clear-btn {
    position: absolute;
    right: 8px;
    background: transparent;
    border: none;
    color: var(--color-ash);
    font-size: 14px;
    cursor: pointer;
    display: none;
  }
  .clear-btn.visible { display: block; }
  .clear-btn:hover { color: var(--color-bone-white); }

  select {
    background: var(--color-canvas-black);
    color: var(--color-bone-white);
    border: 1px solid var(--color-absolute-black);
    padding: 10px 12px;
    font-family: var(--font-chrome);
    font-size: 12px;
    cursor: pointer;
    outline: none;
  }
  select:focus { border-color: var(--color-bone-white); }

  .pills-row {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-8);
    align-items: center;
  }
  .pill-label {
    color: var(--color-ash);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-right: 4px;
  }
  .chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: var(--color-canvas-black);
    border: 1px solid var(--color-absolute-black);
    padding: 6px 10px;
    color: var(--color-ash);
    cursor: pointer;
    user-select: none;
  }
  .chip:hover { color: var(--color-bone-white); }
  .chip.active {
    background: var(--color-bone-white);
    color: var(--color-canvas-black);
  }

  /* Insights Panel */
  .analytics-panel {
    background: var(--color-slate-surface);
    border: 1px solid var(--color-absolute-black);
    padding: var(--spacing-14);
    margin-bottom: var(--spacing-50);
    display: none;
  }
  .analytics-panel.open {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }
  .ana-col h3 {
    margin: 0 0 12px;
    font-family: var(--font-display);
    font-weight: 500;
    font-size: 18px;
    line-height: 1.13;
    letter-spacing: -0.45px;
    color: var(--color-bone-white);
  }
  .ana-row {
    display: grid;
    grid-template-columns: 160px 1fr 48px;
    gap: 10px;
    align-items: center;
    margin-bottom: 8px;
    cursor: pointer;
  }
  .ana-row:hover .ana-name { text-decoration: underline; }
  .ana-name { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--color-bone-white); }
  .ana-bar-bg { height: 6px; background: var(--color-canvas-black); border: 1px solid var(--color-absolute-black); }
  .ana-bar-fill { height: 100%; background: var(--color-bone-white); }
  .ana-count { text-align: right; color: var(--color-ash); font-variant-numeric: tabular-nums; }

  /* Table View */
  .table-frame {
    background: var(--color-slate-surface);
    border: 1px solid var(--color-absolute-black);
  }
  .table-scroll { overflow-x: auto; max-height: 70vh; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  thead th {
    position: sticky;
    top: 0;
    z-index: 2;
    background: var(--color-canvas-black);
    color: var(--color-ash);
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid var(--color-absolute-black);
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
  }
  tbody tr {
    border-bottom: 1px solid var(--color-absolute-black);
    cursor: pointer;
  }
  tbody tr:hover { background: #2c2c2c; }
  tbody td { padding: 12px; vertical-align: top; }
  .col-star { width: 38px; text-align: center; }
  .col-sr { width: 54px; color: var(--color-ash); font-variant-numeric: tabular-nums; }

  .college-title {
    font-family: var(--font-display);
    font-weight: 500;
    font-size: 18px;
    line-height: 1.13;
    letter-spacing: -0.45px;
    color: var(--color-bone-white);
    font-feature-settings: "blwf", "cv03", "cv04", "cv09", "cv11", "ss09", "ss10";
  }
  .college-sub { color: var(--color-ash); margin-top: 4px; }

  .star-btn {
    background: transparent;
    border: none;
    font-size: 14px;
    cursor: pointer;
    color: var(--color-ash);
    padding: 0;
  }
  .star-btn.starred { color: var(--color-bone-white); }

  .tag {
    display: inline-block;
    padding: 4px 8px;
    background: var(--color-canvas-black);
    border: 1px solid var(--color-absolute-black);
    color: var(--color-bone-white);
    white-space: nowrap;
  }
  .copy-mini, .wa-pill {
    display: inline-block;
    padding: 2px 6px;
    background: var(--color-canvas-black);
    border: 1px solid var(--color-absolute-black);
    color: var(--color-ash);
    margin-left: 6px;
    cursor: pointer;
    font-size: 11px;
  }
  .copy-mini:hover, .wa-pill:hover { color: var(--color-bone-white); text-decoration: none; }
  .muted { color: var(--color-ash); }
  mark { background: var(--color-bone-white); color: var(--color-canvas-black); padding: 0 2px; }

  /* Grid View */
  .cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: var(--spacing-10);
  }
  .college-card {
    background: var(--color-slate-surface);
    border: 1px solid var(--color-absolute-black);
    padding: var(--spacing-12);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-10);
  }
  .college-card:hover { border-color: var(--color-bone-white); }
  .card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
  .card-meta { display: grid; gap: 6px; }
  .card-footer {
    margin-top: auto;
    padding-top: 10px;
    border-top: 1px solid var(--color-absolute-black);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  /* Pagination */
  .pagination {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
    gap: 12px;
    color: var(--color-ash);
  }
  .page-btns { display: flex; gap: var(--spacing-8); align-items: center; }

  /* PostNew Bottom-Center Floating View Toggle */
  .floating-view-toggle {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--color-slate-surface);
    border: 1px solid var(--color-absolute-black);
    padding: 8px 12px;
    display: flex;
    gap: 13px;
    z-index: 30;
  }
  .floating-view-toggle button {
    background: transparent;
    border: none;
    color: var(--color-ash);
    font-family: var(--font-chrome);
    font-size: 12px;
    cursor: pointer;
    padding: 0;
  }
  .floating-view-toggle button.active {
    color: var(--color-bone-white);
    text-decoration: underline;
    text-underline-offset: 4px;
  }

  /* Slide-Over Vitrine Detail Drawer */
  .drawer-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.72);
    z-index: 50;
    display: none;
    justify-content: flex-end;
  }
  .drawer-backdrop.open { display: flex; }
  .drawer {
    width: min(560px, 100vw);
    height: 100%;
    background: var(--color-canvas-black);
    border-left: 1px solid var(--color-absolute-black);
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .drawer-nav { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
  .detail-list { display: grid; gap: 8px; }
  .detail-item {
    background: var(--color-slate-surface);
    border: 1px solid var(--color-absolute-black);
    padding: 10px 12px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
  }
  .detail-label { color: var(--color-ash); text-transform: uppercase; letter-spacing: 0.05em; }
  .detail-val { color: var(--color-bone-white); word-break: break-word; margin-top: 4px; }

  /* Minimalist Footer */
  .site-footer {
    border-top: 1px solid var(--color-absolute-black);
    background: var(--color-canvas-black);
    padding: 24px 0 72px;
    color: var(--color-ash);
  }
  .footer-inner {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
  }
  .footer-links { display: flex; flex-wrap: wrap; gap: 16px; }
  .footer-links a { color: var(--color-bone-white); }

  @media (max-width: 1120px) {
    .scroll-dots { display: none; }
  }
  @media (max-width: 900px) {
    .search-row { grid-template-columns: 1fr; }
    .cards-grid { grid-template-columns: 1fr; }
    .analytics-panel.open { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
  <nav class="top-nav" aria-label="Primary">
    <button id="navIndex" class="nav-active">Index</button>
    <button id="navMmr">MMR</button>
    <button id="navShortlist">Shortlist (<span id="navShortlistCount">0</span>)</button>
    <button id="navInsights">Insights</button>
    <a href="https://github.com/oghimanshu/Maharashtra-College-Database-2026" target="_blank" rel="noopener">GitHub</a>
  </nav>

  <div class="scroll-dots" id="scrollDots" aria-hidden="true"></div>

  <header class="vitrine-header">
    <div class="container">
      <div class="header-grid">
        <div>
          <h1 class="editorial-h1">Maharashtra College Database</h1>
          <p class="editorial-lead">10,448 institutions across Mumbai, MMR &amp; Maharashtra — Principals, +91 mobiles, Instagram &amp; affiliations.</p>
        </div>
        <div class="header-actions">
          <a class="btn-ghost" href="https://raw.githubusercontent.com/oghimanshu/Maharashtra-College-Database-2026/main/data/maharashtra_colleges.xlsx" id="excelLink" download>Excel (.xlsx)</a>
          <button class="btn-ghost" id="exportBtn">Export CSV</button>
        </div>
      </div>
      <div class="stats-strip" id="statsBar"></div>
    </div>
  </header>

  <main class="gallery-main">
    <div class="container">
      <section class="controls-vitrine">
        <div class="search-row">
          <div class="search-wrap">
            <input id="searchInput" type="text" placeholder="Press '/' to fuzzy search — e.g. 'xaviers mumbai', 'vjti', 'ruia', principal, '+91', '@handle'" autocomplete="off" />
            <button class="clear-btn" id="clearSearchBtn" title="Clear">&times;</button>
          </div>
          <select id="districtFilter"><option value="">All Districts</option></select>
          <select id="categoryFilter"><option value="">All Categories</option></select>
          <select id="sortSelect">
            <option value="relevance">Sort: Relevance</option>
            <option value="name">Sort: Name (A–Z)</option>
            <option value="district">Sort: District (A–Z)</option>
          </select>
        </div>

        <div class="pills-row">
          <span class="pill-label">Region</span>
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
          <span class="pill-label">Filter</span>
          <span class="chip" id="shortlistChip">Shortlisted (<span id="shortlistCount">0</span>)</span>
          <span class="chip" data-flag="principal">Principal</span>
          <span class="chip" data-flag="faculty_mobile">+91 Mobile</span>
          <span class="chip" data-flag="phone">Any Phone</span>
          <span class="chip" data-flag="instagram">Instagram</span>
          <span class="chip" data-flag="website">Website</span>
          <button class="btn-ghost" id="resetBtn" style="margin-left:auto;padding:5px 10px;">Reset</button>
        </div>
      </section>

      <section class="analytics-panel" id="analyticsPanel"></section>

      <div id="resultsContainer"></div>

      <div class="pagination">
        <div id="resultInfo">0 results</div>
        <div class="page-btns">
          <select id="pageSizeSelect" style="padding:7px 10px;">
            <option value="48">48 / page</option>
            <option value="96" selected>96 / page</option>
            <option value="240">240 / page</option>
          </select>
          <button class="btn-ghost" id="prevBtn">Prev</button>
          <span id="pageLabel">Page 1</span>
          <button class="btn-ghost" id="nextBtn">Next</button>
        </div>
      </div>
    </div>
  </main>

  <div class="floating-view-toggle" role="group" aria-label="View mode">
    <button id="tableViewBtn" class="active">List</button>
    <button id="cardViewBtn">Grid</button>
  </div>

  <div class="drawer-backdrop" id="drawerBackdrop">
    <aside class="drawer" id="drawerPanel">
      <div class="drawer-nav">
        <div style="display:flex;gap:8px;">
          <button class="btn-ghost" id="drawerPrev">&larr; Prev</button>
          <button class="btn-ghost" id="drawerNext">Next &rarr;</button>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="btn-ghost" id="drawerStar">Shortlist</button>
          <button class="btn-ghost" id="drawerClose">&times;</button>
        </div>
      </div>
      <div>
        <span class="tag" id="drawerCategory"></span>
        <h2 class="editorial-h1" id="drawerTitle" style="margin-top:10px;"></h2>
        <div id="drawerSub" class="muted"></div>
      </div>
      <div class="detail-list" id="drawerBody"></div>
    </aside>
  </div>

  <footer class="site-footer">
    <div class="container footer-inner">
      <div>
        Made by <span style="color:var(--color-bone-white)">Himanshu Gaur</span>
        <span style="margin:0 6px;">&bull;</span>
        <span>MIT License &bull; AISHE, JDTE Mumbai (2025) &amp; Official Websites</span>
      </div>
      <div class="footer-links">
        <a href="https://github.com/oghimanshu" target="_blank" rel="noopener">GitHub (@oghimanshu)</a>
        <a href="https://github.com/oghimanshu/Maharashtra-College-Database-2026" target="_blank" rel="noopener">Repository</a>
        <a href="mailto:wtfhimanshu@outlook.com">wtfhimanshu@outlook.com</a>
      </div>
    </div>
  </footer>

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

function initScrollDots() {
  const container = document.getElementById("scrollDots");
  container.innerHTML = Array.from({length: 10}, (_, i) => `<div class="scroll-dot ${i === 0 ? 'active' : ''}"></div>`).join("");
  const dots = container.querySelectorAll(".scroll-dot");
  window.addEventListener("scroll", () => {
    const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    const ratio = Math.min(1, Math.max(0, window.scrollY / max));
    const activeIdx = Math.min(9, Math.floor(ratio * 10));
    dots.forEach((d, idx) => d.classList.toggle("active", idx === activeIdx));
  }, { passive: true });
}

function saveShortlist() {
  localStorage.setItem("mh_college_shortlist", JSON.stringify([...state.shortlist]));
  document.getElementById("shortlistCount").textContent = state.shortlist.size;
  document.getElementById("navShortlistCount").textContent = state.shortlist.size;
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
    <span class="stat-cell">Total<strong>${COLLEGES.length.toLocaleString()}</strong></span>
    <span class="stat-cell">Districts<strong>${Object.keys(distCounts).length}</strong></span>
    <span class="stat-cell">Principals<strong>${pCount.toLocaleString()}</strong></span>
    <span class="stat-cell">+91 Mobiles<strong>${mobCount.toLocaleString()}</strong></span>
    <span class="stat-cell">Instagram<strong>${igCount.toLocaleString()}</strong></span>
    <span class="stat-cell">Websites<strong>${webCount.toLocaleString()}</strong></span>
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

function updateNavActive() {
  document.getElementById("navIndex").classList.toggle("nav-active", state.region === "all" && !state.shortlistOnly);
  document.getElementById("navMmr").classList.toggle("nav-active", state.region === "mmr" && !state.shortlistOnly);
  document.getElementById("navShortlist").classList.toggle("nav-active", state.shortlistOnly);
  document.getElementById("navInsights").classList.toggle("nav-active", state.analyticsOpen);
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
      <h3>Top Districts</h3>
      ${topD.map(([name, cnt]) => `<div class="ana-row" onclick="quickFilterDist('${esc(name)}')">
        <span class="ana-name">${esc(name)}</span>
        <div class="ana-bar-bg"><div class="ana-bar-fill" style="width:${Math.round(cnt / maxD * 100)}%"></div></div>
        <span class="ana-count">${cnt}</span>
      </div>`).join("") || '<span class="muted">No data</span>'}
    </div>
    <div class="ana-col">
      <h3>Top Categories</h3>
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
  updateNavActive();
  renderAnalytics();
  renderResults(tokens);
}

function copyText(txt, btn, ev) {
  if (ev) ev.stopPropagation();
  navigator.clipboard.writeText(txt).then(() => {
    const old = btn.textContent;
    btn.textContent = "Copied";
    setTimeout(() => { btn.textContent = old; }, 1000);
  });
}

function updateDrawerStarBtn(c) {
  const btn = document.getElementById("drawerStar");
  const starred = state.shortlist.has(c._id);
  btn.textContent = starred ? "★ Shortlisted" : "☆ Shortlist";
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
    let valHtml = val ? esc(val) : '<span class="muted">—</span>';
    if (val && label === "Official Website") valHtml = `<a href="${esc(val)}" target="_blank" rel="noopener">${esc(val)}</a>`;
    if (val && label === "Official Email ID") valHtml = `<a href="mailto:${esc(val)}">${esc(val)}</a>`;
    if (val && label === "Instagram ID") valHtml = `<a href="https://www.instagram.com/${esc(val.replace(/^@/, ''))}/" target="_blank" rel="noopener">${esc(val)}</a>`;
    if (val && label.includes("Mobile")) {
      const wa = waLink(val);
      valHtml = `<a href="tel:${esc(val.split(',')[0].trim())}">${esc(val)}</a>` + (wa ? `<a class="wa-pill" href="${wa}" target="_blank" rel="noopener">WA</a>` : "");
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
    container.innerHTML = `<div class="table-frame" style="padding:48px;text-align:center;color:var(--color-ash);">No matching colleges found.</div>`;
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
          <div style="display:flex;align-items:center;gap:6px;">
            <button class="star-btn ${starred ? 'starred' : ''}" onclick="toggleStar('${esc(c._id)}', event)">${starred ? "★" : "☆"}</button>
            <span class="tag">${esc(c.category.split(" ")[0])}</span>
          </div>
        </div>
        <div class="card-meta">
          ${c.principal_name ? `<div><span class="muted">Principal:</span> ${highlight(c.principal_name, tokens)}</div>` : ""}
          ${mob ? `<div><span>${highlight(mob, tokens)}</span>${wa ? `<a class="wa-pill" href="${wa}" target="_blank" rel="noopener" onclick="event.stopPropagation()">WA</a>` : ""}<button class="copy-mini" onclick="copyText('${esc(mob)}', this, event)">Copy</button></div>` : (phone ? `<div><span class="muted">Tel:</span> ${highlight(phone, tokens)}</div>` : "")}
          ${ig ? `<div><a href="https://www.instagram.com/${esc(ig)}/" target="_blank" rel="noopener" onclick="event.stopPropagation()">@${highlight(ig, tokens)}</a></div>` : ""}
        </div>
        <div class="card-footer">
          <span class="muted">${esc(c.aishe_code || "Details")}</span>
          ${c.website ? `<a href="${esc(c.website)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">Website &#8599;</a>` : `<span class="muted">Open &rarr;</span>`}
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
        <td class="col-star"><button class="star-btn ${starred ? 'starred' : ''}" onclick="toggleStar('${esc(c._id)}', event)">${starred ? "★" : "☆"}</button></td>
        <td class="col-sr">${c.sr_no}</td>
        <td>
          <div class="college-title">${highlight(c.name, tokens)}</div>
          <div class="college-sub">${highlight(c.district, tokens)}${c.city && c.city !== c.district ? " • " + highlight(c.city, tokens) : ""}${c.affiliation ? " • " + highlight(c.affiliation, tokens) : ""}</div>
        </td>
        <td>${c.principal_name ? highlight(c.principal_name, tokens) : '<span class="muted">—</span>'}</td>
        <td>
          ${mob ? `<div><a href="tel:${esc(mob.split(',')[0].trim())}" onclick="event.stopPropagation()">${highlight(mob, tokens)}</a>${wa ? `<a class="wa-pill" href="${wa}" target="_blank" rel="noopener" onclick="event.stopPropagation()">WA</a>` : ""}<button class="copy-mini" onclick="copyText('${esc(mob)}', this, event)">Copy</button></div>` : ""}
          ${tel ? `<div class="muted" style="margin-top:3px;">${highlight(tel, tokens)}</div>` : (!mob ? '<span class="muted">—</span>' : "")}
        </td>
        <td>${ig ? `<a href="https://www.instagram.com/${esc(ig)}/" target="_blank" rel="noopener" onclick="event.stopPropagation()">@${highlight(ig, tokens)}</a>` : '<span class="muted">—</span>'}</td>
        <td><span class="tag">${esc(c.category)}</span></td>
        <td>${c.website ? `<a href="${esc(c.website)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">Visit &#8599;</a>` : '<span class="muted">Open</span>'}</td>
      </tr>`;
    }).join("");

    container.innerHTML = `<div class="table-frame"><div class="table-scroll">
      <table>
        <thead><tr>
          <th class="col-star">★</th>
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
    total ? `${(start + 1).toLocaleString()}–${Math.min(start + state.pageSize, total).toLocaleString()} of ${total.toLocaleString()} colleges` : "0 results";
  document.getElementById("pageLabel").textContent = `Page ${state.page} / ${totalPages}`;
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

document.getElementById("navIndex").addEventListener("click", () => {
  state.region = "all"; state.shortlistOnly = false;
  document.getElementById("shortlistChip").classList.remove("active");
  document.querySelectorAll(".chip[data-region]").forEach(x => x.classList.toggle("active", x.dataset.region === "all"));
  applyFilters();
});
document.getElementById("navMmr").addEventListener("click", () => {
  state.region = "mmr"; state.shortlistOnly = false;
  document.getElementById("shortlistChip").classList.remove("active");
  document.querySelectorAll(".chip[data-region]").forEach(x => x.classList.toggle("active", x.dataset.region === "mmr"));
  applyFilters();
});
document.getElementById("navShortlist").addEventListener("click", () => {
  state.shortlistOnly = !state.shortlistOnly;
  document.getElementById("shortlistChip").classList.toggle("active", state.shortlistOnly);
  applyFilters();
});
document.getElementById("navInsights").addEventListener("click", () => {
  state.analyticsOpen = !state.analyticsOpen;
  updateNavActive();
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

initScrollDots();
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
