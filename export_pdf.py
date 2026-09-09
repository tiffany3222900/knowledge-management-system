"""
Export MkDocs print-site page to PDF via Playwright (Chromium).
Works on both local Windows and CI (Ubuntu).
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# Resolve paths relative to this script (cross-platform)
repo_dir = Path(__file__).resolve().parent
print_page = repo_dir / "site" / "print_page" / "index.html"
output_pdf = repo_dir / "Printer_Maintenance_Manual.pdf"

if not print_page.exists():
    print(f"ERROR: print page not found at {print_page}")
    sys.exit(1)

file_url = print_page.as_uri()
print(f"Source: {file_url}")
print(f"Output: {output_pdf}")

with sync_playwright() as p:
    # Use Playwright's bundled Chromium (works in CI without system Chrome)
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
    )

    context = browser.new_context()
    page = context.new_page()

    print("Loading print page...")
    page.goto(file_url, wait_until="networkidle", timeout=60000)

    # Wait for fonts and images to load
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
            "right": "15mm"
        },
        display_header_footer=True,
        header_template='''
            <div style="font-size:8px; width:100%; text-align:center; color:#666; padding:0 15mm;">
                Printer Maintenance Manual
            </div>
        ''',
        footer_template='''
            <div style="font-size:8px; width:100%; text-align:center; color:#666; padding:0 15mm;">
                Page <span class="pageNumber"></span> of <span class="totalPages"></span>
                &nbsp;|&nbsp; &copy; 2026 IT Operations Team
            </div>
        ''',
        prefer_css_page_size=False
    )

    browser.close()

size_mb = output_pdf.stat().st_size / (1024 * 1024)
print(f"\nSUCCESS: PDF generated - {output_pdf}")
print(f"Size: {size_mb:.2f} MB")
