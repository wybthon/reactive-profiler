// Reactive Profiler bootstrap.
//
// Loads Pyodide from CDN, installs `wybthon` from PyPI via micropip,
// fetches our app package via a static manifest, writes it into
// Pyodide's virtual filesystem, and runs `app.main.main()`.
//
// Designed to work as a static site on GitHub Pages with no server:
// every request is a plain GET against files in this repo or an
// allowlisted CDN.

const PYODIDE_VERSION = "0.27.5";
const PYODIDE_BASE_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

// Pin the Wybthon version to keep the demo deterministic. The compatible
// range matches `pyproject.toml`. Bump both when upgrading.
const WYBTHON_SPEC = "wybthon==0.23.0";

const BUILD_VERSION = "1";
const APP_ROOT = "/app";
const APP_BASE = "./app";
const MANIFEST_URL = `${APP_BASE}/manifest.json`;

const setStatus = (msg) => {
  const el = document.getElementById("loading-status");
  if (el) el.textContent = msg;
};

const fadeOutLoader = () => {
  const el = document.getElementById("loading");
  if (!el) return;
  el.classList.add("fade-out");
  setTimeout(() => {
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }, 420);
};

// ---------- Error overlay ------------------------------------------------

let __overlay = null;
function showErrorOverlay(title, details) {
  try {
    if (__overlay) {
      __overlay.remove();
      __overlay = null;
    }
    const overlay = document.createElement("div");
    overlay.style.cssText = `
      position: fixed; inset: 0; z-index: 2147483647;
      background: rgba(255,244,176,0.88);
      color: #13223f;
      overflow: auto; padding: 24px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px; line-height: 1.6;
    `;

    const box = document.createElement("div");
    box.style.cssText = `
      max-width: 960px; margin: 0 auto;
      background: #fffdf2;
      border: 3px solid #d92845;
      border-radius: 4px;
      box-shadow: 9px 9px 0 #24365f;
      padding: 18px 22px;
    `;

    const hdr = document.createElement("div");
    hdr.style.cssText = "display:flex; align-items:center; justify-content:space-between; gap:12px;";

    const h = document.createElement("div");
    h.textContent = title || "Error";
    h.style.cssText = "font-weight:900; font-size:14px; color:#d92845; letter-spacing:0.01em; text-transform:uppercase;";
    hdr.appendChild(h);

    const btn = document.createElement("button");
    btn.textContent = "Dismiss";
    btn.style.cssText = `
      background: #f8de4e; color: #13223f;
      border: 2px solid #24365f;
      border-radius: 2px; padding: 6px 12px; cursor: pointer;
      box-shadow: 3px 3px 0 #24365f;
      font: inherit;
    `;
    btn.onclick = () => { try { overlay.remove(); } catch {} };
    hdr.appendChild(btn);

    const pre = document.createElement("pre");
    pre.style.cssText = "white-space: pre-wrap; margin-top: 12px; color: #33415f;";
    pre.textContent = details || "";

    box.appendChild(hdr);
    box.appendChild(pre);
    overlay.appendChild(box);
    document.body.appendChild(overlay);
    __overlay = overlay;
  } catch {
    // overlay is best-effort; never let it throw further.
  }
}

window.addEventListener("error", (e) => {
  try {
    const msg = (e?.error && (e.error.stack || String(e.error))) || String(e?.message || "");
    showErrorOverlay("JavaScript Error", msg);
  } catch {}
});
window.addEventListener("unhandledrejection", (e) => {
  try {
    const reason = e?.reason;
    showErrorOverlay("Unhandled Promise Rejection", String(reason?.stack || reason || "Unknown rejection"));
  } catch {}
});

// ---------- Filesystem helpers ------------------------------------------

function ensureDirs(pyodide, mountRoot, files) {
  const dirs = new Set([mountRoot]);
  for (const f of files) {
    const parts = f.split("/");
    for (let i = 1; i < parts.length; i++) {
      dirs.add(`${mountRoot}/${parts.slice(0, i).join("/")}`);
    }
  }
  for (const d of [...dirs].sort()) {
    try { pyodide.FS.mkdir(d); } catch { /* already exists */ }
  }
}

async function fetchTextNoStore(url) {
  const r = await fetch(url, { cache: "no-store" });
  if (!r.ok) throw new Error(`Failed to fetch ${url}: ${r.status} ${r.statusText}`);
  return r.text();
}

// ---------- Boot --------------------------------------------------------

async function bootstrap() {
  try {
    setStatus("Loading Pyodide runtime…");
    const { loadPyodide } = await import(`${PYODIDE_BASE_URL}pyodide.mjs`);
    const pyodide = await loadPyodide({
      indexURL: PYODIDE_BASE_URL,
      stdout: (s) => console.log("[py]", s),
      stderr: (s) => console.warn("[py]", s),
    });
    window.__pyodide = pyodide;

    setStatus("Installing wybthon from PyPI…");
    await pyodide.loadPackage("micropip");
    await pyodide.runPythonAsync(`
import micropip
await micropip.install("${WYBTHON_SPEC}")
import wybthon  # type: ignore
`);

    setStatus("Loading app modules…");
    const manifestResp = await fetch(`${MANIFEST_URL}?v=${BUILD_VERSION}`, { cache: "no-store" });
    if (!manifestResp.ok) {
      throw new Error(`Cannot load app manifest at ${MANIFEST_URL}: ${manifestResp.status} ${manifestResp.statusText}`);
    }
    const manifest = await manifestResp.json();
    const files = Array.isArray(manifest) ? manifest : (manifest && manifest.files);
    if (!Array.isArray(files) || files.length === 0) {
      throw new Error("App manifest is empty or malformed.");
    }

    ensureDirs(pyodide, APP_ROOT, files);
    await Promise.all(files.map(async (rel) => {
      const url = `${APP_BASE}/${rel}?v=${BUILD_VERSION}`;
      const txt = await fetchTextNoStore(url);
      pyodide.FS.writeFile(`${APP_ROOT}/${rel}`, new TextEncoder().encode(txt));
    }));

    await pyodide.runPythonAsync(`
import sys
if "/" not in sys.path:
    sys.path.insert(0, "/")
`);

    setStatus("Mounting app…");
    await pyodide.runPythonAsync(`
from app.main import main
import asyncio
asyncio.get_event_loop()
await main()
`);

    fadeOutLoader();
    console.log(`[reactive-profiler] Loaded ${files.length} Python files. Wybthon ${WYBTHON_SPEC} ready.`);
  } catch (err) {
    console.error("[reactive-profiler] Bootstrap failed:", err);
    setStatus("Boot failed; see the overlay for details.");
    const msg = (err && (err.message || err.stack)) ? `${err.message || ""}\n${err.stack || ""}` : String(err);
    showErrorOverlay("Bootstrap Failure", msg);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootstrap);
} else {
  bootstrap();
}
