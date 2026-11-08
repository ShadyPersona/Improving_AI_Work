import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


PROJECT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("s5", PROJECT / "s5-harness.py")
s5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s5)


class G1Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.original = s5.ROOT
        self.addCleanup(setattr, s5, "ROOT", self.original)
        s5.ROOT = Path(self.temp.name)
        self.rd = s5.ROOT / "runs" / "test"
        self.rd.mkdir(parents=True)
        (s5.ROOT / "schemas").mkdir()
        for path in (PROJECT / "schemas").glob("*.json"):
            (s5.ROOT / "schemas" / path.name).write_bytes(path.read_bytes())
        sources = []
        for name, role in [("prior-report.md", "prior-report"),
                           ("history-report.md", "history-report"),
                           ("cis.md", "cis-ref"), ("nist.md", "nist-ref"),
                           ("defender-export-folder/a.csv", "defender-export"),
                           ("defender-export-folder/b.csv", "defender-export")]:
            path = self.rd / "inputs" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic", encoding="utf-8")
            sources.append({"path": "inputs/" + name, "role": role,
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        self.inv = {"sources": sources, "export_files": [s["path"] for s in sources[-2:]],
                    "section_map": [{"heading": "Identity", "order": 1}]}
        self.idx = {"files": [dict(path=s["path"], sha256=s["sha256"],
                                   domain="identities", description="Synthetic") for s in sources[-2:]]}
        self.style = dict(voice="formal", tense="present", sentence_style="concise",
                          phrasing_conventions=[], formatting_conventions=[], banned_patterns=[])
        self.write("dispatch-received-01.json", {"agent": "01-ingest"})

    def write(self, name, value):
        (self.rd / name).write_text(json.dumps(value), encoding="utf-8")

    def result(self):
        for name, value in [("inventory.json", self.inv), ("evidence-index.json", self.idx),
                            ("style-profile.json", self.style)]:
            self.write(name, value)
        with patch.dict("sys.modules", {"jsonschema": None}):
            return s5.g1_check("test")["result"]

    def test_drive_bootstrap(self):
        cfg = copy.deepcopy(s5.DEFAULT_CONFIG)
        cfg["runner"]["mode"] = "manual"
        self.assertEqual(s5.advance("fresh", cfg)["action"], "needs-inputs")
        action = s5.advance("fresh", cfg)
        self.assertEqual(action["action"], "execute_step")
        self.assertEqual(action["step"], "01")
        self.assertTrue(Path(action["prompt_file"]).exists())
        self.assertEqual(s5.load_state("fresh")["status"], "needs-step01")
        self.assertEqual(s5.advance("fresh", cfg)["action"], "wait")

    def test_drive_ingest_through_g1(self):
        cfg = copy.deepcopy(s5.DEFAULT_CONFIG)
        cfg["runner"]["mode"] = "manual"
        action = s5.advance("test", cfg)
        self.assertEqual(action["action"], "execute_step")
        self.assertEqual(self.result(), "pass")
        marker = self.rd / ".harness-step01-done"
        marker.touch()
        self.assertEqual(s5.advance("test", cfg)["action"], "wait")
        self.assertFalse(marker.exists())
        action = s5.advance("test", cfg)
        self.assertEqual(action["step"], "02")
        self.assertEqual(s5.load_state("test")["status"], "needs-step02")
        self.assertFalse((self.rd / "matrix.json").exists())
        record = json.loads((s5.ROOT / "audit/run-test.jsonl")
                            .read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(record["input_hash_scope"], "declared-dependencies")
        self.assertEqual(record["missing_declared_inputs"], [])
        self.assertIn("runs/test/inputs/defender-export-folder/a.csv",
                      record["input_hashes"])
        self.assertIn("runs/test/inputs/defender-export-folder/b.csv",
                      record["input_hashes"])
        self.assertIn("runs/test/inventory.json", record["output_hashes"])

    def test_declared_input_hashes(self):
        nested = self.rd / "inputs/defender-export-folder/nested/a.csv"
        nested.parent.mkdir(parents=True)
        nested.write_text("nested", encoding="utf-8")
        hashes, missing = s5._declared_input_hashes(
            "test", s5.DEFAULT_CONFIG, "01")
        self.assertEqual(missing, [])
        self.assertEqual(len(hashes), 7)
        self.assertIn("runs/test/inputs/defender-export-folder/a.csv", hashes)
        self.assertIn("runs/test/inputs/defender-export-folder/nested/a.csv",
                      hashes)
        before = hashes["runs/test/inputs/defender-export-folder/b.csv"]
        (self.rd / "inputs/defender-export-folder/b.csv").write_text(
            "changed", encoding="utf-8")
        after, _ = s5._declared_input_hashes(
            "test", s5.DEFAULT_CONFIG, "01")
        self.assertNotEqual(
            before, after["runs/test/inputs/defender-export-folder/b.csv"])

    def test_step_specific_and_missing_dependencies(self):
        self.write("inventory.json", {})
        self.write("evidence-index.json", {})
        self.write("matrix.json", {"rows": []})
        hashes, missing = s5._declared_input_hashes(
            "test", s5.DEFAULT_CONFIG, "02")
        self.assertEqual(missing, [])
        self.assertNotIn("runs/test/matrix.json", hashes)
        self.assertNotIn("runs/test/inputs/cis.md", hashes)
        s5.init_run("test")
        hashes, missing = s5._declared_input_hashes(
            "test", s5.DEFAULT_CONFIG, "03a")
        self.assertEqual(missing, [])
        self.assertIn("runs/test/matrix.json", hashes)
        self.assertIn("runs/test/run-state.json", hashes)
        (self.rd / "inventory.json").unlink()
        _, missing = s5._declared_input_hashes(
            "test", s5.DEFAULT_CONFIG, "02")
        self.assertEqual(missing, ["runs/test/inventory.json"])

    def test_clean(self):
        self.assertEqual(self.result(), "pass")

    def test_negative_fixtures(self):
        inv, idx, style = copy.deepcopy((self.inv, self.idx, self.style))
        mutations = [
            lambda: self.inv["sources"][0].update(sha256="0" * 64),
            lambda: self.idx["files"][0].update(sha256="0" * 64),
            lambda: self.idx["files"].pop(),
            lambda: self.inv["export_files"].pop(),
            lambda: self.inv["sources"].pop(),
            lambda: self.idx["files"][0].update(path="inputs/missing.csv"),
            lambda: self.idx["files"][0].update(path="../outside.csv"),
            lambda: self.idx["files"][0].update(domain="invalid"),
            lambda: self.style.pop("sentence_style"),
            lambda: self.inv.update(sources=[None]),
            lambda: self.inv["sources"].append(copy.deepcopy(self.inv["sources"][0])),
        ]
        for number, mutate in enumerate(mutations):
            with self.subTest(number=number):
                self.inv, self.idx, self.style = copy.deepcopy((inv, idx, style))
                mutate()
                self.assertEqual(self.result(), "fail")

    def test_unlisted_disk_export(self):
        (self.rd / "inputs/defender-export-folder/extra.csv").write_text("extra")
        self.assertEqual(self.result(), "fail")

    def test_logging_creates_directory(self):
        s5.append_guardrail_record("test", "G1", "pass", [])
        record = s5.ROOT / "audit/guardrails-test.jsonl"
        self.assertEqual(json.loads(record.read_text())["result"], "pass")

    def test_fallback_constraints(self):
        self.assertTrue(s5._mini_validate("bad", {"type": "string", "pattern": "^[0-9a-f]{64}$"}))
        self.assertTrue(s5._mini_validate(-1, {"type": "integer", "minimum": 0}))
        self.assertTrue(s5._mini_validate({}, {"type": "object", "properties": {
            "absent": {"type": "string", "minLength": 1}}}))
        for path in (PROJECT / "schemas").glob("*.json"):
            self.assertEqual(s5._schema_support_errors(json.loads(path.read_text(encoding="utf-8"))), [])


if __name__ == "__main__":
    unittest.main()
