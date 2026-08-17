const T1 = window.TASK1_BASE;
const T2 = window.TASK2_BASE;

/* ---------------- Tab switching ---------------- */
const tabBtns = document.querySelectorAll(".tab-btn");
const indicator = document.getElementById("tab-indicator");

function positionIndicator(btn) {
  indicator.style.width = btn.offsetWidth + "px";
  indicator.style.transform = `translateX(${btn.offsetLeft - 4}px)`;
}

function activateTab(name) {
  tabBtns.forEach((b) => {
    const active = b.dataset.tab === name;
    b.classList.toggle("active", active);
    b.setAttribute("aria-selected", active);
    if (active) positionIndicator(b);
  });
  document.getElementById("panel-search").classList.toggle("active", name === "search");
  document.getElementById("panel-cluster").classList.toggle("active", name === "cluster");
}

tabBtns.forEach((b) => b.addEventListener("click", () => activateTab(b.dataset.tab)));
window.addEventListener("load", () => positionIndicator(document.querySelector(".tab-btn.active")));
window.addEventListener("resize", () => positionIndicator(document.querySelector(".tab-btn.active")));

/* ---------------- Backend status pills ---------------- */
async function checkStatus(url, pillId) {
  const pill = document.getElementById(pillId);
  try {
    const res = await fetch(url, { method: "GET" });
    pill.classList.add(res.ok ? "online" : "offline");
  } catch {
    pill.classList.add("offline");
  }
}
checkStatus(`${T1}/api/crawler/status`, "status-task1");
checkStatus(`${T2}/api/dataset/stats`, "status-task2");

/* ---------------- Subtle 3D tilt on cards ---------------- */
function attachTilt(el) {
  el.addEventListener("mousemove", (e) => {
    const r = el.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - 0.5;
    const py = (e.clientY - r.top) / r.height - 0.5;
    el.style.transform = `perspective(800px) rotateX(${(-py * 4).toFixed(2)}deg) rotateY(${(px * 4).toFixed(2)}deg) translateY(-2px)`;
  });
  el.addEventListener("mouseleave", () => { el.style.transform = ""; });
}

/* ===================== TASK 1: SEARCH ===================== */
const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const resultsEl = document.getElementById("results");
const metaEl = document.getElementById("results-meta");
const paginationEl = document.getElementById("pagination");
const statusToggle = document.getElementById("crawler-status-toggle");
const statusPanel = document.getElementById("crawler-status-panel");

let currentQuery = "";
let currentPage = 1;

searchForm.addEventListener("submit", (e) => {
  e.preventDefault();
  currentQuery = searchInput.value.trim();
  currentPage = 1;
  if (currentQuery) runSearch();
});

document.querySelectorAll(".chip[data-q]").forEach((chip) => {
  chip.addEventListener("click", () => {
    searchInput.value = chip.dataset.q;
    currentQuery = chip.dataset.q;
    currentPage = 1;
    runSearch();
  });
});

let statusInterval = null;

async function fetchStatus(isInitial = false) {
  if (statusPanel.classList.contains("hidden")) return;
  if (isInitial) statusPanel.innerHTML = '<p class="state-msg">Loading crawler status…</p>';
  try {
    const res = await fetch(`${T1}/api/crawler/status`);
    const data = await res.json();
    let lastCrawl = "No crawl has run yet.";
    if (data.last_crawl) {
      if (data.last_crawl.stopped_reason === "Running...") {
        lastCrawl = `<span style="color: var(--rose); font-weight: 600; display: inline-flex; align-items: center; gap: 8px;"><span class="spinner" style="width: 14px; height: 14px; border: 2px solid var(--rose); border-bottom-color: transparent; border-radius: 50%; animation: spin 1s linear infinite;"></span> Crawling live right now... (${data.research_output_count} pubs & ${data.profile_count} profiles found so far!)</span>`;
      } else {
        let finishedDate = data.last_crawl.finished_at ? new Date(data.last_crawl.finished_at).toLocaleString() : 'Unknown date';
        let remainingDaysText = '';
        if (data.scheduler && data.scheduler.jobs && data.scheduler.jobs.length > 0 && data.scheduler.jobs[0].next_run_time) {
           let nextRun = new Date(data.scheduler.jobs[0].next_run_time);
           let diffMs = nextRun - new Date();
           let days = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
           remainingDaysText = ` (Next auto-crawl in ${days} days)`;
        }
        lastCrawl = `<span style="color: var(--text); font-weight: 500;">Last Crawled: ${finishedDate}${remainingDaysText}</span>`;
      }
    }

    if (!document.getElementById("spin-style")) {
      document.head.insertAdjacentHTML("beforeend", `<style id="spin-style">@keyframes spin { to { transform: rotate(360deg); } }</style>`);
    }

    statusPanel.innerHTML = `
      <table>
        <tr><td>Research outputs indexed</td><td>${data.research_output_count}</td></tr>
        <tr><td>Profiles indexed</td><td>${data.profile_count}</td></tr>
        <tr><td>TF-IDF Search Index</td><td>
          <span style="color: ${data.index_ready ? 'var(--success)' : 'var(--accent)'}; font-weight: bold;">
            ${data.index_ready ? "Ready & Optimized" : "Building..."}
          </span>
        </td></tr>
        <tr><td>Auto-Crawl Scheduler</td><td>
          <span style="color: var(--success); font-weight: bold;">${data.scheduler.running ? "Active" : "Inactive"}</span> 
          <span style="color: var(--muted); font-size: 0.9em;">(Runs every ${data.scheduler.interval_months ?? "?"} months)</span>
        </td></tr>
        <tr><td>Last crawl</td><td>${lastCrawl}</td></tr>
      </table>`;
  } catch {
    statusPanel.innerHTML = '<p class="state-msg error">Failed to reach the Task 1 backend on :5001.</p>';
  }
}

