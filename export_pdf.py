"""
Export MkDocs print-site page to PDF via Playwright (Chromium).

Supports both English and Chinese PDF generation by building the site
with mkdocs-static-i18n's build_only_locale option:

  python export_pdf.py en   -> Printer_Maintenance_Manual_EN.pdf
  python export_pdf.py zh   -> Printer_Maintenance_Manual_ZH.pdf

For English, the print-site plugin also excludes *.zh.md files so the
PDF contains only English content. For Chinese, i18n maps files to the
zh locale automatically.

Reproducible builds:
  Chromium embeds a creation timestamp and random file ID in every PDF,
  so identical content produces different bytes on each run. After
  export, the PDF is normalized with pikepdf (fixed CreationDate/ModDate
  and a deterministic file ID) so that content-identical builds yield
  byte-identical PDFs. This lets CI skip the "PDF update" PR when the
  content has not actually changed.

Works on both local Windows and CI (Ubuntu).
"""
import sys
import re
import shutil
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

# Resolve paths relative to this script (cross-platform)
repo_dir = Path(__file__).resolve().parent
main_config = repo_dir / "mkdocs.yml"

HEADER_TEXT = {
    "en": "Printer Maintenance Manual",
    "zh": "打印机维护手册",
}

OUTPUT_NAME = {
    "en": "Printer_Maintenance_Manual_EN.pdf",
    "zh": "Printer_Maintenance_Manual_ZH.pdf",
}

# Fixed metadata so content-identical builds produce byte-identical PDFs
FIXED_DATE = "D:20260101000000+00'00'"
FIXED_ID = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"


def make_reproducible(pdf_path: Path):
    """Strip run-to-run nondeterminism (timestamps, file ID) from a PDF."""
    try:
        import pikepdf
    except ImportError:
        print("WARNING: pikepdf not installed; PDF will not be reproducible.")
        return

    tmp_path = pdf_path.with_suffix(".tmp.pdf")
    with pikepdf.open(pdf_path) as pdf:
        if pdf.docinfo is not None:
            for key in ("/CreationDate", "/ModDate"):
                if key in pdf.docinfo:
                    pdf.docinfo[key] = FIXED_DATE
        # deterministic_id=True makes pikepdf emit a fixed ID derived from
        # the content instead of a random one
        pdf.save(tmp_path, deterministic_id=True)
    tmp_path.replace(pdf_path)
    print(f"Reproducible metadata applied: {pdf_path.name}")


def make_temp_config(lang: str) -> Path:
    """Create a temporary mkdocs config with build_only_locale + site_dir."""
    content = main_config.read_text(encoding="utf-8")

    # Inject build_only_locale into the i18n plugin block
    content = content.replace(
        "  - i18n:\n      languages:",
        f"  - i18n:\n      build_only_locale: {lang}\n      languages:",
        1,
    )

    # For English, exclude Chinese files from the print page
    if lang == "en":
        content = content.replace(
            "  - print-site:\n",
            "  - print-site:\n      exclude:\n        - '*.zh.md'\n",
            1,
        )

    # Use a dedicated site_dir so we never clobber the main ./site
    content = re.sub(
        r"(?m)^site_dir:.*$", "", content
    ).rstrip() + f"\n\nsite_dir: site_pdf_{lang}\n"

    tmp_config = repo_dir / f"mkdocs.pdf.{lang}.yml"
    tmp_config.write_text(content, encoding="utf-8")
    return tmp_config


def build_site(lang: str, tmp_config: Path):
    """Build the site for a single locale."""
    print(f"Building site for locale '{lang}' ...")
    result = subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "-f", str(tmp_config)],
        capture_output=True,
        text=True,
    )
    print(result.stdout[-1500:] if result.stdout else "")
    if result.returncode != 0:
        print(result.stderr[-2000:] if result.stderr else "")
        raise RuntimeError(f"mkdocs build failed for locale '{lang}'")


def export_pdf(lang: str):
    """Export the print page for a locale to a PDF file."""
    print_page = repo_dir / f"site_pdf_{lang}" / "print_page" / "index.html"
    output_pdf = repo_dir / OUTPUT_NAME[lang]

    if not print_page.exists():
        raise RuntimeError(f"print page not found: {print_page}")

    file_url = print_page.as_uri()
    print(f"Source: {file_url}")
    print(f"Output: {output_pdf}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        )
        context = browser.new_context()
        page = context.new_page()

        print("Loading print page...")
        page.goto(file_url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(2000)

        # Scroll to bottom to trigger lazy-loaded content
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)

        print("Exporting to PDF...")
        page.pdf(
            path=str(output_pdf),
            format="A4",
            print_background=True,
            margin={
                "top": "20mm",
                "bottom": "20mm",
                "left": "15mm",
                "right": "15mm",
            },
            display_header_footer=True,
            header_template=f'''
                <div style="font-size:8px; width:100%; text-align:center; color:#666; padding:0 15mm;">
                    {HEADER_TEXT[lang]}
                </div>
            ''',
            footer_template='''
                <div style="font-size:8px; width:100%; text-align:center; color:#666; padding:0 15mm;">
                    Page <span class="pageNumber"></span> of <span class="totalPages"></span>
                    &nbsp;|&nbsp; &copy; 2026 IT Operations Team
                </div>
            ''',
            prefer_css_page_size=False,
        )
        browser.close()

    # Make the PDF byte-deterministic (fix timestamps + file ID)
    make_reproducible(output_pdf)

    size_mb = output_pdf.stat().st_size / (1024 * 1024)
    print(f"\nSUCCESS: PDF generated - {output_pdf}")
    print(f"Size: {size_mb:.2f} MB")
    return output_pdf


def cleanup(lang: str, tmp_config: Path):
    """Remove temp config and the dedicated site_pdf directory."""
    tmp_config.unlink(missing_ok=True)
    site_dir = repo_dir / f"site_pdf_{lang}"
    shutil.rmtree(site_dir, ignore_errors=True)


def main():
    lang = "en"
    if len(sys.argv) > 1:
        lang = sys.argv[1].strip().lower()
    if lang not in OUTPUT_NAME:
        print(f"ERROR: unsupported locale '{lang}'. Use 'en' or 'zh'.")
        sys.exit(1)

    tmp_config = make_temp_config(lang)
    try:
        build_site(lang, tmp_config)
        export_pdf(lang)
    finally:
        cleanup(lang, tmp_config)


if __name__ == "__main__":
    main()
