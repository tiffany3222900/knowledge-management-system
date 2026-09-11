"""
AI Auto-Fix for MkDocs documentation.

Reads all docs/*.md files from a target branch, sends each to AI for
style correction, then creates a new branch + PR with all fixes applied.

Human reviewer only needs to approve or reject the PR.

Usage:
  python ai_style_fix.py [--branch main]

Requires ZHIPU_API_KEY in repo secrets.
"""
import os
import sys
import re
import time
import requests
from github import Github
from github import InputGitTreeElement

# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
# Style guide 鈥?same rules as the checker, but
# here the AI applies them directly.
# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
STYLE_GUIDE = """
You are a senior technical editor. Your job is to FIX the documentation
according to the rules below. Output ONLY the corrected markdown content,
no explanations, no code fences, no commentary.

## Rules to apply:

1. **Tone & Voice**
   - Professional, objective, second-person ("you")
   - No colloquialisms; replace "cheaper" with "less expensive",
     "stuff" with "items", etc.
   - Remove belittling words: "just", "simply", "easy", "obviously"
   - Use "might" instead of "may" when describing possibility
     (reserve "may" for permission)

2. **Structure**
   - Procedures use numbered steps, each starting with an imperative verb
   - One idea per paragraph; paragraphs 鈮?5 lines
   - Headings follow hierarchy: # 鈫?## 鈫?### (no skipping levels)
   - Each page has a clear intro paragraph stating purpose

3. **Terminology (printer maintenance context)**
   - "toner cartridge" (not "ink cartridge" for laser printers)
   - "paper jam" (not "paper stuck")
   - "control panel" (not "screen" or "display")
   - Model numbers in bold on first mention

4. **Safety & Warnings**
   - Electrical/thermal hazards use !!! warning admonition
   - Caution for non-injury damage, Note for supplementary info
   - Safety instructions never buried in normal paragraphs

5. **Formatting**
   - Buttons and UI elements in **bold**
   - File paths and commands in `code`
   - Tables have header rows; no empty cells

6. **Completeness**
   - Every procedure has: prerequisites, steps, expected result
   - Troubleshooting entries: symptom 鈫?cause 鈫?fix
   - No "TBD", "TODO", "coming soon" placeholders

## Important:
- Preserve all technical content, facts, and code blocks exactly.
- Only fix style, tone, terminology, and formatting issues.
- Do NOT add new information or remove existing content.
- Do NOT change the meaning of any sentence.
- Output the complete corrected file, from the first line to the last.
"""


def call_ai_fix(filepath, content):
    """Call Zhipu API to fix the document style."""
    api_key = os.environ.get("ZHIPU_API_KEY")
    model = os.environ.get("ZHIPU_MODEL", "glm-4-flash")

    if not api_key:
        raise RuntimeError("ZHIPU_API_KEY is not set")

    print(f"  AI fixing {filepath} ...")

    resp = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
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
                    "content": (
                        f"Fix the style of this file ({filepath}).\n"
                        f"Output ONLY the corrected markdown, no explanations.\n\n"
                        f"---\n{content}\n---"
                    ),
                },
            ],
            "temperature": 0.2,
            "max_tokens": 8000,
        },
        timeout=180,
    )

    if resp.status_code != 200:
        raise RuntimeError(f"Zhipu API {resp.status_code}: {resp.text[:500]}")

    result = resp.json()["choices"][0]["message"]["content"]

    # Strip code fences if AI wrapped the output
    result = re.sub(r"^```markdown\s*\n", "", result)
    result = re.sub(r"^```\s*\n", "", result)
    result = re.sub(r"\n```\s*$", "", result)

    return result.strip() + "\n"


def get_all_md_files(repo, branch):
    """Get all docs/*.md files from a branch."""
    files = []
    contents = repo.get_contents("docs", ref=branch)
    while contents:
        item = contents.pop(0)
        if item.type == "dir":
            contents.extend(repo.get_contents(item.path, ref=branch))
        elif item.name.endswith(".md"):
            files.append(item.path)
    return sorted(files)


