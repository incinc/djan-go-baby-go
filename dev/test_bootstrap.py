"""Fast bootstrap guard tests; real Docker integration runs separately in CI."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bootstrap test ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.script = self.root / "bootstrap.sh"
        self.script.write_bytes(
            (Path(__file__).resolve().parents[1] / "bootstrap.sh").read_bytes()
        )
        self.calls = self.root / "calls"
        docker = self.root / "docker"
        docker.write_text(
            '#!/bin/sh\nprintf "%s\\n" "$*" >> "$BOOTSTRAP_CALLS"\nexit 23\n'
        )
        docker.chmod(0o755)
        self.env = {
            **os.environ,
            "PATH": f"{self.root}:{os.environ['PATH']}",
            "BOOTSTRAP_CALLS": str(self.calls),
        }

    def run_bootstrap(self, *args):
        return subprocess.run(
            ["sh", str(self.script), *args],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
        )

    def test_invalid_names_do_not_run_docker_or_modify_files(self):
        for name in (
            "",
            "1project",
            "Project",
            "with-dash",
            "class",
            "app",
            "mcp",
            "bad;command",
        ):
            with self.subTest(name=name):
                self.assertNotEqual(self.run_bootstrap(name).returncode, 0)
                self.assertFalse(self.calls.exists())
                self.assertTrue(self.script.exists())

    def test_existing_target_is_rejected(self):
        (self.root / "existing").mkdir()
        self.assertNotEqual(self.run_bootstrap("existing").returncode, 0)
        self.assertFalse(self.calls.exists())

    def test_container_failure_stops_before_build_or_up(self):
        result = self.run_bootstrap("valid_project", "-d")
        self.assertEqual(result.returncode, 23)
        self.assertTrue(self.calls.read_text().startswith("run --rm"))
        self.assertNotIn("compose build", self.calls.read_text())
        self.assertNotIn("compose up", self.calls.read_text())

    def test_build_failure_stops_before_migrations(self):
        (self.root / "docker").write_text(
            '#!/bin/sh\nprintf "%s\\n" "$*" >> "$BOOTSTRAP_CALLS"\n'
            'if [ "$1" = run ]; then exit 0; fi\nexit 23\n'
        )
        result = self.run_bootstrap("valid_project", "-d")
        self.assertEqual(result.returncode, 23)
        self.assertIn("compose build", self.calls.read_text())
        self.assertNotIn("compose run", self.calls.read_text())
        self.assertNotIn("compose up", self.calls.read_text())
