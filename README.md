# Printer Maintenance Manual

An enterprise-grade printer maintenance and troubleshooting documentation site built with **MkDocs Material**.

## Overview

This repository contains a daily maintenance manual for office printers, covering routine checks, cleaning procedures, consumable replacement, paper handling, troubleshooting, and safety guidelines. It is designed as a reference for IT operations teams and end users.

- **Live site**: https://tiffany3222900.github.io/knowledge-management-system/
- **PDF exports** (bilingual, in repository root):
  - `Printer_Maintenance_Manual_EN.pdf` — English
  - `Printer_Maintenance_Manual_ZH.pdf` — Chinese

---

## Quick Start (Windows)

This project uses a **virtual environment** (`.venv`) to isolate dependencies. All convenience scripts automatically use the venv — no manual activation needed.

### First-time setup

If you just cloned this repo and `.venv` does not exist yet:

```bat
cd C:\Github\knowledge-management-system
python -m venv .venv
.venv\Scripts\python.exe -m pip install mkdocs-material mkdocs-print-site-plugin mkdocs-static-i18n playwright pikepdf
```

> **Note**: `.venv` is gitignored — it is not stored in GitHub. Each clone needs its own venv.

### Daily use — convenience scripts

Double-click any `.bat` file in the project root, or run it from the terminal:

| Script | Command | What it does |
|--------|---------|--------------|
| `serve.bat` | `serve.bat` | Start local preview at http://127.0.0.1:8000 (auto-reloads on file changes) |
| `build.bat` | `build.bat` | Build static HTML only (output to `site/` directory) |
| `deploy.bat` | `deploy.bat` | Build and deploy to GitHub Pages (live site updates in 1–2 min) |
| `build-pdf.bat` | `build-pdf.bat` | Build site and export both `Printer_Maintenance_Manual_EN.pdf` + `Printer_Maintenance_Manual_ZH.pdf` |

### Manual commands (without scripts)

If you prefer to run commands directly, prefix with the venv Python:

```bat
REM Preview locally
.venv\Scripts\python.exe -m mkdocs serve

REM Build static site
.venv\Scripts\python.exe -m mkdocs build

REM Deploy to GitHub Pages
.venv\Scripts\python.exe -m mkdocs gh-deploy --force

REM Export PDFs (bilingual; requires build first)
.venv\Scripts\python.exe -m mkdocs build
.venv\Scripts\python.exe export_pdf.py en
.venv\Scripts\python.exe export_pdf.py zh
```

---

## Typical Workflow

When you edit documentation:

```
1. Edit a file in docs/
2. Double-click serve.bat  →  preview at http://127.0.0.1:8000
3. Double-click build-pdf.bat  →  generates EN + ZH PDFs
4. git add . && git commit && git push  →  CI builds & deploys site, then opens PDF update PR if content changed
```

> **Important**: `deploy.bat` is legacy (uses `mkdocs gh-deploy`). The recommended path is to push to `main` and let the GitHub Actions workflow (`deploy.yml`) build and deploy the site. The PDFs are generated separately by `build-pdf.bat` (or by CI in the `build-pdf` job) and committed via PR.

---

## Documentation Structure

```
knowledge-management-system/
├── mkdocs.yml                  # MkDocs configuration and navigation
├── README.md                   # This file
├── .gitignore                  # Excludes site/, .venv/, etc.
├── export_pdf.py               # PDF export script (Playwright + Chromium; args: en | zh)
├── Printer_Maintenance_Manual_EN.pdf  # Generated PDF - English (committed)
├── Printer_Maintenance_Manual_ZH.pdf  # Generated PDF - Chinese (committed)
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
    ├── faq.md                  # Frequently asked questions
    └── *.zh.md                 # Chinese translations (suffix mode, one per English page)
```

---

## PDF Export Details

The PDFs are generated from the MkDocs **print-site** single page (`/print_page/`) using Playwright's bundled Chromium. Each language is built in an isolated site directory (`site_pdf_en` / `site_pdf_zh`) so the two PDFs contain only their own language.

- `python export_pdf.py en` → `Printer_Maintenance_Manual_EN.pdf`
- `python export_pdf.py zh` → `Printer_Maintenance_Manual_ZH.pdf`

**PDF settings** (configured in `export_pdf.py`):
- Paper size: A4
- Margins: 20mm top/bottom, 15mm left/right
- Background colors printed (preserves Material theme callout boxes)
- Header: document title
- Footer: page numbers + copyright

**Reproducible builds**: after export, the PDF is normalized with `pikepdf` (fixed creation/modification dates + deterministic file ID). Content-identical builds produce byte-identical files, so CI does not open redundant PDF-update PRs when nothing changed.

**Requirements for PDF export**:
- Playwright Chromium installed (`python -m playwright install chromium`)
- Playwright + pikepdf Python packages (installed in venv)

---

## Deployment

### GitHub Pages (current)

The site is automatically deployed by the **GitHub Actions workflow** (`.github/workflows/deploy.yml`) on every push to `main`. The workflow builds the site, uploads it as an artifact, and deploys via `actions/deploy-pages` to the `gh-pages` branch. GitHub Pages serves it at:

**https://tiffany3222900.github.io/knowledge-management-system/**

### Other platforms

This site can also be deployed to Netlify, Vercel, Cloudflare Pages, or any static hosting platform. The build output is in the `site/` directory after running `mkdocs build`.

---

## CI/CD Workflows

This repository uses **5 GitHub Actions workflows** to automate the full documentation lifecycle. `main` is branch-protected (no direct push — all automatic changes go through PRs for human review).

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `deploy.yml` | Push to `main` (docs/mkdocs.yml/export_pdf.py/workflow paths) or manual | Builds site once (artifact) and deploys to GitHub Pages. `build-pdf` job runs a **EN-ZH sync gate**: it only builds bilingual PDFs when every English doc's latest change has a matching, up-to-date `*.zh.md` translation (i.e. after the translation PR is merged); otherwise it skips the PDF build entirely |
| `release.yml` | Push tag `v*`, or manual (enter tag name) | Builds bilingual PDFs and creates a **GitHub Release** with EN+ZH PDF attachments. On manual trigger it auto-creates the tag first |
| `auto-translate.yml` | Push to `main` (docs/ changes) or manual | Incrementally translates changed English docs to Chinese (`*.zh.md`), opens a PR |
| `ai-style-check.yml` | Any PR touching `docs/**/*.md`, or manual | Runs AI writing-style review (Zhipu GLM-4-Flash) and posts an advisory report as a PR comment (does not block) |
| `ai-style-fix.yml` | Manual only (choose target branch) | AI auto-fixes English doc style issues, opens a PR for human review |

**Release artifacts**: https://github.com/tiffany3222900/knowledge-management-system/releases (e.g. `v1.0.0`, `v1.0.1` — each contains `Printer_Maintenance_Manual_EN.pdf` + `_ZH.pdf`).

> **Note**: All Actions are pinned to Node 24 runtimes (checkout@v5, setup-python@v6, etc.) to avoid Node 20 deprecation warnings.

---

## Technology Stack

| Component | Version / Detail |
|-----------|-----------------|
| MkDocs | 1.6.1 |
| Material for MkDocs | 9.7.7 |
| mkdocs-print-site-plugin | 2.9 (single-page print output) |
| mkdocs-static-i18n | 1.3.1 (EN/ZH bilingual, suffix mode) |
| Playwright | 1.62.0 (PDF export via bundled Chromium) |
| pikepdf | 10.16.0 (reproducible PDF normalization) |
| Python | 3.14 (local venv) |

---

## License

Content licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
