"""Shared commit + push helper for the scripts that publish into
data/github_sync/. Several jobs (snapshot fetch, scoring, outcome
tracking) push to the same branch, so a push can be rejected because
another job pushed first -- rebase onto the remote and retry rather than
losing the run's output (the 2026-10-15 open snapshot was lost that way).
"""
import subprocess
import time

from config import PROJECT_DIR

PUSH_ATTEMPTS = 4


def git_pull():
    result = subprocess.run(
        ["git", "pull"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git pull failed: {result.stderr}")
    return result.stdout.strip()


def commit_and_push(paths, message):
    """Returns "no_changes" or "pushed". Raises if the push still fails
    after PUSH_ATTEMPTS, or if the rebase hits a conflict (the next run
    redoes the work from a clean checkout)."""
    paths = [str(p) for p in paths]
    subprocess.run(["git", "add", *paths], cwd=PROJECT_DIR, check=True, timeout=120)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=PROJECT_DIR, timeout=60)
    if diff.returncode == 0:
        return "no_changes"
    subprocess.run(["git", "commit", "-m", message], cwd=PROJECT_DIR, check=True, timeout=120)

    push = None
    for attempt in range(1, PUSH_ATTEMPTS + 1):
        push = subprocess.run(["git", "push"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=300)
        if push.returncode == 0:
            return "pushed"
        print(f"Push rejected (attempt {attempt} of {PUSH_ATTEMPTS}); rebasing onto the remote and retrying")
        time.sleep(attempt * 5)
        rebase = subprocess.run(
            ["git", "pull", "--rebase"], cwd=PROJECT_DIR, capture_output=True, text=True, timeout=300,
        )
        if rebase.returncode != 0:
            subprocess.run(["git", "rebase", "--abort"], cwd=PROJECT_DIR, capture_output=True, timeout=60)
            raise RuntimeError(f"git pull --rebase failed: {rebase.stderr or rebase.stdout}")
    raise RuntimeError(f"git push failed after {PUSH_ATTEMPTS} attempts: {push.stderr}")
