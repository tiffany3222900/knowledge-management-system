"""
Incremental auto-translation: English docs -> Chinese (.zh.md).

Triggered on push to main when English .md files change.
Only translates changed files (not the whole docs folder).
Opens a PR for human review instead of pushing directly to main.

Usage:
  python auto_translate.py

Requires ZHIPU_API_KEY in repo secrets.
"""
import os
import sys
import re
import subprocess
import time
import requests

# ─────────────────────────────────────────────────────────────────────
# Translation prompt
# ─────────────────────────────────────────────────────────────────────
TRANSLATE_PROMPT = """You are a professional technical translator specializing in IT and hardware documentation.
Translate the following English Markdown into Simplified Chinese.

## Rules:
1. Translate all visible text: headings, paragraphs, list items, table cells, admonition titles.
2. Preserve ALL Markdown syntax exactly: # headings, **bold**, *italic*, `inline code`, ```code blocks```, [links](url), !!! admonitions, tables, numbered/bullet lists, horizontal rules.
3. Do NOT translate: code block contents, URLs, file paths, shell commands, brand names (HP, Brother, Canon), model numbers, technical acronyms (CPU, USB, PDF, LCD), MkDocs directives.
4. Admonition type keywords (warning, caution, note, info, tip) stay in English; only translate the title and body text.
5. Keep the same line count and structure as much as possible.
6. Output ONLY the translated Markdown. No explanations, no wrapping code fences.
"""


def call_ai_translate(filepath, content):
    """Call Zhipu GLM API to translate content."""
    api_key = os.environ.get("ZHIPU_API_KEY")
    model = os.environ.get("ZHIPU_MODEL", "glm-4-flash")

    if not api_key:
        raise RuntimeError("ZHIPU_API_KEY is not set")

    print(f"  Translating {filepath} ...")

    resp = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": TRANSLATE_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Translate this Markdown file ({filepath}) to Simplified Chinese.\n"
                        f"Output ONLY the translated content.\n\n"
                        f"---\n{content}\n---"
                    ),
                },
            ],
            "temperature": 0.3,
            "max_tokens": 8000,
        },
        timeout=180,
    )

    if resp.status_code != 200:
        raise RuntimeError(f"Zhipu API {resp.status_code}: {resp.text[:500]}")

    result = resp.json()["choices"][0]["message"]["content"]

    # Strip code fences if AI wrapped output
    result = re.sub(r"^```markdown\s*\n", "", result)
    result = re.sub(r"^```\s*\n", "", result)
    result = re.sub(r"\n```\s*$", "", result)

    return result.strip() + "\n"


def get_changed_english_files():
    """Return list of changed English .md files (excluding .zh.md) from latest commit."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("  WARNING: HEAD~1 not available, translating all English docs")
        result = subprocess.run(
            ["git", "ls-files", "docs/*.md"],
            capture_output=True, text=True,
        )

    files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    english = [
        f for f in files
        if f.startswith("docs/")
        and f.endswith(".md")
        and not f.endswith(".zh.md")
    ]
    return english


def main():
    changed = get_changed_english_files()

    if not changed:
        print("No English .md files changed in this push. Nothing to translate.")
        return

    print(f"Found {len(changed)} changed English file(s):")
    for f in changed:
        print(f"  - {f}")

    translated = []
    failures = []

    for filepath in changed:
        if not os.path.exists(filepath):
            print(f"  SKIP {filepath} (file no longer exists, likely deleted)")
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                english = f.read()

            chinese = call_ai_translate(filepath, english)

            zh_path = filepath.replace(".md", ".zh.md")

            # Skip if translation is identical to existing
            if os.path.exists(zh_path):
                with open(zh_path, "r", encoding="utf-8") as f:
                    existing = f.read()
                if existing.strip() == chinese.strip():
                    print(f"    -> unchanged, skipping {zh_path}")
                    continue

            with open(zh_path, "w", encoding="utf-8") as f:
                f.write(chinese)

            translated.append(zh_path)
            print(f"    -> wrote {zh_path}")

        except Exception as e:
            print(f"    ERROR: {e}")
            failures.append((filepath, str(e)))

        time.sleep(1)  # rate limit

    if failures and not translated:
        print(f"\nAll {len(failures)} file(s) failed.")
        sys.exit(1)

    if not translated:
        print("\nNo new translations needed.")
        return

    # Create branch, commit, push, and open PR
    print(f"\nCreating PR with {len(translated)} translated file(s)...")
    subprocess.run(
        ["git", "config", "user.name", "github-actions[bot]"],
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"],
        check=True,
    )
    subprocess.run(["git", "add"] + translated, check=True)

    # Check for actual changes
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], capture_output=True
    )
    if diff.returncode == 0:
        print("No changes to commit.")
        return

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    branch = f"auto/translate-{timestamp}"
    file_list = "\n".join(f"- {f}" for f in translated)
    commit_msg = f"docs: auto-translate EN->ZH [skip translate]\n\n{file_list}"

    subprocess.run(["git", "checkout", "-b", branch], check=True)
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    subprocess.run(["git", "push", "origin", branch], check=True)
    print(f"Pushed to branch {branch}")

    # Open PR via GitHub API
    token = os.environ.get("GITHUB_TOKEN")
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    if token and repo_name:
        pr_body = (
            "## [AI] Auto Translation (EN -> ZH)\n\n"
            "This PR was automatically generated by the incremental translation workflow.\n"
            "It contains Chinese translations for recently changed English documents.\n\n"
            "### Files Translated\n\n"
            f"{file_list}\n\n"
            "### Reviewer Checklist\n\n"
            "- [ ] Translation accuracy is acceptable\n"
            "- [ ] Markdown formatting is preserved\n"
            "- [ ] Technical terms are correctly translated\n\n"
            "---\n"
            "_Generated by Auto Translate workflow. Approve if translations look good._\n"
        )
        resp = requests.post(
            f"https://api.github.com/repos/{repo_name}/pulls",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
            json={
                "title": f"[AI] Auto Translate ({timestamp})",
                "body": pr_body,
                "head": branch,
                "base": "main",
            },
            timeout=30,
        )
        if resp.status_code == 201:
            pr_url = resp.json()["html_url"]
            print(f"PR created: {pr_url}")
        else:
            print(f"Failed to create PR: {resp.status_code} {resp.text[:200]}")
    else:
        print("GITHUB_TOKEN or GITHUB_REPOSITORY not set, skipping PR creation.")
        print(f"Branch {branch} is ready for manual PR creation.")


if __name__ == "__main__":
    main()
