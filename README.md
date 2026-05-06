<p align="center">
  <img src="assets/banner.jpg" alt="Wybthon" width="800" />
</p>

<h1 align="center">Reactive Profiler</h1>

<p align="center">
  <em>An interactive demo of <a href="https://github.com/wybthon/wybthon">Wybthon</a>'s run-once components and fine-grained reactive holes, written in Python and served as a plain static site at <a href="https://profiler.wybthon.com/">profiler.wybthon.com</a>.</em>
</p>

<p align="center">
  <a href="https://profiler.wybthon.com/"><img src="https://img.shields.io/badge/demo-profiler.wybthon.com-7c5cff" alt="Live demo" /></a>
  <a href="https://pypi.org/project/wybthon/"><img src="https://img.shields.io/pypi/v/wybthon?label=wybthon" alt="PyPI Version" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-success" alt="License: MIT" /></a>
</p>

---

## What this is

The Reactive Profiler is a single, polished landing page that visualises Wybthon's update model:

- A **playground** with a counter, a slider, and a text field. Each derived value is wrapped in a flashing "island" so you can see exactly which DOM nodes update when you interact.
- A **side-by-side comparison** that pits Wybthon's reactive-hole path against a naive whole-component `innerHTML` rewrite. A 60-update burst makes the difference impossible to miss.
- A **live profiler panel** that tallies signal writes, reactive-hole evaluations, and DOM mutations for both paths, alongside a "component bodies executed" stat that stays locked at the number of mounted components because Wybthon never re-runs them.
- An **annotated code inspector** that highlights what runs once at mount versus what becomes a reactive hole.

Everything is written in Python with [Wybthon](https://pypi.org/project/wybthon/) and runs entirely in your browser via [Pyodide](https://pyodide.org/). There is no JavaScript build step.

## Project layout

```
reactive-profiler/
├── index.html            # Shell, metadata, loading state, all CSS
├── bootstrap.js          # Pyodide + micropip + manifest-driven loader
├── app/
│   ├── manifest.json     # List of Python files to install into Pyodide FS
│   ├── main.py           # async main(), bootstrap entry point
│   ├── app.py            # Root <App> component
│   ├── profiler/         # Counters + Island wrapper for visualising holes
│   ├── ui/               # Tiny presentational primitives (Stat, Pill, …)
│   └── sections/         # Hero, Comparison, CodeInspector, WhyItMatters, …
├── assets/               # Logos, banners, social card, icons
├── tools/
│   └── build_manifest.py # Regenerates app/manifest.json
├── CNAME                 # Custom domain for GitHub Pages
└── .nojekyll             # Serve files directly, without Jekyll processing
```

## Running locally

You only need Python 3.10+ on your `PATH`. Wybthon itself is fetched from PyPI by Pyodide at runtime.

```bash
git clone https://github.com/wybthon/reactive-profiler.git
cd reactive-profiler

# 1. Generate the static file manifest used by bootstrap.js
make manifest

# 2. Serve the directory; any static server works
make serve         # → http://localhost:8000

# Or in one go:
make dev
```

When you add, rename, or remove a Python file under `app/`, regenerate the manifest:

```bash
make manifest
```

The repository commits `app/manifest.json` so the static site works on GitHub Pages with no build step. CI or reviewers can run `python tools/build_manifest.py --check` to catch stale manifests.

### Optional: install `wybthon` for IDE autocomplete

The runtime installs Wybthon inside Pyodide via `micropip`, but having it locally helps editors (linters, type checkers, autocomplete):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Customising

- **Wybthon version.** Bump the pinned spec in `bootstrap.js` (`WYBTHON_SPEC = "wybthon==X.Y.Z"`) and the exact `wybthon==X.Y.Z` dependency in `pyproject.toml` together.
- **Theme tokens.** The colour palette and spacing scale live as CSS variables in `index.html` (`--accent`, `--bg-1`, ...). Components reference those via `class_=` props.
- **Profiler instrumentation.** New islands? Wrap your getter with `Island(getter, kind="primary")` from `app.profiler` and the global counters update automatically.
- **Social card.** The README uses the original `assets/banner.jpg`. Open Graph and Twitter use the separate, 1200x630 `assets/og-image.jpg` generated from that banner so link previews do not crop unpredictably.

## Deployment

This repository is intentionally deployable directly from the repo root. No build workflow is required.

To wire up the custom domain `profiler.wybthon.com`:

1. **Repository -> Settings -> Pages**, set the source to **Deploy from a branch**.
2. Choose the `main` branch and `/ (root)` folder.
3. Set **Custom domain** to `profiler.wybthon.com` (the `CNAME` file at the repo root makes this stick).
4. In your DNS provider, add a `CNAME` record:

    ```
    profiler  CNAME  <github-username>.github.io.
    ```

   (For an apex domain, you'd use the GitHub Pages `A` records instead; apex isn't needed here.)

5. Once DNS propagates, enable **Enforce HTTPS** in the Pages settings.

## Tech notes

- Pyodide is loaded from `cdn.jsdelivr.net` (`/pyodide/v0.27.5/full/`).
- `micropip.install("wybthon==0.23.0")` pulls the pure-Python wheel from `files.pythonhosted.org`.
- The bootstrap script reads `app/manifest.json`, fetches each file via plain `GET`, and writes it into Pyodide's virtual FS at `/app/...`. No service worker, no zip extraction.
- Component bodies use the `@component` decorator. Reactive holes are zero-arg callables embedded in the VNode tree; see [`app/profiler/island.py`](app/profiler/island.py) for the canonical pattern.

## License

[MIT](LICENSE) © 2026 Owen Carey

The page reuses the official Wybthon banner, favicon, and logo from the [main repository](https://github.com/wybthon/wybthon) under the same MIT license.
