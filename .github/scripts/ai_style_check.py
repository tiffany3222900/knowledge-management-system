"""
AI Writing Style Check for MkDocs documentation.

Runs on pull requests that change docs/**/*.md files.
Fetches changed files, sends them to Google Gemini for style review,
and posts the results as a PR comment.

Supports both pull_request and workflow_dispatch triggers.
For workflow_dispatch, auto-finds the open PR for the branch.

Mode: "advisory" (default) — only comments, never fails the check.
Set FAIL_ON_CRITICAL=true in workflow env to enable hard gate mode.

Requires GEMINI_API_KEY in repo secrets.
Get a free key at: https://aistudio.google.com/apikey
Free tier: 1500 requests/day, no credit card required.
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


def find_pr_for_branch(repo, branch):
    """Find the open PR for a given branch (for workflow_dispatch triggers)."""
    pulls = repo.get_pulls(state="open", head=f"{repo.owner.login}:{branch}")
    for pr in pulls:
        return pr
    return None


def call_llm(filepath, content):
    """Call Google Gemini API (free tier, 1500 req/day)."""
    api_key = os.environ.get("GEMINI_API_KEY")
    model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
    api_version = os.environ.get("GEMINI_API_VERSION", "v1")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    url = (
        f"https://generativelanguage.googleapis.com/{api_version}/models/"
        f"{model}:generateContent?key={api_key}"
    )

    print(f"  Calling Gemini {model} ({api_version})...")

    resp = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "system_instruction": {
                "parts": [{"text": STYLE_GUIDE}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": f"Review this file: {filepath}\n\n---\n{content}\n---"}
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1500,
            },
        },
        timeout=90,
    )

    if resp.status_code != 200:
        # Print full error details for debugging
        print(f"  API Error {resp.status_code}: {resp.text}")
        raise RuntimeError(f"Gemini API {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def main():
    token = os.environ.get("GITHUB_TOKEN")
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    fail_on_critical = os.environ.get("FAIL_ON_CRITICAL", "false").lower() == "true"

    g = Github(token)
    repo = g.get_repo(repo_name)

    # Resolve PR number: from env (pull_request event) or auto-find (workflow_dispatch)
    pr_number_str = os.environ.get("PR_NUMBER")
    if pr_number_str:
        pr_number = int(pr_number_str)
        pr = repo.get_pull(pr_number)
    else:
        branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
        print(f"No PR_NUMBER set, auto-finding PR for branch: {branch}")
        pr = find_pr_for_branch(repo, branch)
        if not pr:
            print(f"ERROR: No open PR found for branch {branch}")
            sys.exit(1)
        pr_number = pr.number
        print(f"Found PR #{pr_number}: {pr.title}")

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
