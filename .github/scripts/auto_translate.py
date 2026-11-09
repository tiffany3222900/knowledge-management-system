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
# Translation prompt (incremental: update existing Chinese in place)
# ─────────────────────────────────────────────────────────────────────
TRANSLATE_PROMPT = """You are a professional technical translator specializing in IT and hardware documentation.
You are given a new English Markdown source and its EXISTING Chinese translation.
The English source has been UPDATED. Update the existing Chinese translation to match.

## Rules:
1. Translate all NEW or CHANGED English content into Simplified Chinese.
2. When an English sentence has been REWORDED, rewrite the corresponding
   Chinese sentence so it reflects the new wording, even when the underlying
   meaning is unchanged. NEVER return the old Chinese verbatim for a sentence
   whose English source changed — a style edit is still a translation task.
3. For English content that did NOT change, keep the existing Chinese
   translation EXACTLY as-is. Keep terminology consistent (e.g. keep
   "墨粉" if the existing translation uses it).
4. If English content was removed, remove the corresponding Chinese text.
5. Preserve ALL Markdown syntax exactly: # headings, **bold**, *italic*,
   `inline code`, ```code blocks```, [links](url), !!! admonitions, tables,
   numbered/bullet lists, horizontal rules.
6. Do NOT translate: code block contents, URLs, file paths, shell commands,
   brand names (HP, Brother, Canon), model numbers, technical acronyms
   (CPU, USB, PDF, LCD), MkDocs directives.
7. Admonition type keywords (warning, caution, note, info, tip) stay in
   English; only translate the title and body text.
8. Output ONLY the COMPLETE updated Markdown file. No explanations, no
   wrapping code fences, no diff or summary of what you changed.
"""


def call_ai_translate(filepath, content, existing_zh=None):
    """Call Zhipu GLM API to translate/update content.

    When existing_zh is provided, the AI updates the existing translation
    in place (incremental mode) instead of re-translating from scratch.
    """
    api_key = os.environ.get("ZHIPU_API_KEY")
    model = os.environ.get("ZHIPU_MODEL", "glm-4-flash")

    if not api_key:
        raise RuntimeError("ZHIPU_API_KEY is not set")

    print(f"  {'Updating' if existing_zh else 'Translating'} {filepath} ...")

    if existing_zh:
        user_content = (
            f"Update the Chinese translation to match this English file "
            f"({filepath}). The English text has been revised: rewrite every "
            f"Chinese sentence whose English source changed, INCLUDING pure "
            f"wording or style edits. Keep only the paragraphs whose English "
            f"source is untouched exactly as they are. Return the complete "
            f"updated Chinese document.\n\n"
            f"--- NEW ENGLISH ---\n{content}\n---\n\n"
            f"--- EXISTING CHINESE ---\n{existing_zh}\n---"
        )
    else:
        user_content = (
            f"Translate this Markdown file ({filepath}) to Simplified Chinese.\n"
            f"Output ONLY the translated content.\n\n"
            f"---\n{content}\n---"
        )

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
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.1,
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


def structural_signature(text):
    """Count the Markdown constructs a faithful translation must preserve.

    A translation changes words, not structure. If the model returns the old
    Chinese verbatim after an English table row was added, the counts differ
    and we can refuse to publish an incomplete translation instead of letting
    it look like "no translation needed".
    """
    lines = text.splitlines()
    return (
        sum(1 for line in lines if line.startswith("## ")),
        sum(1 for line in lines if line.startswith("### ")),
        sum(1 for line in lines if line.startswith("|")),
    )


def normalize_content(text):
    """Whitespace/layout-insensitive view of the *translatable* prose.

    Fenced code blocks, inline code, link targets, horizontal rules and blank
    lines are ignored: editing those does not require a Chinese wording change,
    and a model that only trims a trailing ``---`` must not be mistaken for a
    successful translation. Used both for EN (did the source really change?)
    and ZH (did the translation really change?).
    """
    lines = []
    in_code = False
    for raw in text.splitlines():
        if raw.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        line = re.sub(r"`[^`]*`", "", raw)
        line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
        line = line.strip()
        if not line or re.fullmatch(r"[-*_]{3,}", line):
            continue
        lines.append(line)
    return "\n".join(lines)


