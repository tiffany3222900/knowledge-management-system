# Printer Maintenance Manual

An enterprise-grade printer maintenance and troubleshooting documentation site built with **MkDocs Material**.

## Overview

This repository contains a daily maintenance manual for office printers, covering routine checks, cleaning procedures, consumable replacement, paper handling, troubleshooting, and safety guidelines. It is designed as a reference for IT operations teams and end users.

- **Live site**: https://tiffany3222900.github.io/knowledge-management-system/
- **PDF export**: `Printer_Maintenance_Manual.pdf` (in repository root)

---

## Quick Start (Windows)

This project uses a **virtual environment** (`.venv`) to isolate dependencies. All convenience scripts automatically use the venv — no manual activation needed.

### First-time setup

If you just cloned this repo and `.venv` does not exist yet:

```bat
cd C:\Github\knowledge-management-system
python -m venv .venv
.venv\Scripts\python.exe -m pip install mkdocs-material mkdocs-print-site-plugin playwright
```

> **Note**: `.venv` is gitignored — it is not stored in GitHub. Each clone needs its own venv.

### Daily use — convenience scripts

Double-click any `.bat` file in the project root, or run it from the terminal:

| Script | Command | What it does |
|--------|---------|--------------|
| `serve.bat` | `serve.bat` | Start local preview at http://127.0.0.1:8000 (auto-reloads on file changes) |
| `build.bat` | `build.bat` | Build static HTML only (output to `site/` directory) |
| `deploy.bat` | `deploy.bat` | Build and deploy to GitHub Pages (live site updates in 1–2 min) |
| `build-pdf.bat` | `build-pdf.bat` | Build site and export `Printer_Maintenance_Manual.pdf` |

### Manual commands (without scripts)

If you prefer to run commands directly, prefix with the venv Python:

```bat
REM Preview locally
.venv\Scripts\python.exe -m mkdocs serve

REM Build static site
.venv\Scripts\python.exe -m mkdocs build

REM Deploy to GitHub Pages
.venv\Scripts\python.exe -m mkdocs gh-deploy --force

REM Export PDF (requires build first)
.venv\Scripts\python.exe -m mkdocs build
.venv\Scripts\python.exe export_pdf.py
```

---

## Typical Workflow

When you edit documentation:

```
1. Edit a file in docs/
2. Double-click serve.bat  →  preview at http://127.0.0.1:8000
3. Double-click build-pdf.bat  →  generates new Printer_Maintenance_Manual.pdf
4. Double-click deploy.bat  →  updates the live GitHub Pages site
5. git add . && git commit && git push  →  pushes updated docs + PDF to GitHub
```

> **Important**: `deploy.bat` only updates the website. The PDF is generated separately by `build-pdf.bat` and must be committed to Git manually.

---

## Documentation Structure

```
knowledge-management-system/
├── mkdocs.yml                  # MkDocs configuration and navigation
├── README.md                   # This file
├── .gitignore                  # Excludes site/, .venv/, etc.
├── export_pdf.py               # PDF export script (Playwright + Chrome)
├── Printer_Maintenance_Manual.pdf  # Generated PDF (committed)
├── serve.bat                   # Local preview (double-click)
├── build.bat                   # Build static site only
├── deploy.bat                  # Deploy to GitHub Pages
├── build-pdf.bat               # Build + export PDF
├── site/                       # Build output (gitignored)
├── .venv/                      # Python virtual environment (gitignored)
└── docs/
    ├── index.md                # Home / overview
    ├── getting-started.md      # Introduction and prerequisites
    ├── daily-checklist.md      # Daily and weekly maintenance checklist
    ├── cleaning.md             # Cleaning and care procedures
    ├── consumables.md          # Toner, ink, and drum replacement
    ├── paper-handling.md       # Paper loading and jam resolution
    ├── troubleshooting.md      # Common issues and fixes
    ├── safety.md               # Safety guidelines and PPE
    └── faq.md                  # Frequently asked questions
```

---

## PDF Export Details

The PDF is generated from the MkDocs **print-site** single page (`/print_page/`) using Playwright with the system-installed Chrome browser. This ensures pixel-perfect rendering identical to the web version.

**PDF settings** (configured in `export_pdf.py`):
- Paper size: A4
- Margins: 20mm top/bottom, 15mm left/right
- Background colors printed (preserves Material theme callout boxes)
- Header: document title
- Footer: page numbers + copyright

**Requirements for PDF export**:
- Google Chrome or Microsoft Edge installed on the system
- Playwright Python package (installed in venv)

---

## Deployment

### GitHub Pages (current)

The site is automatically deployed via `mkdocs gh-deploy`, which pushes the `site/` directory to the `gh-pages` branch. GitHub Pages serves it at:

**https://tiffany3222900.github.io/knowledge-management-system/**

### Other platforms

This site can also be deployed to Netlify, Vercel, Cloudflare Pages, or any static hosting platform. The build output is in the `site/` directory after running `mkdocs build`.

---

## Technology Stack

| Component | Version / Detail |
|-----------|-----------------|
| MkDocs | 1.6.1 |
| Material for MkDocs | 9.7.7 |
| mkdocs-print-site-plugin | 2.9 (single-page print output) |
| Playwright | 1.62.0 (PDF export via headless Chrome) |
| Python | 3.14 |

---

## License

Content licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