statusToggle.addEventListener("click", () => {
  document.getElementById("search-center-wrapper").style.marginTop = "0";
  statusPanel.classList.toggle("hidden");
  if (!statusPanel.classList.contains("hidden")) {
    fetchStatus(true);
    if (!statusInterval) statusInterval = setInterval(() => fetchStatus(false), 3000);
  } else {
    if (statusInterval) {
      clearInterval(statusInterval);
      statusInterval = null;
    }
  }
});

async function runSearch() {
  document.getElementById("search-center-wrapper").style.marginTop = "0";
  resultsEl.innerHTML = '<p class="state-msg">Searching…</p>';
  metaEl.classList.add("hidden");
  paginationEl.classList.add("hidden");
  try {
    const res = await fetch(`${T1}/api/search?q=${encodeURIComponent(currentQuery)}&page=${currentPage}`);
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error || `Request failed (${res.status})`);
    renderResults(await res.json());
  } catch (err) {
    resultsEl.innerHTML = `<p class="state-msg error">${err.message}. Is the Task 1 backend running on :5001?</p>`;
  }
}

function renderResults(data) {
  metaEl.classList.remove("hidden");
  if (data.total_results === 0) {
    metaEl.textContent = `No results for "${data.query}".`;
    resultsEl.innerHTML = '<p class="state-msg">Try a different keyword or author name.</p>';
    return;
  }
  metaEl.textContent = `${data.total_results} result${data.total_results === 1 ? "" : "s"} for "${data.query}" | page ${data.page} of ${data.total_pages}`;
  resultsEl.innerHTML = data.results.map(renderCard).join("");
  resultsEl.querySelectorAll(".result-card").forEach(attachTilt);
  renderPagination(data);
}

function renderCard(r, i) {
  const authorsHtml = r.authors
    .map((name, idx) => {
      const url = r.author_profiles[idx];
      return url ? `<a href="${url}" target="_blank" rel="noopener">${escapeHtml(name)}</a>` : escapeHtml(name);
    })
    .join(" · ");
  return `
    <article class="result-card">
      <span class="result-rank">#${(currentPage - 1) * 10 + i + 1}</span>
      <div class="result-title"><a href="${r.document_url}" target="_blank" rel="noopener">${escapeHtml(r.title)}</a></div>
      <div class="result-meta"><span class="authors">${authorsHtml || "Authors not listed"}</span>${r.publication_type ? ` · ${escapeHtml(r.publication_type)}` : ""}${r.journal ? ` · ${escapeHtml(r.journal)}` : ""}</div>
      ${r.description ? `<p class="result-desc">${escapeHtml(truncate(r.description, 240))}</p>` : ""}
      <div class="result-footer">
        <span style="color:var(--muted);font-size:.8rem;">Published: ${escapeHtml(r.publication_date || "Not stated")}</span>
        <span class="similarity-badge">Cosine similarity: ${r.cosine_similarity.toFixed(4)}</span>
        <a class="view-link" href="${r.document_url}" target="_blank" rel="noopener">View Research Output →</a>
      </div>
    </article>`;
}

