"""
AI Writing Style Check for MkDocs documentation.

Runs on pull requests that change docs/**/*.md files.
Fetches changed files, sends them to an LLM for style review,
and posts the results as a PR comment.

Mode: "advisory" (default) — only comments, never fails the check.
Set FAIL_ON_CRITICAL=true in workflow env to enable hard gate mode.
"""
import os
import sys
import requests
from github import Github

# ──────────────────────────────────────────────
# Style guide — edit this to match your team's
# documentation standards.
# ──────────────────────────────────────────────
STYLE_GUIDE = """
You are a senior technical editor reviewing enterprise documentation.
Check the document against these standards and give actionable feedback.

## Standards

1. **Tone & Voice**
   - Professional, objective, second-person ("you")
   - No colloquialisms, no contractions in formal sections
   - Avoid "just", "simply", "easy", "obviously" (belittling words)

2. **Structure**
   - Procedures use numbered steps, each starting with an imperative verb
   - One idea per paragraph; paragraphs ≤ 5 lines
   - Headings follow hierarchy: # → ## → ### (no skipping levels)
   - Each page has a clear intro paragraph stating purpose

3. **Terminology (for printer maintenance context)**
   - Use "toner cartridge", not "ink cartridge" (unless inkjet model)
   - Use "paper jam", not "paper stuck"
   - Use "control panel", not "screen" or "display"
   - Model numbers in bold on first mention

4. **Safety & Warnings**
   - Electrical/thermal hazards must use !!! warning admonition
   - Caution for non-injury damage, Note for supplementary info
   - Never bury safety instructions in a normal paragraph

5. **Formatting**
   - Buttons and UI elements in **bold**
   - File paths and commands in `code`
   - No orphan links (every link text describes the destination)
   - Tables have header rows; no empty cells

6. **Completeness**
   - Every procedure has: prerequisites, steps, expected result
   - Troubleshooting entries have: symptom → cause → fix
   - No "TBD", "TODO", "coming soon" placeholders

## Output Format

**Overall rating:** A / B / C / D

**Strengths:** (2-3 bullet points)

**Issues:**
- [Severity: High/Medium/Low] File:line — description
  Suggested fix: "..."

**Summary:** one sentence on whether this is ready to merge.

Be concise. Only flag real issues, not style preferences.
If the document is clean, say so explicitly.
"""


def get_changed_md_files(repo, pr_number):
    """Return list of changed markdown file paths in this PR."""
    pr = repo.get_pull(pr_number)
    files = []
    for f in pr.get_files():
        if f.filename.endswith(".md") and f.filename.startswith("docs/"):
            files.append(f.filename)
    return files


def call_llm(filepath, content):
    """Call OpenAI Chat Completions API."""
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": STYLE_GUIDE},
                {
                    "role": "user",
                    "content": f"Review this file: {filepath}\n\n"
                    f"---\n{content}\n---",
                },
            ],
            "temperature": 0.3,
            "max_tokens": 1500,
        },
        timeout=90,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main():
    token = os.environ.get("GITHUB_TOKEN")
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    pr_number = int(os.environ.get("PR_NUMBER"))
    fail_on_critical = os.environ.get("FAIL_ON_CRITICAL", "false").lower() == "true"

    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    changed = get_changed_md_files(repo, pr_number)
    if not changed:
        print("No markdown files changed in docs/, skipping style check.")
        return

    print(f"Found {len(changed)} changed markdown file(s):")
    for f in changed:
        print(f"  - {f}")

    results = []
    has_critical = False

    for filepath in changed:
        print(f"\nReviewing {filepath} ...")
        try:
            raw = repo.get_contents(filepath, ref=pr.head.sha)
            content = raw.decoded_content.decode("utf-8")
        except Exception as e:
            results.append(f"### 📄 {filepath}\n\n⚠️ Could not read file: {e}")
            continue

        try:
            review = call_llm(filepath, content)
        except Exception as e:
            results.append(
                f"### 📄 {filepath}\n\n⚠️ AI review failed: {e}"
            )
            continue

        results.append(f"### 📄 {filepath}\n\n{review}")
        if "Overall rating:** D" in review or "Overall rating: D" in review:
            has_critical = True

    # Post comment to PR
    comment = (
        "## 🤖 AI Writing Style Check\n\n"
        + "\n\n---\n\n".join(results)
        + "\n\n---\n"
        + "_This is an automated advisory review. "
        + "Human review is still required._\n"
    )
    pr.create_issue_comment(comment)
    print("\n✅ Style review posted to PR.")

    if fail_on_critical and has_critical:
        print("\n❌ Critical style issues found — failing the check.")
        sys.exit(1)


if __name__ == "__main__":
    main()
