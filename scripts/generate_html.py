#!/usr/bin/env python3
"""
Generate a single self-contained offline HTML directory with instant fuzzy search,
district/category/contact filters, pagination, and filtered CSV export.
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
<title>Maharashtra Colleges Database — Fuzzy Search</title>
<style>
  :root {
    --bg: #0f172a;
    --surface: #1e293b;
    --surface-2: #273549;
    --border: #334155;
    --text: #f1f5f9;
    --muted: #94a3b8;
    --accent: #38bdf8;
    --accent-2: #818cf8;
    --green: #34d399;
    --pink: #f472b6;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.45;
  }
  .container { max-width: 1520px; margin: 0 auto; padding: 20px; }
  header {
    display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;
    gap: 12px; margin-bottom: 18px;
  }
  h1 { margin: 0; font-size: 1.5rem; letter-spacing: -0.02em; }
  .subtitle { color: var(--muted); font-size: 0.88rem; margin-top: 2px; }
  .stats-bar { display: flex; flex-wrap: wrap; gap: 10px; }
  .stat-pill {
    background: var(--surface); border: 1px solid var(--border);
    padding: 6px 12px; border-radius: 999px; font-size: 0.82rem; color: var(--muted);
  }
  .stat-pill strong { color: var(--text); }

  .controls {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 14px; margin-bottom: 16px;
    display: grid; gap: 12px;
  }
  .search-row {
    display: grid; grid-template-columns: 1fr auto auto; gap: 10px; align-items: center;
  }
  .search-box {
    position: relative; display: flex; align-items: center;
  }
  .search-box input {
    width: 100%; padding: 11px 14px 11px 38px;
    background: var(--bg); border: 1px solid var(--border); border-radius: 8px;
    color: var(--text); font-size: 0.96rem; outline: none;
    transition: border-color .15s;
  }
  .search-box input:focus { border-color: var(--accent); }
  .search-icon {
    position: absolute; left: 12px; color: var(--muted); pointer-events: none; font-size: 1rem;
  }
  .filters-row {
    display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
  }
  select, button {
    background: var(--bg); color: var(--text); border: 1px solid var(--border);
    border-radius: 8px; padding: 8px 12px; font-size: 0.86rem; cursor: pointer;
  }
  select:focus, button:focus { outline: none; border-color: var(--accent); }
  .btn-primary {
    background: linear-gradient(135deg, #0284c7, #4f46e5);
    border: none; font-weight: 600; color: #fff;
  }
  .btn-primary:hover { filter: brightness(1.1); }
  .chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--bg); border: 1px solid var(--border);
    padding: 6px 11px; border-radius: 999px; font-size: 0.82rem; cursor: pointer;
    user-select: none; color: var(--muted);
  }
  .chip.active {
    background: rgba(56, 189, 248, 0.14); border-color: var(--accent); color: var(--accent);
  }

  .table-wrap {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; overflow: auto; max-height: 70vh;
  }
  table { width: 100%; border-collapse: collapse; font-size: 0.85rem; min-width: 1250px; }
  thead th {
    position: sticky; top: 0; z-index: 2;
    background: #162235; color: #cbd5e1; text-align: left;
    padding: 11px 12px; border-bottom: 1px solid var(--border);
    white-space: nowrap; font-weight: 600;
  }
  tbody td {
    padding: 10px 12px; border-bottom: 1px solid rgba(51, 65, 85, 0.55);
    vertical-align: top;
  }
  tbody tr:hover { background: var(--surface-2); }
  .col-sr { width: 64px; color: var(--muted); text-align: center; }
  .col-name { min-width: 260px; font-weight: 600; color: #f8fafc; }
  .badge {
    display: inline-block; padding: 2px 8px; border-radius: 6px;
    font-size: 0.74rem; background: rgba(129, 140, 248, 0.16); color: #c7d2fe;
    white-space: nowrap;
  }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  .ig-link { color: var(--pink); }
  .copy-btn {
    background: transparent; border: 1px solid var(--border); color: var(--muted);
    padding: 1px 6px; font-size: 0.72rem; border-radius: 4px; margin-left: 6px;
  }
  .copy-btn:hover { color: var(--text); border-color: var(--accent); }
  mark {
    background: rgba(56, 189, 248, 0.28); color: #fff; padding: 0 2px; border-radius: 3px;
  }
  .muted { color: var(--muted); }
  .pagination {
    display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;
    margin-top: 14px; gap: 10px; font-size: 0.86rem; color: var(--muted);
  }
  .page-btns { display: flex; gap: 6px; align-items: center; }
  .page-btns button:disabled { opacity: 0.4; cursor: not-allowed; }
  @media (max-width: 768px) {
    .search-row { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<div class="container">
  <header>
    <div>
      <h1>Maharashtra Colleges &amp; Institutions Directory</h1>
      <div class="subtitle">Fuzzy search across College Name, Principal, Phone, Instagram, District, Affiliation &amp; AISHE Code</div>
    </div>
    <div class="stats-bar" id="statsBar"></div>
  </header>

  <section class="controls">
    <div class="search-row">
      <div class="search-box">
        <span class="search-icon">&#128269;</span>
        <input id="searchInput" type="text" placeholder="Fuzzy search... e.g. 'xaviers mumbai', 'vjti', 'coep pune', 'pharmacy nagpur', principal name, or code" autocomplete="off" />
      </div>
      <select id="sortSelect">
        <option value="relevance">Sort: Relevance / Enriched First</option>
        <option value="name">Sort: College Name (A–Z)</option>
        <option value="district">Sort: District (A–Z)</option>
      </select>
      <button class="btn-primary" id="exportBtn">Export Filtered CSV</button>
    </div>

    <div class="filters-row">
      <select id="districtFilter"><option value="">All Districts (Maharashtra)</option></select>
      <select id="categoryFilter"><option value="">All Categories / Streams</option></select>
      <span class="chip" data-flag="principal">Has Principal</span>
      <span class="chip" data-flag="phone">Has Phone</span>
      <span class="chip" data-flag="instagram">Has Instagram</span>
      <span class="chip" data-flag="website">Has Website</span>
      <button id="resetBtn">Reset</button>
    </div>
  </section>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th class="col-sr">Sr. No.</th>
          <th>Name of the College</th>
          <th>Principal Name</th>
          <th>College Phone</th>
          <th>Principal Phone</th>
          <th>Faculty / Personal (+91)</th>
          <th>Instagram ID</th>
          <th>District</th>
          <th>City / Area</th>
          <th>Category / Stream</th>
          <th>University / Board Affiliation</th>
          <th>Management</th>
          <th>Email</th>
          <th>Website</th>
          <th>Address</th>
          <th>Code</th>
          <th>Data Source / Verification</th>
        </tr>
      </thead>
      <tbody id="tableBody"></tbody>
    </table>
  </div>

  <div class="pagination">
    <div id="resultInfo">Showing 0 results</div>
    <div class="page-btns">
      <select id="pageSizeSelect">
        <option value="50">50 / page</option>
        <option value="100" selected>100 / page</option>
        <option value="250">250 / page</option>
      </select>
      <button id="prevBtn">Prev</button>
      <span id="pageLabel">Page 1</span>
      <button id="nextBtn">Next</button>
    </div>
  </div>
</div>

<script>
const COLLEGES = __DATA_JSON__;

// Precompute lowercase search blob for fast fuzzy scoring
for (const c of COLLEGES) {
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
  let qi = 0, gaps = 0, firstIdx = -1;
  for (let ti = 0; ti < target.length && qi < query.length; ti++) {
    if (target[ti] === query[qi]) {
      if (firstIdx === -1) firstIdx = ti;
      qi++;
    } else if (qi > 0) {
      gaps++;
    }
  }
  if (qi < query.length) return 0;
  return Math.max(5, 40 - Math.min(35, gaps));
}

function fuzzyScore(item, tokens) {
  if (!tokens.length) return 1;
  let total = 0;
  const words = item._blob.split(/[^a-z0-9]+/).filter(Boolean);

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
      if (!bestFuzzy) {
        bestFuzzy = subsequenceScore(tok, item._nameL);
      }
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

const state = {
  query: "",
  district: "",
  category: "",
  sort: "relevance",
  flags: new Set(),
  page: 1,
  pageSize: 100,
  filtered: COLLEGES,
};

function initFilters() {
  const distCounts = {};
  const catCounts = {};
  let pCount = 0, phCount = 0, igCount = 0, webCount = 0;

  for (const c of COLLEGES) {
    if (c.district) distCounts[c.district] = (distCounts[c.district] || 0) + 1;
    if (c.category) catCounts[c.category] = (catCounts[c.category] || 0) + 1;
    if (c.principal_name) pCount++;
    if (c.college_phone) phCount++;
    if (c.instagram_id) igCount++;
    if (c.website) webCount++;
  }

  document.getElementById("statsBar").innerHTML = `
    <span class="stat-pill">Total: <strong>${COLLEGES.length.toLocaleString()}</strong></span>
    <span class="stat-pill">Districts: <strong>${Object.keys(distCounts).length}</strong></span>
    <span class="stat-pill">Principals: <strong>${pCount.toLocaleString()}</strong></span>
    <span class="stat-pill">Phones: <strong>${phCount.toLocaleString()}</strong></span>
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
}

function applyFilters() {
  const tokens = state.query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  const res = [];

  for (const c of COLLEGES) {
    if (state.district && c.district !== state.district) continue;
    if (state.category && c.category !== state.category) continue;
    if (state.flags.has("principal") && !c.principal_name) continue;
    if (state.flags.has("phone") && !c.college_phone && !c.principal_phone) continue;
    if (state.flags.has("instagram") && !c.instagram_id) continue;
    if (state.flags.has("website") && !c.website) continue;

    const score = fuzzyScore(c, tokens);
    if (score > 0) {
      res.push({ item: c, score });
    }
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
  renderTable(tokens);
}

function copyText(txt, btn) {
  navigator.clipboard.writeText(txt).then(() => {
    const old = btn.textContent;
    btn.textContent = "Copied";
    setTimeout(() => { btn.textContent = old; }, 1000);
  });
}

function renderTable(tokens = state.query.trim().toLowerCase().split(/\s+/).filter(Boolean)) {
  const tbody = document.getElementById("tableBody");
  const total = state.filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / state.pageSize));
  if (state.page > totalPages) state.page = totalPages;

  const start = (state.page - 1) * state.pageSize;
  const slice = state.filtered.slice(start, start + state.pageSize);

  const html = slice.map(c => {
    const igHandle = (c.instagram_id || "").replace(/^@/, "");
    const igHtml = igHandle
      ? `<a class="ig-link" href="https://www.instagram.com/${esc(igHandle)}/" target="_blank" rel="noopener">@${highlight(igHandle, tokens)}</a>`
      : `<span class="muted">—</span>`;
    const webHtml = c.website
      ? `<a href="${esc(c.website)}" target="_blank" rel="noopener">${esc(c.website.replace(/^https?:\/\//, ""))}</a>`
      : `<span class="muted">—</span>`;
    const emailHtml = c.email
      ? `<a href="mailto:${esc(c.email)}">${highlight(c.email, tokens)}</a>`
      : `<span class="muted">—</span>`;
    const phHtml = c.college_phone
      ? `<a href="tel:${esc(c.college_phone)}">${highlight(c.college_phone, tokens)}</a><button class="copy-btn" onclick="copyText('${esc(c.college_phone)}', this)">Copy</button>`
      : `<span class="muted">—</span>`;
    const pPhHtml = c.principal_phone
      ? `<a href="tel:${esc(c.principal_phone)}">${highlight(c.principal_phone, tokens)}</a>`
      : `<span class="muted">—</span>`;
    const fMobHtml = c.faculty_mobile
      ? `<a href="tel:${esc(c.faculty_mobile.split(',')[0].trim())}">${highlight(c.faculty_mobile, tokens)}</a><button class="copy-btn" onclick="copyText('${esc(c.faculty_mobile)}', this)">Copy</button>`
      : `<span class="muted">—</span>`;

    return `<tr>
      <td class="col-sr">${c.sr_no}</td>
      <td class="col-name">${highlight(c.name, tokens)}</td>
      <td>${c.principal_name ? highlight(c.principal_name, tokens) : '<span class="muted">—</span>'}</td>
      <td>${phHtml}</td>
      <td>${pPhHtml}</td>
      <td>${fMobHtml}</td>
      <td>${igHtml}</td>
      <td>${highlight(c.district, tokens)}</td>
      <td>${highlight(c.city, tokens)}</td>
      <td><span class="badge">${esc(c.category)}</span></td>
      <td>${c.affiliation ? highlight(c.affiliation, tokens) : '<span class="muted">—</span>'}</td>
      <td>${esc(c.management_type) || '<span class="muted">—</span>'}</td>
      <td>${emailHtml}</td>
      <td>${webHtml}</td>
      <td>${c.address ? highlight(c.address, tokens) : '<span class="muted">—</span>'}</td>
      <td>${c.aishe_code ? highlight(c.aishe_code, tokens) : '<span class="muted">—</span>'}</td>
      <td><span class="badge">${esc(c.verification_source || 'AISHE')}</span></td>
    </tr>`;
  }).join("");

  tbody.innerHTML = html || `<tr><td colspan="16" style="text-align:center;padding:30px;color:#94a3b8;">No matching colleges found. Try a broader search or reset filters.</td></tr>`;

  document.getElementById("resultInfo").textContent =
    total ? `Showing ${(start + 1).toLocaleString()}–${Math.min(start + state.pageSize, total).toLocaleString()} of ${total.toLocaleString()} colleges` : "0 results";
  document.getElementById("pageLabel").textContent = `Page ${state.page} of ${totalPages}`;
  document.getElementById("prevBtn").disabled = state.page <= 1;
  document.getElementById("nextBtn").disabled = state.page >= totalPages;
}

function exportFilteredCsv() {
  const headers = [
    "Sr. No.", "Name of the College", "Principal Name", "Phone Number of the College",
    "Phone Number of the Principal", "Faculty / Personal Mobile (+91)", "Instagram ID", "District", "City / Area",
    "Category / Stream", "University / Board Affiliation", "Management Type",
    "Official Email ID", "Official Website", "Full Address & Pincode", "AISHE / DTE Code", "Data Source / Verification"
  ];
  const keys = [
    "sr_no", "name", "principal_name", "college_phone", "principal_phone", "faculty_mobile",
    "instagram_id", "district", "city", "category", "affiliation",
    "management_type", "email", "website", "address", "aishe_code", "verification_source"
  ];
  const rows = [headers.join(",")];
  for (const c of state.filtered) {
    rows.push(keys.map(k => `"${String(c[k] || "").replace(/"/g, '""')}"`).join(","));
  }
  const blob = new Blob(["\uFEFF" + rows.join("\n")], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "maharashtra_colleges_filtered.csv";
  a.click();
}

let debounceTimer;
document.getElementById("searchInput").addEventListener("input", e => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    state.query = e.target.value;
    applyFilters();
  }, 120);
});
document.getElementById("districtFilter").addEventListener("change", e => { state.district = e.target.value; applyFilters(); });
document.getElementById("categoryFilter").addEventListener("change", e => { state.category = e.target.value; applyFilters(); });
document.getElementById("sortSelect").addEventListener("change", e => { state.sort = e.target.value; applyFilters(); });
document.getElementById("pageSizeSelect").addEventListener("change", e => { state.pageSize = Number(e.target.value); state.page = 1; renderTable(); });
document.getElementById("prevBtn").addEventListener("click", () => { if (state.page > 1) { state.page--; renderTable(); } });
document.getElementById("nextBtn").addEventListener("click", () => { state.page++; renderTable(); });
document.getElementById("exportBtn").addEventListener("click", exportFilteredCsv);
document.getElementById("resetBtn").addEventListener("click", () => {
  state.query = ""; state.district = ""; state.category = ""; state.sort = "relevance"; state.flags.clear();
  document.getElementById("searchInput").value = "";
  document.getElementById("districtFilter").value = "";
  document.getElementById("categoryFilter").value = "";
  document.getElementById("sortSelect").value = "relevance";
  document.querySelectorAll(".chip").forEach(ch => ch.classList.remove("active"));
  applyFilters();
});
document.querySelectorAll(".chip").forEach(ch => {
  ch.addEventListener("click", () => {
    const flag = ch.dataset.flag;
    if (state.flags.has(flag)) { state.flags.delete(flag); ch.classList.remove("active"); }
    else { state.flags.add(flag); ch.classList.add("active"); }
    applyFilters();
  });
});

initFilters();
applyFilters();
</script>
</body>
</html>
"""


def main() -> None:
    with open(IN_JSON, encoding="utf-8") as f:
        data = json.load(f)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # Prevent </script> injection inside embedded JSON
    payload = payload.replace("</", "<\\/")
    html = HTML_TEMPLATE.replace("__DATA_JSON__", payload)
    OUT_HTML.write_text(html, encoding="utf-8")
    size_mb = OUT_HTML.stat().st_size / (1024 * 1024)
    print(f"Saved {OUT_HTML.name} ({size_mb:.2f} MB) with {len(data)} colleges.")


if __name__ == "__main__":
    main()