function renderPagination(data) {
  if (data.total_pages <= 1) { paginationEl.classList.add("hidden"); return; }
  paginationEl.classList.remove("hidden");
  let html = `<button ${data.page <= 1 ? "disabled" : ""} data-page="${data.page - 1}">Previous</button>`;
  for (let p = 1; p <= data.total_pages; p++) html += `<button class="${p === data.page ? "active" : ""}" data-page="${p}">${p}</button>`;
  html += `<button ${data.page >= data.total_pages ? "disabled" : ""} data-page="${data.page + 1}">Next</button>`;
  paginationEl.innerHTML = html;
  paginationEl.querySelectorAll("button[data-page]").forEach((btn) => {
    btn.addEventListener("click", () => { currentPage = parseInt(btn.dataset.page, 10); runSearch(); window.scrollTo({ top: 0, behavior: "smooth" }); });
  });
}

/* ===================== TASK 2: CLUSTERING ===================== */
const textInput = document.getElementById("text-input");
const classifyBtn = document.getElementById("classify-btn");
const clearBtn = document.getElementById("clear-btn");
const resultPanel = document.getElementById("result-panel");
const historyList = document.getElementById("history-list");

classifyBtn.addEventListener("click", classify);
clearBtn.addEventListener("click", () => { textInput.value = ""; resultPanel.classList.add("hidden"); textInput.rows = 7; });

const CAT_COLORS = { Economics: "#22d3c9", Entertainment: "#f5a524", Politics: "#a78bfa" };

function showToast(msg) {
  const toast = document.createElement("div");
  toast.className = "toast-popup";
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.classList.add("show"), 10);
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

async function classify() {
  const text = textInput.value.trim();
  const loader = document.getElementById("classify-loader");
  
  if (!text) { 
    resultPanel.classList.remove("hidden");
    resultPanel.innerHTML = '<p class="state-msg error">Please enter some text to classify.</p>'; 
    return; 
  }
  
  loader.classList.remove("hidden");
  resultPanel.classList.add("hidden");
  
  try {
    const res = await fetch(`${T2}/api/classify`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) });
    const data = await res.json().catch(() => ({}));
    
    loader.classList.add("hidden");
    
    if (!res.ok) {
      if (res.status === 400 && data.error) {
        showToast(data.error);
        return; // do not show error inside the panel
      }
      throw new Error(data.error || "Classification failed.");
    }

    resultPanel.classList.remove("hidden");
    textInput.rows = 4;
    resultPanel.innerHTML = `
      <div class="result-category ${data.predicted_category}">${data.predicted_category}</div>`;
    loadHistory();
  } catch (err) {
    loader.classList.add("hidden");
    resultPanel.classList.remove("hidden");
    textInput.rows = 7;
    resultPanel.innerHTML = `<p class="state-msg error">${err.message}. Is the Task 2 backend running on :5002?</p>`;
  }
}

async function loadHistory() {
  try {
    const res = await fetch(`${T2}/api/predictions/history?limit=8&_t=${Date.now()}`);
    const data = await res.json();
    if (!data.predictions.length) { historyList.innerHTML = '<p class="state-msg">No predictions yet.</p>'; return; }
    historyList.innerHTML = data.predictions.map((p) => `
      <div class="history-item">
        <span class="cat-tag ${p.predicted_category}">${p.predicted_category}</span>
        <span class="history-text">${escapeHtml(p.input_text)}</span>
        <span class="history-ts">${new Date(p.timestamp).toLocaleString()}</span>
      </div>`).join("");
  } catch {
    historyList.innerHTML = '<p class="state-msg error">Failed to load history.</p>';
  }
}

/* ---------------- Dataset / Model stats tabs ---------------- */
const statsTabs = document.querySelectorAll(".stats-tab");
const datasetBody = document.getElementById("dataset-stats");
const modelBody = document.getElementById("model-stats");

statsTabs.forEach((tab) => tab.addEventListener("click", () => {
  statsTabs.forEach((t) => t.classList.remove("active"));
  tab.classList.add("active");
  datasetBody.classList.toggle("hidden", tab.dataset.stats !== "dataset");
  modelBody.classList.toggle("hidden", tab.dataset.stats !== "model");
}));

