"""Check Signova's repository without importing or running application modules.

Owner: Hisham; module owners review any change to the checked boundaries.
Inputs: Git-tracked files, unignored local additions, and the repository ignore policy.
Outputs: content-free file/line diagnostics and a nonzero exit status on failure.
Responsibilities: check structure, Python syntax, strict JSON, inline local Markdown
links, and files accidentally tracked despite .gitignore; verify key ignore rules.
Connections: .github/workflows/ci.yml, tests/ci, and docs/runbooks/continuous-integration.md.
Implementation: standard-library checks shared by local development and GitHub Actions.
Limitations: no app tests, dependency/import resolution, TypeScript checking, remote
link/anchor checks, or complete secret scanning; application code may replace placeholders.
Acceptance: invalid input fails safely; valid Arabic/encoded links pass; ignored local
data is not read; force-tracked ignored files fail; Python is never executed.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


REQUIRED_FILES = (
    "AGENTS.md", "START-HERE.md", ".gitignore", "frontend/package.json",
    ".github/workflows/ci.yml", "tests/ci/test_repository_checks.py",
)
MODULES = (
    "frontend", "backend", "ml", "ml/alphabet", "ml/words", "ml/common",
    "data", "artifacts", "docs", "scripts", "tests", ".github/workflows",
)
IGNORE_PROBES = (
    "frontend/.env.local", "backend/.env", "backend/.venv/pyvenv.cfg",
    "frontend/node_modules/example/index.js", "backend/app/__pycache__/example.pyc",
    "data/raw/__ci_probe__.csv", "data/interim/__ci_probe__.csv",
    "data/processed/__ci_probe__.csv", "data/features/__ci_probe__.csv",
    "artifacts/alphabet/__ci_probe__.PT", "artifacts/words/__ci_probe__.onnx",
    "backend/recordings/__ci_probe__.json", "backend/inference_tmp/__ci_probe__.dat",
)
INLINE_LINK = re.compile(
    r"!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)]+))"
    r"(?:\s+[\"'][^\n]*?[\"'])?\s*\)"
)


def git(root: Path, *arguments: str, input_bytes: bytes | None = None):
    """Run Git without a shell or the machine's global excludes file."""
    return subprocess.run(
        ["git", "-c", f"core.excludesFile={os.devnull}", *arguments],
        cwd=root, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False,
    )


def repository_files(root: Path) -> list[str]:
    """Include staged/tracked files and unignored additions so local checks need no commit."""
    result = git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    if result.returncode:
        raise RuntimeError("Cannot list repository files; run inside a Git checkout.")
    return sorted(set(os.fsdecode(p) for p in result.stdout.split(b"\0") if p))


def ignored_paths(root: Path, paths: list[str] | tuple[str, ...]) -> set[str]:
    """--no-index also detects files force-added despite the ignore policy."""
    if not paths:
        return set()
    payload = b"".join(os.fsencode(p) + b"\0" for p in paths)
    result = git(root, "check-ignore", "--no-index", "-z", "--stdin", input_bytes=payload)
    if result.returncode not in (0, 1):
        raise RuntimeError("Cannot evaluate the repository ignore policy.")
    return {os.fsdecode(p) for p in result.stdout.split(b"\0") if p}


def reject_constant(value: str):
    raise ValueError("JSON contains a nonfinite number")


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON contains a duplicate key")
        result[key] = value
    return result


def visible_markdown(text: str):
    """Yield real prose lines, excluding fenced examples, inline code and HTML comments."""
    text = re.sub(r"<!--[\s\S]*?-->", lambda match: "\n" * match[0].count("\n"), text)
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            marks, rest = marker.groups()
            if fence is None:
                fence = marks
            elif marks[0] == fence[0] and len(marks) >= len(fence) and not rest.strip():
                fence = None
            continue
        if fence is None:
            yield number, re.sub(r"`+[^`\n]*`+", "", line)


def check_file(root: Path, relative: str) -> list[str]:
    """Inspect supported text types; never print private input values or execute Python."""
    path = root / relative
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        return [f"{relative}: symbolic links/outside-checkout paths are not checked in CI"]
    if not path.is_file():
        return [f"{relative}: missing file (stage intended deletions before checking locally)"]
    suffix = path.suffix.lower()
    try:
        if suffix == ".py":
            compile(path.read_bytes(), relative, "exec", dont_inherit=True)
        elif suffix == ".json":
            json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant,
                       object_pairs_hook=unique_keys)
        elif suffix == ".md":
            failures = []
            for line, text in visible_markdown(path.read_text(encoding="utf-8")):
                for match in INLINE_LINK.finditer(text):
                    target = urlsplit(match.group(1) or match.group(2))
                    if target.scheme or target.netloc or not target.path:
                        continue
                    decoded = unquote(target.path)
                    destination = (root / decoded.lstrip("/") if decoded.startswith("/")
                                   else path.parent / decoded).resolve()
                    if not destination.is_relative_to(root.resolve()) or not destination.exists():
                        failures.append(f"{relative}:{line}: local link target is missing/outside checkout")
            return failures
    except SyntaxError as error:
        return [f"{relative}:{error.lineno}: invalid Python syntax"]
    except json.JSONDecodeError as error:
        return [f"{relative}:{error.lineno}: invalid JSON"]
    except (ValueError, UnicodeError, OSError):
        return [f"{relative}: invalid/unreadable {suffix.lstrip('.')} content"]
    return []


def check_repository(root: Path) -> tuple[list[str], int]:
    files = repository_files(root)
    failures = []
    for name in REQUIRED_FILES:
        if name not in files:
            failures.append(f"{name}: required repository file is missing")
    for module in MODULES:
        if f"{module}/README.md" not in files:
            failures.append(f"{module}/README.md: module guide is missing")
    blocked = ignored_paths(root, files)
    failures.extend(f"{p}: tracked file violates .gitignore; remove it from Git" for p in sorted(blocked))
    unprotected = set(IGNORE_PROBES) - ignored_paths(root, IGNORE_PROBES)
    failures.extend(f"{p}: required ignore protection is missing" for p in sorted(unprotected))
    for relative in files:
        if relative not in blocked:
            failures.extend(check_file(root, relative))
    return failures, len(files)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        failures, count = check_repository(root)
    except (OSError, RuntimeError):
        print("Repository checks failed: Git could not inspect this checkout.", file=sys.stderr)
        return 1
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        print(f"Repository checks failed with {len(failures)} issue(s).", file=sys.stderr)
        return 1
    print(f"Repository checks passed for {count} tracked/unignored files.")
    print("Checked Python syntax, strict JSON, local Markdown links, module guides and Git ignore policy.")
    print("Frontend/backend/model application suites are not configured yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
