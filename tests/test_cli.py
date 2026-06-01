from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, manifest: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "jp_geo_game_qa",
                "validate",
                str(ROOT / "examples" / manifest),
                "--json",
            ],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

    def test_sample_manifest_passes(self) -> None:
        proc = self.run_cli("sample_manifest.json")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        report = json.loads(proc.stdout)
        self.assertEqual(report["status"], "PASS")

    def test_broken_manifest_fails(self) -> None:
        proc = self.run_cli("broken_manifest.json")
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        report = json.loads(proc.stdout)
        self.assertEqual(report["status"], "FAIL")
        failed = {gate["id"] for gate in report["gates"] if gate["status"] == "FAIL"}
        self.assertIn("REQUIRED_LOD_COVERAGE", failed)
        self.assertIn("BROAD_WATER_NO_INTERNAL_CENTERLINES", failed)
        self.assertIn("ROAD_WATER_CROSSINGS_RESOLVED", failed)
        self.assertIn("VISIBLE_ROADS_HAVE_MARKINGS", failed)
        self.assertIn("UNDERGROUND_RAIL_NOT_SURFACE", failed)
        self.assertIn("VISUAL_CHECKPOINT_EVIDENCE_PRESENT", failed)


if __name__ == "__main__":
    unittest.main()
