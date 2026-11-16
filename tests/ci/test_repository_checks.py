"""Regression tests for CI tooling, owned by Hisham.

Inputs: temporary synthetic Git checkouts and deliberately invalid text; no app data.
Outputs: unittest results for failure detection and safe handling of valid files.
Responsibilities: prove broken syntax/JSON/links and force-tracked ignored files fail,
while Unicode, documentation examples, safe filenames and ignored local files work.
Connections: scripts/check_repository.py and the Repository checks Actions job.
Implementation: standard-library tests; no project dependencies or application imports.
Limits: tests CI behavior, never model accuracy, API behavior or frontend functionality.
Acceptance: the suite passes locally and on the same Python 3.11 CI commands.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.check_repository import (
    IGNORE_PROBES, MODULES, REQUIRED_FILES, check_file, check_repository,
    ignored_paths, repository_files,
)


class RepositoryChecksTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def init_git(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)

    def test_python_syntax_failure(self):
        self.write("invalid.py", "def broken(:\n")
        self.assertIn("invalid Python syntax", check_file(self.root, "invalid.py")[0])

    def test_python_is_compiled_but_never_executed(self):
        self.write("valid.py", "raise RuntimeError('must never execute')\n")
        self.assertEqual(check_file(self.root, "valid.py"), [])

    def test_json_valid_unicode_and_invalid_content(self):
        self.write("labels.json", json.dumps({"text": "ماء"}, ensure_ascii=False))
        self.assertEqual(check_file(self.root, "labels.json"), [])
        for content in ['{"bad":}', '{"x":NaN}', '{"x":Infinity}', '{"x":1,"x":2}']:
            with self.subTest(content=content):
                self.write("invalid.json", content)
                self.assertTrue(check_file(self.root, "invalid.json"))

    def test_missing_local_link_and_image_fail(self):
        self.write("README.md", "[Missing](absent.md)\n![Missing](absent.png)\n")
        self.assertEqual(len(check_file(self.root, "README.md")), 2)

    def test_encoded_and_angle_links_and_fragments_pass(self):
        self.write("docs/Arabic Guide.md", "# Guide\n")
        self.write("README.md", "[Guide](docs/Arabic%20Guide.md#scope)\n"
                   "[Guide](<docs/Arabic Guide.md>)\n[Here](#local)\n"
                   "[Web](https://example.invalid/no-network-request)\n")
        self.assertEqual(check_file(self.root, "README.md"), [])

    def test_documentation_code_examples_are_not_links(self):
        self.write("README.md", "```markdown\n[Example](absent.md)\n```\n"
                   "~~~markdown\n[Example](absent.md)\n~~~\n"
                   "`[Example](absent.md)`\n<!-- [Example](absent.md) -->\n")
        self.assertEqual(check_file(self.root, "README.md"), [])

    def test_link_cannot_escape_checkout(self):
        self.write("README.md", "[Outside](../outside.md)\n")
        self.assertTrue(check_file(self.root, "README.md"))

    def test_symlink_is_not_followed(self):
        target = self.write("target.json", "{}")
        (self.root / "link.json").symlink_to(target)
        self.assertTrue(check_file(self.root, "link.json"))

    def test_utf8_error_has_safe_diagnostic(self):
        (self.root / "invalid.json").write_bytes(b"\xff")
        self.assertTrue(check_file(self.root, "invalid.json"))

    def test_git_lists_untracked_safe_files_with_spaces(self):
        self.init_git()
        self.write(".gitignore", ".env\n")
        self.write(".env", "not-a-secret\n")
        self.write("safe guide.md", "# Guide\n")
        self.assertIn("safe guide.md", repository_files(self.root))
        self.assertNotIn(".env", repository_files(self.root))

    def test_force_tracked_ignored_file_is_detected(self):
        self.init_git()
        self.write(".gitignore", ".env\n")
        self.write(".env", "not-a-secret\n")
        subprocess.run(["git", "add", "--force", "--", ".env"], cwd=self.root, check=True)
        self.assertIn(".env", repository_files(self.root))
        self.assertEqual(ignored_paths(self.root, [".env"]), {".env"})

    def test_repository_checks_require_structure_and_ignore_policy(self):
        self.init_git()
        self.write(".gitignore", "")
        failures, _ = check_repository(self.root)
        self.assertTrue(any("required repository file" in item for item in failures))
        self.assertTrue(any("ignore protection" in item for item in failures))

    def test_checkout_without_optional_agents_file_passes_then_broken_json_fails(self):
        self.init_git()
        for relative in REQUIRED_FILES:
            self.write(relative, "{}" if relative.endswith(".json") else "# Synthetic\n")
        for module in MODULES:
            self.write(f"{module}/README.md", "# Synthetic module guide\n")
        self.write(".gitignore", "\n".join(IGNORE_PROBES) + "\n")
        self.assertFalse((self.root / "AGENTS.md").exists())
        self.assertEqual(check_repository(self.root)[0], [])
        self.write("bad.json", "{broken}")
        self.assertTrue(any("invalid JSON" in item for item in check_repository(self.root)[0]))


if __name__ == "__main__":
    unittest.main()