async function loadDatasetStats() {
  try {
    const res = await fetch(`${T2}/api/dataset/stats`);
    const data = await res.json();
    
    let currentAngle = 0;
    const radius = 60;
    const circumference = 2 * Math.PI * radius;
    const total = data.total;
    
    const colors = { Economics: "var(--econ)", Entertainment: "var(--ent)", Politics: "var(--pol)" };
    const icons = { Economics: "📈", Entertainment: "🎬", Politics: "🏛️" };
    
    let svg = `<div style="perspective: 800px; width:180px; height:180px; margin:0 auto;"><svg viewBox="0 0 160 160" style="width:100%; height:100%; display:block; filter: drop-shadow(0 25px 20px rgba(0,0,0,0.7)) drop-shadow(0 0 10px rgba(255,255,255,0.1)); transform: rotateX(25deg) rotateY(-15deg) scale(1.1); transform-style: preserve-3d; transition: transform 0.5s;">`;
    let legend = `<div style="display:flex; flex-direction:column; gap:12px;">`;
    
    data.categories.forEach((c) => {
      const cat = c.category;
      const count = c.actual;
      const percent = count / total;
      const strokeDasharray = `${percent * circumference} ${circumference}`;
      const strokeDashoffset = - (currentAngle / 360) * circumference;
      
      svg += `<circle r="${radius}" cx="80" cy="80" fill="transparent" stroke="${colors[cat]}" stroke-width="24" stroke-dasharray="${strokeDasharray}" stroke-dashoffset="${strokeDashoffset}" transform="rotate(-90 80 80)" style="transition: all 1s ease-out; stroke-linecap: round; filter: drop-shadow(inset 0 4px 4px rgba(255,255,255,0.5));" />`;
      currentAngle += percent * 360;
      
      legend += `<div style="display:flex; align-items:center; gap:14px; font-size:14px;">
                   <div style="width:12px; height:12px; border-radius:50%; background:${colors[cat]}; box-shadow: 0 0 12px ${colors[cat]};"></div>
                   <div style="color:var(--muted); display:flex; align-items:center; gap:8px;">
                     <span>${icons[cat]}</span>
                     <span>${cat}</span>
                   </div>
                   <div class="count-up" data-count="${count}" style="color:#fff; font-weight:800; font-size:15px; margin-left:auto;">0</div>
                 </div>`;
    });
    
    svg += `<text x="80" y="75" class="count-up" data-count="${total}" text-anchor="middle" fill="#fff" font-size="28" font-weight="900" font-family="var(--font-sans)" style="transform: translateZ(20px); text-shadow: 0 5px 10px rgba(0,0,0,0.8);">0</text>
            <text x="80" y="98" text-anchor="middle" fill="var(--muted)" font-size="12" font-family="var(--font-sans)" style="transform: translateZ(20px);">documents</text>
           </svg></div>`;
    legend += `</div>`;
    
    const html = `
      <div style="margin-bottom: 8px;">
        <h3 style="color:#fff; font-size:1.05rem; font-weight:800; margin-bottom: 16px; text-align:center;">Cluster Distribution</h3>
        <div style="display:flex; justify-content:center; align-items:center; gap: 32px;">
          ${svg}
          ${legend}
        </div>
      </div>`;
    datasetBody.innerHTML = html;

    // Animate numbers
    datasetBody.querySelectorAll('.count-up').forEach(el => {
      const target = parseInt(el.getAttribute('data-count'), 10);
      const duration = 1500;
      const startTime = performance.now();
      
      function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOutQuad = progress * (2 - progress);
        el.textContent = Math.floor(easeOutQuad * target);
        if (progress < 1) requestAnimationFrame(updateNumber);
        else el.textContent = target;
      }
      requestAnimationFrame(updateNumber);
    });
  } catch (err) {
    datasetBody.innerHTML = '<p class="state-msg error">Failed to reach the Task 2 backend on :5002.</p>';
  }
}

async function loadModelStats() {
  try {
    const res = await fetch(`${T2}/api/model/evaluation`);
    if (!res.ok) { modelBody.innerHTML = '<p class="state-msg">Model not trained yet. Run scripts/train_model.py.</p>'; return; }
    const d = await res.json();
    modelBody.innerHTML = `
      <table>
        <tr><td>Documents / vocabulary terms</td><td>${d.n_documents} / ${d.n_terms}</td></tr>
        <tr><td>Silhouette score</td><td>${d.silhouette_score.toFixed(4)}</td></tr>
        <tr><td>Inertia</td><td>${d.inertia.toFixed(2)}</td></tr>
        <tr><td>Accuracy vs. known labels</td><td>${(d.accuracy * 100).toFixed(1)}%</td></tr>
        <tr><td>Precision (macro)</td><td>${d.precision_macro.toFixed(4)}</td></tr>
        <tr><td>Recall (macro)</td><td>${d.recall_macro.toFixed(4)}</td></tr>
        <tr><td>F1 (macro)</td><td>${d.f1_macro.toFixed(4)}</td></tr>
      </table>`;
  } catch {
    modelBody.innerHTML = '<p class="state-msg error">Failed to reach the Task 2 backend on :5002.</p>';
  }
}

