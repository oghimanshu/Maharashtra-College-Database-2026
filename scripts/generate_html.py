#!/usr/bin/env python3
"""
Generate the GitHub Pages web app (docs/index.html) with:
- Single unified document scroll (zero nested table scrollbars, zero extra scroll dots)
- Streamlined, non-redundant controls (single Top Bar + single compact Filter Card)
- Animated floating chromatic aurora orbs + architectural grid background
- Crisp glassmorphic cards & table with high-contrast readable typography
- Full functionality: fuzzy search ('/' shortcut + shareable URLs), Shortlist,
  WhatsApp/IG/Website links, Insights strip, and Slide-over Detail Drawer.
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
<title>Maharashtra College Database (2026) — Interactive Directory</title>
<meta name="description" content="Curated directory of 10,249 colleges across Mumbai, MMR, and Maharashtra with Principal names, +91 mobiles, Instagram IDs, and affiliations." />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%230f172a'/><text x='50' y='68' font-size='58' text-anchor='middle'>🎓</text></svg>" />
<style>
  :root {
    --bg: #0c0e14;
    --surface: rgba(23, 26, 36, 0.78);
    --surface-solid: #171a24;
    --surface-hover: rgba(34, 39, 54, 0.9);
    --border: rgba(255, 255, 255, 0.09);
    --border-strong: rgba(255, 255, 255, 0.18);
    --text: #f8fafc;
    --text-secondary: #cbd5e1;
    --muted: #94a3b8;
    --accent: #38bdf8;
    --accent-soft: rgba(56, 189, 248, 0.14);
    --green: #34d399;
    --green-soft: rgba(52, 211, 153, 0.14);
    --pink: #f472b6;
    --amber: #fbbf24;
    --amber-soft: rgba(251, 191, 36, 0.15);
    --font-display: 'Inter Tight', ui-sans-serif, system-ui, -apple-system, sans-serif;
    --font-sans: 'Inter', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  }

  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-sans);
    font-size: 14px;
    font-weight: 400;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }

  /* Animated Aurora & Architectural Grid Background */
  .bg-stage {
    position: fixed;
    inset: 0;
    z-index: -1;
    overflow: hidden;
    pointer-events: none;
    background: #0c0e14;
  }
  .bg-grid {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(to right, rgba(255, 255, 255, 0.035) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
    background-size: 56px 56px;
    mask-image: radial-gradient(ellipse 85% 70% at 50% 25%, #000 40%, transparent 100%);
    -webkit-mask-image: radial-gradient(ellipse 85% 70% at 50% 25%, #000 40%, transparent 100%);
  }
  .orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(110px);
    opacity: 0.34;
    will-change: transform;
  }
  .orb-1 {
    width: 560px; height: 560px;
    background: radial-gradient(circle, #3b82f6, #1d4ed8 60%, transparent);
    top: -160px; left: -100px;
    animation: driftA 22s ease-in-out infinite alternate;
  }
  .orb-2 {
    width: 520px; height: 520px;
    background: radial-gradient(circle, #ec4899, #9333ea 60%, transparent);
    top: 8%; right: -140px;
    animation: driftB 26s ease-in-out infinite alternate;
  }
  .orb-3 {
    width: 480px; height: 480px;
    background: radial-gradient(circle, #10b981, #06b6d4 60%, transparent);
    bottom: -140px; left: 32%;
    opacity: 0.22;
    animation: driftC 28s ease-in-out infinite alternate;
  }
  @keyframes driftA {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(110px, 80px) scale(1.12); }
  }
  @keyframes driftB {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(-120px, 95px) scale(1.1); }
  }
  @keyframes driftC {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(80px, -90px) scale(1.15); }
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }
  @media (prefers-reduced-motion: reduce) {
    .orb { animation: none; }
    * { transition: none !important; animation: none !important; }
  }

  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }

  .container {
    width: 100%;
    max-width: 1360px;
    margin: 0 auto;
    padding: 0 24px;
  }

  /* Unified Hero Header */
  .vitrine-header { padding: 32px 0 22px; }
  .header-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: flex-end;
    gap: 20px;
  }
  .brand-row { display: flex; align-items: center; gap: 14px; margin-bottom: 6px; }
  .logo-badge {
    width: 42px; height: 42px; border-radius: 12px;
    background: linear-gradient(135deg, #2563eb, #ec4899);
    display: grid; place-items: center; font-size: 20px;
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
  }
  .editorial-h1 {
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 26px;
    line-height: 1.15;
    letter-spacing: -0.025em;
    margin: 0;
    color: var(--text);
  }
  .editorial-lead {
    font-size: 14.5px;
    line-height: 1.5;
    color: var(--text-secondary);
    margin: 4px 0 0;
    max-width: 680px;
  }

  .header-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
    align-items: center;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    border-radius: 10px;
    background: var(--surface);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    color: var(--text);
    border: 1px solid var(--border);
    font-family: var(--font-sans);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    transition: all .18s ease;
  }
  .btn:hover {
    border-color: var(--border-strong);
    background: var(--surface-hover);
    transform: translateY(-1px);
    text-decoration: none;
  }
  .btn-primary {
    background: linear-gradient(135deg, #2563eb, #6366f1);
    border: none;
    color: #fff;
    font-weight: 600;
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3);
  }
  .btn-primary:hover {
    filter: brightness(1.1);
    background: linear-gradient(135deg, #2563eb, #6366f1);
  }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

  .stats-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
    margin-top: 18px;
  }
  .stat-cell {
    background: var(--surface);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 5px 13px;
    font-size: 12.5px;
    color: var(--muted);
  }
  .stat-cell strong {
    color: var(--text);
    font-weight: 600;
    margin-left: 5px;
  }

  /* Main Section — Single Unified Scroll */
  .gallery-main { padding: 4px 0 96px; }

  .controls-vitrine {
    background: var(--surface);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 15px;
    display: grid;
    gap: 12px;
    margin-bottom: 20px;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
  }
  .search-row {
    display: grid;
    grid-template-columns: 1fr auto auto auto;
    gap: 10px;
    align-items: center;
  }
  .search-wrap { position: relative; display: flex; align-items: center; }
  .search-icon { position: absolute; left: 14px; color: var(--muted); pointer-events: none; font-size: 15px; }
  .search-wrap input {
    width: 100%;
    padding: 10px 36px 10px 40px;
    background: rgba(12, 14, 20, 0.7);
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text);
    font-family: var(--font-sans);
    font-size: 14px;
    outline: none;
    transition: border-color .18s, box-shadow .18s;
  }
  .search-wrap input::placeholder { color: var(--muted); }
  .search-wrap input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-soft);
  }
  .clear-btn {
    position: absolute;
    right: 10px;
    background: transparent;
    border: none;
    color: var(--muted);
    font-size: 18px;
    cursor: pointer;
    display: none;
  }
  .clear-btn.visible { display: block; }
  .clear-btn:hover { color: var(--text); }

  select {
    background: rgba(12, 14, 20, 0.7);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 12px;
    font-family: var(--font-sans);
    font-size: 13px;
    cursor: pointer;
    outline: none;
  }
  select:focus { border-color: var(--accent); }

  .pills-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
  }
  .pill-label {
    color: var(--muted);
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-right: 4px;
  }
  .chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(12, 14, 20, 0.55);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 5px 12px;
    font-size: 12.5px;
    color: var(--text-secondary);
    cursor: pointer;
    user-select: none;
    transition: all .15s;
  }
  .chip:hover { border-color: var(--border-strong); color: var(--text); }
  .chip.active {
    background: var(--accent-soft);
    border-color: var(--accent);
    color: var(--accent);
    font-weight: 500;
  }
  .chip-star.active {
    background: var(--amber-soft);
    border-color: var(--amber);
    color: var(--amber);
  }

  /* Insights Panel */
  .analytics-panel {
    background: var(--surface);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 20px;
    display: none;
  }
  .analytics-panel.open {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    animation: fadeUp .2s ease;
  }
  .ana-col h3 {
    margin: 0 0 12px;
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 16px;
    color: var(--text);
  }
  .ana-row {
    display: grid;
    grid-template-columns: 170px 1fr 48px;
    gap: 10px;
    align-items: center;
    margin-bottom: 9px;
    font-size: 13px;
    cursor: pointer;
  }
  .ana-row:hover .ana-name { color: var(--accent); }
  .ana-name { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--text-secondary); }
  .ana-bar-bg { height: 7px; border-radius: 999px; background: rgba(255, 255, 255, 0.07); overflow: hidden; }
  .ana-bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--accent), var(--pink)); }
  .ana-count { text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }

  /* Unified Table View (No nested scrollbars) */
  .table-frame {
    background: var(--surface);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: clip;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
    table-layout: fixed;
  }
  thead th {
    position: sticky;
    top: 0;
    z-index: 2;
    background: rgba(15, 18, 28, 0.96);
    backdrop-filter: blur(12px);
    color: var(--muted);
    text-align: left;
    padding: 12px 12px;
    border-bottom: 1px solid var(--border);
    font-size: 11.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  tbody tr {
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    transition: background .12s;
  }
  tbody tr:last-child { border-bottom: none; }
  tbody tr:hover { background: var(--surface-hover); }
  tbody td {
    padding: 13px 12px;
    vertical-align: top;
    word-wrap: break-word;
    overflow-wrap: anywhere;
  }
  .col-star { width: 40px; text-align: center; }
  .col-sr { width: 54px; color: var(--muted); font-variant-numeric: tabular-nums; }
  .col-college { width: 30%; }
  .col-principal { width: 15%; }
  .col-phone { width: 20%; }
  .col-ig { width: 14%; }
  .col-cat { width: 14%; }
  .col-site { width: 64px; }

  .college-title {
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 15px;
    line-height: 1.3;
    color: var(--text);
  }
  .college-sub { color: var(--muted); font-size: 12.5px; margin-top: 3px; }

  .star-btn {
    background: transparent;
    border: none;
    font-size: 16px;
    cursor: pointer;
    color: var(--muted);
    padding: 0;
    transition: transform .15s;
  }
  .star-btn:hover { transform: scale(1.2); color: var(--amber); }
  .star-btn.starred { color: var(--amber); }

  .tag {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 6px;
    background: var(--accent-soft);
    color: var(--accent);
    font-size: 11.5px;
    font-weight: 500;
  }
  .ig-link { color: var(--pink); font-weight: 500; }
  .mob-link { color: var(--green); font-weight: 600; font-variant-numeric: tabular-nums; }
  .wa-pill {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 5px;
    background: var(--green-soft);
    color: var(--green);
    margin-left: 5px;
    font-size: 11px;
    font-weight: 600;
  }
  .wa-pill:hover { filter: brightness(1.1); text-decoration: none; }
  .copy-mini {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 5px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid var(--border);
    color: var(--text-secondary);
    margin-left: 4px;
    cursor: pointer;
    font-size: 11px;
  }
  .copy-mini:hover { border-color: var(--accent); color: var(--text); }
  .muted { color: var(--muted); }
  mark { background: rgba(251, 191, 36, 0.3); color: #fff; padding: 0 3px; border-radius: 3px; }

  /* Grid View */
  .cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 14px;
  }
  .college-card {
    background: var(--surface);
    backdrop-filter: blur(14px);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: 10px;
    transition: transform .18s ease, border-color .18s ease, background .18s ease;
    animation: fadeUp .25s ease backwards;
  }
  .college-card:hover {
    transform: translateY(-3px);
    border-color: var(--accent);
    background: var(--surface-hover);
  }
  .card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
  .card-meta { display: grid; gap: 6px; font-size: 13.5px; }
  .card-footer {
    margin-top: auto;
    padding-top: 10px;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
  }

  /* Pagination */
  .pagination {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
    gap: 12px;
    color: var(--text-secondary);
    font-size: 13.5px;
  }
  .page-btns { display: flex; gap: 8px; align-items: center; }

  /* Bottom-Center Floating View Toggle */
  .floating-view-toggle {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(23, 26, 36, 0.92);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-strong);
    border-radius: 999px;
    padding: 5px 7px;
    display: flex;
    gap: 4px;
    z-index: 30;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
  }
  .floating-view-toggle button {
    background: transparent;
    border: none;
    border-radius: 999px;
    color: var(--muted);
    font-family: var(--font-sans);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    padding: 6px 14px;
    transition: all .15s;
  }
  .floating-view-toggle button.active {
    background: var(--accent);
    color: #0c0e14;
    font-weight: 600;
  }

  /* Slide-Over Detail Drawer */
  .drawer-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(5, 7, 12, 0.72);
    backdrop-filter: blur(4px);
    z-index: 50;
    display: none;
    justify-content: flex-end;
  }
  .drawer-backdrop.open { display: flex; }
  .drawer {
    width: min(560px, 100vw);
    height: 100%;
    background: var(--surface-solid);
    border-left: 1px solid var(--border);
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    box-shadow: -16px 0 48px rgba(0, 0, 0, 0.5);
  }
  .drawer-nav { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
  .detail-list { display: grid; gap: 9px; }
  .detail-item {
    background: rgba(12, 14, 20, 0.6);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 11px 13px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
  }
  .detail-label { color: var(--muted); font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.05em; }
  .detail-val { color: var(--text); font-size: 14px; word-break: break-word; margin-top: 3px; }

  /* Footer */
  .site-footer {
    border-top: 1px solid var(--border);
    background: rgba(12, 14, 20, 0.85);
    backdrop-filter: blur(12px);
    padding: 24px 0 76px;
    color: var(--muted);
    font-size: 13.5px;
  }
  .footer-inner {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
  }
  .footer-links { display: flex; flex-wrap: wrap; gap: 16px; }

  @media (max-width: 900px) {
    .search-row { grid-template-columns: 1fr; }
    .cards-grid { grid-template-columns: 1fr; }
    .analytics-panel.open { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
  <div class="bg-stage" aria-hidden="true">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    <div class="bg-grid"></div>
  </div>

  <header class="vitrine-header">
    <div class="container">
      <div class="header-grid">
        <div>
          <div class="brand-row">
            <div class="logo-badge">&#127891;</div>
            <h1 class="editorial-h1">Maharashtra College Database</h1>
          </div>
          <p class="editorial-lead">10,249 verified colleges across Mumbai, MMR &amp; Maharashtra — Principals, +91 mobiles, Instagram IDs &amp; affiliations.</p>
        </div>
        <div class="header-actions">
          <button class="btn" id="insightsBtn">&#128200; Insights</button>
          <a class="btn" href="https://github.com/oghimanshu/Maharashtra-College-Database-2026" target="_blank" rel="noopener">&#128187; GitHub</a>
          <a class="btn" href="https://raw.githubusercontent.com/oghimanshu/Maharashtra-College-Database-2026/main/data/maharashtra_colleges.xlsx" id="excelLink" download>&#128202; Excel (.xlsx)</a>
          <button class="btn btn-primary" id="exportBtn">&#11015; Export CSV</button>
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
            <span class="search-icon">&#128269;</span>
            <input id="searchInput" type="text" placeholder="Press '/' to fuzzy search — e.g. 'xaviers mumbai', 'vjti', 'ruia', principal, '+91', '@handle'" autocomplete="off" />
            <button class="clear-btn" id="clearSearchBtn" title="Clear">&times;</button>
          </div>
          <select id="districtFilter"><option value="">All Districts (Maharashtra)</option></select>
          <select id="categoryFilter"><option value="">All Categories</option></select>
          <select id="sortSelect">
            <option value="relevance">Sort: Relevance</option>
            <option value="name">Sort: Name (A–Z)</option>
            <option value="district">Sort: District (A–Z)</option>
          </select>
        </div>

        <div class="pills-row">
          <span class="pill-label">Quick Filter</span>
          <span class="chip" id="mmrChip">Mumbai &amp; MMR</span>
          <span class="chip chip-star" id="shortlistChip">&#9733; Shortlisted (<span id="shortlistCount">0</span>)</span>
          <span class="chip" data-flag="principal">Principal Name</span>
          <span class="chip" data-flag="faculty_mobile">+91 Mobile</span>
          <span class="chip" data-flag="phone">Any Phone</span>
          <span class="chip" data-flag="instagram">Instagram ID</span>
          <span class="chip" data-flag="website">Website</span>
          <button class="btn" id="resetBtn" style="margin-left:auto;padding:5px 12px;font-size:12.5px;">Reset</button>
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
          <button class="btn" id="prevBtn" style="padding:7px 12px;">Prev</button>
          <span id="pageLabel">Page 1</span>
          <button class="btn" id="nextBtn" style="padding:7px 12px;">Next</button>
        </div>
      </div>
    </div>
  </main>

  <div class="floating-view-toggle" role="group" aria-label="View mode">
    <button id="tableViewBtn" class="active">Table View</button>
    <button id="cardViewBtn">Card Grid</button>
  </div>

  <div class="drawer-backdrop" id="drawerBackdrop">
    <aside class="drawer" id="drawerPanel">
      <div class="drawer-nav">
        <div style="display:flex;gap:8px;">
          <button class="btn" id="drawerPrev" style="padding:6px 12px;">&larr; Prev</button>
          <button class="btn" id="drawerNext" style="padding:6px 12px;">Next &rarr;</button>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="btn" id="drawerStar" style="padding:6px 12px;">&#9734; Shortlist</button>
          <button class="btn" id="drawerClose" style="padding:6px 12px;">&times;</button>
        </div>
      </div>
      <div>
        <span class="tag" id="drawerCategory"></span>
        <h2 class="editorial-h1" id="drawerTitle" style="font-size:21px;margin-top:10px;"></h2>
        <div id="drawerSub" class="muted" style="font-size:13.5px;margin-top:4px;"></div>
      </div>
      <div class="detail-list" id="drawerBody"></div>
    </aside>
  </div>

  <footer class="site-footer">
    <div class="container footer-inner">
      <div>
        Made with &#10084;&#65039; by <strong style="color:var(--text)">Himanshu Gaur</strong>
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
  mmrOnly: false,
  district: "",
  category: "",
  sort: "relevance",
  view: window.innerWidth < 860 ? "cards" : "table",
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
  if (state.mmrOnly) p.set("mmr", "1");
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
  if (p.get("mmr") === "1") {
    state.mmrOnly = true;
    document.getElementById("mmrChip").classList.add("active");
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
    <span class="stat-cell">Colleges<strong>${COLLEGES.length.toLocaleString()}</strong></span>
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
    if (state.mmrOnly && !MMR_DISTS.has(c.district)) continue;
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
  btn.textContent = starred ? "★ Shortlisted" : "☆ Shortlist";
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
    container.innerHTML = `<div class="table-frame" style="padding:48px;text-align:center;color:var(--muted);">No matching colleges found. Try a broader search or reset filters.</div>`;
  } else if (state.view === "cards") {
    container.innerHTML = `<div class="cards-grid">` + slice.map((c, idx) => {
      const ig = (c.instagram_id || "").replace(/^@/, "");
      const mob = c.faculty_mobile || "";
      const wa = waLink(mob);
      const phone = c.college_phone || c.principal_phone || "";
      const starred = state.shortlist.has(c._id);
      const delay = Math.min(idx, 12) * 20;
      return `<article class="college-card" style="animation-delay:${delay}ms" onclick="openDrawer(${c.sr_no})">
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
          ${c.principal_name ? `<div><span class="muted">Principal:</span> <strong style="color:var(--text)">${highlight(c.principal_name, tokens)}</strong></div>` : ""}
          ${mob ? `<div><a class="mob-link" href="tel:${esc(mob.split(',')[0].trim())}" onclick="event.stopPropagation()">${highlight(mob, tokens)}</a>${wa ? `<a class="wa-pill" href="${wa}" target="_blank" rel="noopener" onclick="event.stopPropagation()">WA &#8599;</a>` : ""}<button class="copy-mini" onclick="copyText('${esc(mob)}', this, event)">Copy</button></div>` : (phone ? `<div><span class="muted">Tel:</span> <span style="color:var(--text-secondary)">${highlight(phone, tokens)}</span></div>` : "")}
          ${ig ? `<div><a class="ig-link" href="https://www.instagram.com/${esc(ig)}/" target="_blank" rel="noopener" onclick="event.stopPropagation()">@${highlight(ig, tokens)}</a></div>` : ""}
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
        <td class="col-star"><button class="star-btn ${starred ? 'starred' : ''}" onclick="toggleStar('${esc(c._id)}', event)">${starred ? "★" : "☆"}</button></td>
        <td class="col-sr">${c.sr_no}</td>
        <td class="col-college">
          <div class="college-title">${highlight(c.name, tokens)}</div>
          <div class="college-sub">${highlight(c.district, tokens)}${c.city && c.city !== c.district ? " • " + highlight(c.city, tokens) : ""}${c.affiliation ? " • " + highlight(c.affiliation, tokens) : ""}</div>
        </td>
        <td class="col-principal" style="color:var(--text-secondary)">${c.principal_name ? highlight(c.principal_name, tokens) : '<span class="muted">—</span>'}</td>
        <td class="col-phone">
          ${mob ? `<div><a class="mob-link" href="tel:${esc(mob.split(',')[0].trim())}" onclick="event.stopPropagation()">${highlight(mob, tokens)}</a>${wa ? `<a class="wa-pill" href="${wa}" target="_blank" rel="noopener" onclick="event.stopPropagation()">WA</a>` : ""}<button class="copy-mini" onclick="copyText('${esc(mob)}', this, event)">Copy</button></div>` : ""}
          ${tel ? `<div class="muted" style="margin-top:3px;font-size:12.5px;">${highlight(tel, tokens)}</div>` : (!mob ? '<span class="muted">—</span>' : "")}
        </td>
        <td class="col-ig">${ig ? `<a class="ig-link" href="https://www.instagram.com/${esc(ig)}/" target="_blank" rel="noopener" onclick="event.stopPropagation()">@${highlight(ig, tokens)}</a>` : '<span class="muted">—</span>'}</td>
        <td class="col-cat"><span class="tag">${esc(c.category.split(" (")[0])}</span></td>
        <td class="col-site">${c.website ? `<a href="${esc(c.website)}" target="_blank" rel="noopener" onclick="event.stopPropagation()">Visit &#8599;</a>` : '<span class="muted">Open</span>'}</td>
      </tr>`;
    }).join("");

    container.innerHTML = `<div class="table-frame">
      <table>
        <thead><tr>
          <th class="col-star">★</th>
          <th class="col-sr">#</th>
          <th class="col-college">College &amp; Location</th>
          <th class="col-principal">Principal</th>
          <th class="col-phone">+91 Mobile &amp; Phone</th>
          <th class="col-ig">Instagram</th>
          <th class="col-cat">Category</th>
          <th class="col-site">Site</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
  }

  document.getElementById("resultInfo").textContent =
    total ? `Showing ${(start + 1).toLocaleString()}–${Math.min(start + state.pageSize, total).toLocaleString()} of ${total.toLocaleString()} colleges` : "0 results";
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

document.getElementById("insightsBtn").addEventListener("click", () => {
  state.analyticsOpen = !state.analyticsOpen;
  document.getElementById("insightsBtn").style.borderColor = state.analyticsOpen ? "var(--accent)" : "";
  renderAnalytics();
});

document.getElementById("mmrChip").addEventListener("click", () => {
  state.mmrOnly = !state.mmrOnly;
  document.getElementById("mmrChip").classList.toggle("active", state.mmrOnly);
  applyFilters();
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

document.querySelectorAll(".chip[data-flag]").forEach(ch => {
  ch.addEventListener("click", () => {
    const f = ch.dataset.flag;
    if (state.flags.has(f)) { state.flags.delete(f); ch.classList.remove("active"); }
    else { state.flags.add(f); ch.classList.add("active"); }
    applyFilters();
  });
});

document.getElementById("resetBtn").addEventListener("click", () => {
  state.query = ""; state.mmrOnly = false; state.district = ""; state.category = ""; state.sort = "relevance";
  state.shortlistOnly = false; state.flags.clear();
  searchEl.value = ""; clearBtn.classList.remove("visible");
  document.getElementById("districtFilter").value = "";
  document.getElementById("categoryFilter").value = "";
  document.getElementById("sortSelect").value = "relevance";
  document.getElementById("mmrChip").classList.remove("active");
  document.getElementById("shortlistChip").classList.remove("active");
  document.querySelectorAll(".chip[data-flag]").forEach(x => x.classList.remove("active"));
  applyFilters();
});

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