def get_previous_english(filepath):
    """Return the English page as of HEAD~1, or None when history is missing."""
    result = subprocess.run(
        ["git", "show", f"HEAD~1:{filepath}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout


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


def requeue_pr_check_runs():
    """Unblock the PR we just opened.

    PRs created with GITHUB_TOKEN have their pull_request workflows parked as
    ``action_required`` with no check-run, which leaves the required status
    check missing and the PR BLOCKED. Requeue them right away so the PR can
    actually be merged. This is best-effort and never fails the job.
    """
    try:
        head_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception as exc:
        print(f"::warning::Could not resolve HEAD SHA: {exc}")
        return

    script = os.path.join(".github", "scripts", "requeue_pr_checks.py")
    if not os.path.exists(script):
        print(f"::warning::{script} not found; skipping PR check requeue")
        return

    print(f"Checking pull_request workflow runs for {head_sha[:8]} ...")
    subprocess.run([sys.executable, script, head_sha], check=False)


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

            zh_path = filepath.replace(".md", ".zh.md")

            # Read existing Chinese translation if present (incremental mode)
            existing_zh = None
            if os.path.exists(zh_path):
                with open(zh_path, "r", encoding="utf-8") as f:
                    existing_zh = f.read()

            chinese = call_ai_translate(filepath, english, existing_zh)

            # Structural guard: the model sometimes returns the existing
            # Chinese verbatim even when a new English row/section was added.
            # Refuse that output instead of silently shipping a stale ZH page.
            en_sig = structural_signature(english)
            zh_sig = structural_signature(chinese)
            if en_sig != zh_sig:
                message = (
                    f"structural mismatch: EN {en_sig} vs ZH {zh_sig} - "
                    "translation output did not preserve the English structure"
                )
                print(f"    ERROR: {message}")
                failures.append((filepath, message))
                continue

            # A translation that only differs in blank lines, trailing
            # separators or code/link markup carries no new Chinese wording.
            zh_unchanged = (
                existing_zh is not None
                and normalize_content(existing_zh) == normalize_content(chinese)
            )
            if zh_unchanged:
                previous_en = get_previous_english(filepath)
                if previous_en is None:
                    en_state = "unknown"
                elif normalize_content(previous_en) != normalize_content(english):
                    en_state = "changed"
                else:
                    en_state = "unchanged"

                # P1 guard: English prose changed but the model handed back
                # the old Chinese. Pure wording edits do not alter the
                # structural signature, so the guard above cannot catch this.
                if en_state == "changed":
                    message = (
                        "stale translation: English prose changed but Chinese "
                        "output matches the existing translation"
                    )
                    print(f"    ERROR: {message} ({filepath})")
                    failures.append((filepath, message))
                    continue

                reason = (
                    "no substantive English prose change"
                    if en_state == "unchanged"
                    else "HEAD~1 history unavailable"
                )
                print(f"    -> unchanged, skipping {zh_path} ({reason})")
                continue

            with open(zh_path, "w", encoding="utf-8") as f:
                f.write(chinese)

            translated.append(zh_path)
            print(f"    -> wrote {zh_path}")

        except Exception as e:
            print(f"    ERROR: {e}")
            failures.append((filepath, str(e)))

        time.sleep(1)  # rate limit

    # An incomplete translation must be loud. A failed upstream run makes the
    # workflow_run gate skip stage 2 entirely, so no PDF is built from stale ZH.
    blocking_failures = [
        msg for _, msg in failures
        if msg.startswith("structural mismatch")
        or msg.startswith("stale translation")
    ]
    if blocking_failures:
        print("::error::Refusing to publish an incomplete translation "
              f"({len(blocking_failures)} file(s) failed the structural/staleness "
              "guards). Rerun the translation or update the Chinese page manually.")
        sys.exit(1)

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
            requeue_pr_check_runs()
        else:
            print(f"Failed to create PR: {resp.status_code} {resp.text[:200]}")
    else:
        print("GITHUB_TOKEN or GITHUB_REPOSITORY not set, skipping PR creation.")
        print(f"Branch {branch} is ready for manual PR creation.")


if __name__ == "__main__":
    main()