def main():
    token = os.environ.get("GITHUB_TOKEN")
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    target_branch = os.environ.get("TARGET_BRANCH", "main")

    g = Github(token)
    repo = g.get_repo(repo_name)

    print(f"Target branch: {target_branch}")
    print(f"Repository: {repo_name}")

    # Get all markdown files
    md_files = get_all_md_files(repo, target_branch)
    print(f"Found {len(md_files)} markdown files:")
    for f in md_files:
        print(f"  - {f}")

    # Process each file
    fixes = []  # list of (filepath, original, fixed, change_summary)
    failures = []  # list of (filepath, error_message)

    for filepath in md_files:
        try:
            raw = repo.get_contents(filepath, ref=target_branch)
            original = raw.decoded_content.decode("utf-8")

            fixed = call_ai_fix(filepath, original)

            if fixed != original:
                # Count changes (simple line diff)
                orig_lines = original.strip().split("\n")
                fixed_lines = fixed.strip().split("\n")
                changed = sum(
                    1 for a, b in zip(orig_lines, fixed_lines) if a != b
                )
                changed += abs(len(fixed_lines) - len(orig_lines))

                fixes.append((filepath, original, fixed, f"{changed} line(s) changed"))
                print(f"    鉁?Fixed ({changed} line(s) changed)")
            else:
                print(f"    鉁?No changes needed")

        except Exception as e:
            error_msg = str(e)
            print(f"    鉁?Error: {error_msg}")
            failures.append((filepath, error_msg))
            continue

        # Rate limiting: small delay between API calls
        time.sleep(1)

    # If ALL files failed, exit with error so CI shows failure
    if failures and not fixes:
        print(f"\n鉂?All {len(failures)} file(s) failed AI processing.")
        for filepath, error in failures:
            print(f"  - {filepath}: {error[:100]}")
        print("\nCommon causes:")
        print("  - API key not configured or invalid")
        print("  - API balance insufficient (402)")
        print("  - Network connectivity issue")
        sys.exit(1)

    if not fixes:
        print("\n鉁?All files are already clean. No PR needed.")
        return

    print(f"\n{len(fixes)} file(s) need fixes. Creating PR...")

    # Create new branch
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    new_branch = f"ai-style-fix/{timestamp}"
    base_ref = repo.get_git_ref(f"heads/{target_branch}")
    repo.create_git_ref(ref=f"refs/heads/{new_branch}", sha=base_ref.object.sha)
    print(f"Created branch: {new_branch}")

    # Commit each fixed file
    commit_messages = []
    for filepath, original, fixed, summary in fixes:
        repo.update_file(
            path=filepath,
            message=f"style(ai): fix {filepath} ({summary})",
            content=fixed,
            sha=repo.get_contents(filepath, ref=new_branch).sha,
            branch=new_branch,
        )
        commit_messages.append(f"- **{filepath}**: {summary}")
        print(f"  Committed: {filepath}")

    # Create PR
    failure_section = ""
    if failures:
        failure_lines = [f"- **{fp}**: {err[:80]}" for fp, err in failures]
        failure_section = (
            "\n### 鈿狅笍 Files Failed (not included in this PR)\n\n"
            + "\n".join(failure_lines)
            + "\n"
        )

    pr_body = (
        "## 馃 AI Style Auto-Fix\n\n"
        "This PR was automatically generated by the AI style checker.\n"
        "It applies documentation style fixes according to the project style guide.\n\n"
        "### Files Changed\n\n"
        + "\n".join(commit_messages)
        + failure_section
        + "\n"
        "### What was fixed\n\n"
        "- Tone and voice (professional, second-person)\n"
        "- Terminology consistency (toner cartridge, paper jam, control panel)\n"
        "- Safety admonitions (warning/caution/note)\n"
        "- Formatting (bold UI elements, code for commands)\n"
        "- Removed colloquialisms and belittling words\n\n"
        "### Reviewer Checklist\n\n"
        "- [ ] Technical content is preserved (no facts changed)\n"
        "- [ ] Meaning of each sentence is unchanged\n"
        "- [ ] Style improvements are reasonable\n"
        "- [ ] No accidental deletions or additions\n\n"
        "---\n"
        "_Generated by AI Style Auto-Fix workflow. "
        "Approve if changes look good, or close with a comment explaining why._\n"
    )

    pr = repo.create_pull(
        title=f"馃 AI Style Fix ({timestamp})",
        body=pr_body,
        head=new_branch,
        base=target_branch,
    )

    print(f"\n鉁?PR created: {pr.html_url}")
    print(f"   Title: {pr.title}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", default="main", help="Target branch to fix")
    args = parser.parse_args()
    os.environ["TARGET_BRANCH"] = args.branch
    main()
