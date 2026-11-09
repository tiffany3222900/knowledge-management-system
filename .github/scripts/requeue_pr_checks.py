"""
Requeue (or approve) pull_request workflow runs parked as "action_required".

PRs opened with GITHUB_TOKEN by the translation and PDF workflows have their
pull_request runs held with conclusion=action_required: no job logs, no
check-run, and approvals=[]. A required status check then never appears, so
the PR stays BLOCKED until a human clicks "rerun" in the Actions UI.

This script is called right after such a PR is created or refreshed. It polls
the Actions runs for the PR head SHA and remediates every parked run. It uses
only the standard library so both workflows can run it without installing
extra dependencies. Failures are warnings, never job failures: the docs or
PDFs were already produced successfully at this point.

Usage:
  python .github/scripts/requeue_pr_checks.py <head_sha>

Requires GITHUB_TOKEN (or GH_TOKEN) and GITHUB_REPOSITORY.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

POLL_ROUNDS = 8
POLL_INTERVAL = 4  # seconds -> up to ~32s for the runs to materialise


def api(method, path, token):
    request = urllib.request.Request(
        "https://api.github.com" + path,
        method=method,
        data=b"{}" if method == "POST" else None,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "kms-requeue-pr-checks",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
        if not body:
            return {}
        try:
            return json.loads(body)
        except ValueError:
            return {}


def list_runs(repo, sha, token):
    path = "/repos/%s/actions/runs?event=pull_request&head_sha=%s&per_page=100" % (
        repo,
        sha,
    )
    return api("GET", path, token).get("workflow_runs", [])


def remediate(repo, run_id, token):
    # Depending on the repository's approval policy the run is either a
    # "needs approval" hold (approve) or a plain parked run (rerun). Try both.
    for label, path in (
        ("rerun", "/repos/%s/actions/runs/%d/rerun" % (repo, run_id)),
        ("approve", "/repos/%s/actions/runs/%d/approve" % (repo, run_id)),
    ):
        try:
            api("POST", path, token)
            print("  %s succeeded for run %d" % (label, run_id))
            return True
        except urllib.error.HTTPError as exc:
            print("  %s returned HTTP %s for run %d" % (label, exc.code, run_id))
        except Exception as exc:
            print("  %s failed for run %d: %s" % (label, run_id, exc))
    print("::warning::Could not remediate run %d; the PR may need a manual rerun" % run_id)
    return False


def main():
    if len(sys.argv) < 2:
        print("usage: requeue_pr_checks.py <head_sha>", file=sys.stderr)
        return 1

    sha = sys.argv[1]
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        print("::warning::GITHUB_TOKEN / GITHUB_REPOSITORY missing; cannot requeue PR checks")
        return 0

    handled = set()
    stable_rounds = 0
    for round_no in range(1, POLL_ROUNDS + 1):
        try:
            runs = list_runs(repo, sha, token)
        except Exception as exc:
            print("::warning::Could not list PR workflow runs: %s" % exc)
            return 0

        parked = [
            run
            for run in runs
            if run.get("conclusion") == "action_required" and run["id"] not in handled
        ]
        if parked:
            print("Round %d: %d parked run(s)" % (round_no, len(parked)))
            for run in parked:
                handled.add(run["id"])
                remediate(repo, run["id"], token)
            stable_rounds = 0
        elif runs:
            stable_rounds += 1
            print("Round %d: %d run(s), none parked" % (round_no, len(runs)))
            # Runs can appear asynchronously; require two quiet rounds.
            if stable_rounds >= 2:
                break
        else:
            print("Round %d: no pull_request runs yet for %s" % (round_no, sha[:8]))

        if round_no < POLL_ROUNDS:
            time.sleep(POLL_INTERVAL)

    if handled:
        print("Remediated %d parked run(s); required checks should now report." % len(handled))
    else:
        print("No parked runs detected; PR checks were not blocked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