async function loadPCAChart() {
  const ctx = document.getElementById('clusterCanvas');
  if (!ctx) return;
  
  try {
    const res = await fetch(`${T2}/api/model/pca`);
    if (!res.ok) throw new Error("Not trained");
    const data = await res.json();
    
    const colors = { Economics: "rgba(34, 211, 201, 0.8)", Entertainment: "rgba(245, 165, 36, 0.8)", Politics: "rgba(167, 139, 250, 0.8)" };
    const borders = { Economics: "#22d3c9", Entertainment: "#f5a524", Politics: "#a78bfa" };
    
    const datasets = ["Economics", "Entertainment", "Politics"].map(cat => {
      return {
        label: cat,
        data: data.filter(d => d.category === cat).map(d => ({ x: d.x, y: d.y, title: d.title })),
        backgroundColor: colors[cat],
        borderColor: borders[cat],
        borderWidth: 1,
        pointRadius: 4,
        pointHoverRadius: 7
      };
    });
    
    new Chart(ctx, {
      type: 'scatter',
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.raw.title;
              }
            }
          }
        },
        scales: {
          x: { grid: { color: "#2a2d3e" }, ticks: { display: false } },
          y: { grid: { color: "#2a2d3e" }, ticks: { display: false } }
        }
      }
    });
  } catch (err) {
    const container = ctx.parentNode;
    container.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--muted);">Run scripts/train_model.py to generate PCA data.</div>`;
  }
}
loadPCAChart();

function truncate(text, n) { return text.length > n ? text.slice(0, n).trim() + "…" : text; }
function escapeHtml(str) { const d = document.createElement("div"); d.textContent = str ?? ""; return d.innerHTML; }

loadHistory();
loadDatasetStats();
loadModelStats();

/* ===================== AUTO-SUGGEST ===================== */
function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// Task 1 Suggest
const task1Suggestions = document.getElementById("task1-suggestions");
searchInput.addEventListener("input", debounce(async (e) => {
  const query = e.target.value.trim();
  if (query.length < 2) {
    task1Suggestions.classList.add("hidden");
    return;
  }
  try {
    const res = await fetch(`${T1}/api/suggest?q=${encodeURIComponent(query)}`);
    const data = await res.json();
    if (data.length > 0) {
      task1Suggestions.innerHTML = data.map(s => `<li>${escapeHtml(s)}</li>`).join("");
      task1Suggestions.classList.remove("hidden");
    } else {
      task1Suggestions.classList.add("hidden");
    }
  } catch {
    task1Suggestions.classList.add("hidden");
  }
}, 300));

task1Suggestions.addEventListener("click", (e) => {
  if (e.target.tagName === "LI") {
    searchInput.value = e.target.textContent;
    task1Suggestions.classList.add("hidden");
    searchForm.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
  }
});

// Task 2 Suggest
const task2Suggestions = document.getElementById("task2-suggestions");
if (task2Suggestions) {
  textInput.addEventListener("input", debounce(async (e) => {
    const query = e.target.value.trim();
    if (query.length < 2) {
      task2Suggestions.classList.add("hidden");
      return;
    }
    try {
      const res = await fetch(`${T2}/api/suggest?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      if (data.length > 0) {
        task2Suggestions.innerHTML = data.map(s => `<li>${escapeHtml(s)}</li>`).join("");
        task2Suggestions.classList.remove("hidden");
      } else {
        task2Suggestions.classList.add("hidden");
      }
    } catch {
      task2Suggestions.classList.add("hidden");
    }
  }, 300));

  task2Suggestions.addEventListener("click", (e) => {
    if (e.target.tagName === "LI") {
      textInput.value = e.target.textContent;
      task2Suggestions.classList.add("hidden");
    }
  });
}

// Hide on outside click
document.addEventListener("click", (e) => {
  if (!e.target.closest("#search-form") && !e.target.closest("#task1-suggestions")) {
    task1Suggestions.classList.add("hidden");
  }
  if (!e.target.closest(".classify-card") && !e.target.closest("#task2-suggestions") && task2Suggestions) {
    task2Suggestions.classList.add("hidden");
  }
});
