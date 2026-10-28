#!/usr/bin/env python3
"""Hook test harness.

Feeds every case in tests/cases/*.json to its hook as the JSON payload Claude
Code sends on stdin, and checks the outcome: "block" means exit 2 with a reason
on stderr, "ask" means exit 0 with a PreToolUse "ask" decision on stdout,
"allow" means exit 0 with no decision. Any other exit code fails the case.

Run from anywhere: python3 plugins/agent-team/hooks/tests/run_tests.py
See hooks/README.md for the case format.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
HOOKS_DIR = TESTS_DIR.parent
CASES_DIR = TESTS_DIR / "cases"
TEAM_CONFIG = TESTS_DIR / "fixtures" / "agent-team.json"


def git(*args, cwd):
    subprocess.run(
        ["git", "-c", "user.name=harness", "-c", "user.email=harness@local.test", *args],
        cwd=cwd, check=True, capture_output=True, env=clean_env(),
    )


def clean_env():
    # Keep the caller's git state (GIT_DIR, GIT_WORK_TREE...) out of the fixtures.
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def make_fixtures(root):
    """Throwaway repos, deleted when the run ends. Keys are used as {repo:<key>}."""
    fixtures = {}
    # Each repo has one commit on main, then moves to its state.
    for key, move in (("main", None), ("feature", ["switch", "-q", "-c", "feat/test"]),
                      ("detached", ["checkout", "-q", "--detach"])):
        path = root / key
        path.mkdir()
        git("init", "-q", "-b", "main", cwd=path)
        git("commit", "-q", "--allow-empty", "-m", "init", cwd=path)
        if move:
            git(*move, cwd=path)
        fixtures[f"{{repo:{key}}}"] = str(path)

    plain = root / "plain"
    plain.mkdir()
    fixtures["{dir:plain}"] = str(plain)
    # {project}: a repo set up for agent-team (.claude/agent-team.json from the fixture).
    project = root / "project"
    (project / ".claude").mkdir(parents=True)
    (project / ".claude" / "agent-team.json").write_text(TEAM_CONFIG.read_text())
    fixtures["{project}"] = str(project)
    fixtures["{tests}"] = str(TESTS_DIR)
    return fixtures


def fill(value, fixtures):
    if isinstance(value, str):
        for token, path in fixtures.items():
            value = value.replace(token, path)
        return value
    if isinstance(value, dict):
        return {k: fill(v, fixtures) for k, v in value.items()}
    if isinstance(value, list):
        return [fill(v, fixtures) for v in value]
    return value


def decision(stdout):
    try:
        output = json.loads(stdout)
    except ValueError:
        return None
    if not isinstance(output, dict):
        return None
    return (output.get("hookSpecificOutput") or {}).get("permissionDecision")


def context(stdout):
    try:
        output = json.loads(stdout)
    except ValueError:
        return ""
    return (output.get("hookSpecificOutput") or {}).get("additionalContext", "") if isinstance(output, dict) else ""


def run_case(hook, case, fixtures):
    # python3 exits 2 on a missing script, which would pass as a block.
    if not (HOOKS_DIR / hook).is_file():
        return False, "missing hook", f"{hook} not found in {HOOKS_DIR}"
    # Files the hook reads (a ticket before an edit), written before the case runs.
    for path, content in case.get("files", {}).items():
        target = Path(fill(path, fixtures))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(fill(content, fixtures))
    for link, target in case.get("symlinks", {}).items():
        link = Path(fill(link, fixtures))
        link.parent.mkdir(parents=True, exist_ok=True)
        if not link.is_symlink():
            link.symlink_to(fill(target, fixtures))
    project = fill(case.get("project", "{project}"), fixtures)
    extra_env = fill(case.get("env", {}), fixtures)
    if "stdin" in case:
        stdin = case["stdin"]
    else:
        payload = {"hook_event_name": "PreToolUse", "cwd": "{project}", **case["payload"]}
        stdin = json.dumps(fill(payload, fixtures))
    result = subprocess.run(
        [sys.executable, str(HOOKS_DIR / hook)],
        input=stdin, capture_output=True, text=True, timeout=10,
        env={**clean_env(), "CLAUDE_PROJECT_DIR": project, **extra_env},
    )
    reason = result.stderr.strip()
    if result.returncode == 2:
        got = "block" if reason else "block without reason"
    elif result.returncode == 0:
        got = "ask" if decision(result.stdout) == "ask" else "allow"
    else:
        got = f"exit {result.returncode}"
    ok = got == case["expect"]
    # "context": text the hook must add for the main session (allow + additionalContext).
    if ok and "context" in case and case["context"] not in context(result.stdout):
        ok, got = False, f"{got} without context '{case['context']}'"
    if ok and "reason" in case and case["reason"] not in reason:
        ok, got = False, f"{got} without reason '{case['reason']}'"
    return ok, got, reason


def main():
    files = sorted(CASES_DIR.glob("*.json"))
    passed = failed = 0
    with tempfile.TemporaryDirectory(prefix="hook-harness-") as tmp:
        fixtures = make_fixtures(Path(tmp))
        for file in files:
            suite = json.loads(file.read_text())
            print(f"\n{file.name} -> {suite['hook']}")
            for case in suite["cases"]:
                ok, got, reason = run_case(suite["hook"], case, fixtures)
                passed += ok
                failed += not ok
                mark = "PASS" if ok else "FAIL"
                line = f"  {mark}  {case['name']}  (expected {case['expect']}, got {got})"
                if not ok and reason:
                    line += f"\n        stderr: {reason}"
                print(line)
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed or not files else 0


if __name__ == "__main__":
    sys.exit(main())
