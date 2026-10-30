#!/usr/bin/env python3
"""Real West cold-start regressions using local Git fixtures, no network/SDK."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().with_name("setup_zephyr.sh")


class WestBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.workspace = root / "workspace"
        # Intentionally different from self.path: app, as on GitHub runners.
        self.app = self.workspace / "coursework-checkout"
        (self.app / "scripts").mkdir(parents=True)
        shutil.copy2(SCRIPT, self.app / "scripts/setup_zephyr.sh")
        self.env = os.environ.copy()
        self.env.pop("ZEPHYR_BASE", None)
        # Keep global/user West settings out of this local fixture.
        self.env["WEST_CONFIG_SYSTEM"] = os.devnull
        self.env["WEST_CONFIG_GLOBAL"] = os.devnull
        self.env.pop("WEST_CONFIG_LOCAL", None)
        upstream = root / "upstream-zephyr"
        upstream.mkdir()
        (upstream / "west.yml").write_text("manifest:\n  projects: []\n")
        self.run_cmd("git", "init", str(upstream))
        self.run_cmd("git", "-C", str(upstream), "add", "west.yml")
        self.run_cmd("git", "-C", str(upstream), "-c", "user.name=Harness test",
                     "-c", "user.email=harness@example.invalid", "commit", "-m", "fixture")
        revision = self.run_cmd("git", "-C", str(upstream), "rev-parse", "HEAD").stdout.strip()
        (self.app / "west.yml").write_text(
            'manifest:\n  version: "0.13"\n  projects:\n'
            f'    - name: zephyr\n      url: "{upstream.as_uri()}"\n'
            f'      revision: {revision}\n      import: true\n'
            '  self:\n    path: app\n')
        self.run_cmd("git", "init", str(self.app))

    def run_cmd(self, *args, check=True):
        result = subprocess.run(args, cwd=self.app, env=self.env,
                                text=True, capture_output=True)
        if check:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def initialize(self, check=True):
        return self.run_cmd("bash", "scripts/setup_zephyr.sh", "--init-only", check=check)

    def test_missing_import_then_update(self):
        self.initialize()
        self.assertFalse((self.workspace / "zephyr").exists())
        self.assertEqual(self.run_cmd("west", "config", "--local", "manifest.path")
                         .stdout.strip(), self.app.name)
        # Reproduce the original failure with a REAL West parser.
        missing = self.run_cmd("west", "manifest", "--path", check=False)
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("manifest", missing.stderr)
        # Download the fixture locally, then resolve the import successfully.
        self.run_cmd("west", "update", "zephyr", "--fetch-opt=--depth=1",
                     "--fetch-opt=--no-tags")
        resolved = self.run_cmd("west", "manifest", "--path").stdout.strip()
        self.assertEqual(Path(resolved).resolve(), self.app / "west.yml")
        self.initialize()

    def test_repeated_initialization_preserves_config(self):
        self.initialize()
        config = self.workspace / ".west/config"
        before = config.read_bytes()
        self.initialize()
        self.assertEqual(config.read_bytes(), before)

    def test_foreign_manifest_rejected_before_mutation(self):
        self.initialize()
        self.run_cmd("west", "config", "--local", "manifest.path", "other-app")
        config = self.workspace / ".west/config"
        before = config.read_bytes()
        result = self.initialize(check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("belongs to another manifest", result.stderr)
        self.assertEqual(config.read_bytes(), before)
        self.assertFalse((self.workspace / "zephyr").exists())

    def test_unknown_option_does_not_initialize(self):
        result = self.run_cmd("bash", "scripts/setup_zephyr.sh", "--unknown", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.workspace / ".west").exists())


if __name__ == "__main__":
    if shutil.which("west") is None:
        raise SystemExit("west is required: activate the Zephyr environment first")
    unittest.main(verbosity=2)
