import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "recovery_audit", ROOT / "scripts" / "recovery_audit.py"
)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class RecoveryAuditTests(unittest.TestCase):
    def test_manifest_round_trip_and_change_detection(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            source.mkdir()
            (source / "nested").mkdir()
            (source / "alpha.txt").write_text("alpha\n", encoding="utf-8")
            (source / "nested" / "beta.bin").write_bytes(b"beta")
            manifest = base / "manifest.jsonl"

            result = AUDIT.write_manifest(
                source, manifest, AUDIT.DEFAULT_EXCLUDES
            )
            self.assertEqual(result["files_and_symlinks"], 2)
            verified = AUDIT.verify_manifest(source, manifest)
            self.assertTrue(verified["ok"])

            (source / "alpha.txt").write_text("changed\n", encoding="utf-8")
            changed = AUDIT.verify_manifest(source, manifest)
            self.assertFalse(changed["ok"])
            self.assertEqual(changed["mismatches"][0]["path"], "alpha.txt")

    def test_manifest_must_be_outside_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            source.mkdir()
            (source / "file.txt").write_text("safe", encoding="utf-8")
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.write_manifest(
                    source, source / "manifest.jsonl", AUDIT.DEFAULT_EXCLUDES
                )

    def test_sensitive_path_blocks_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            source.mkdir()
            (source / "auth.json").write_text("{}", encoding="utf-8")
            findings = AUDIT.sensitive_findings(
                source, AUDIT.DEFAULT_EXCLUDES
            )
            self.assertEqual(findings[0]["rule"], "sensitive-filename")
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.write_manifest(
                    source, base / "manifest.jsonl", AUDIT.DEFAULT_EXCLUDES
                )

    def test_sensitive_content_is_reported_without_value(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            source.mkdir()
            secret = "synthetic-secret-value"
            (source / "settings.json").write_text(
                json.dumps({"api_key": secret}), encoding="utf-8"
            )
            findings = AUDIT.sensitive_findings(
                source, AUDIT.DEFAULT_EXCLUDES
            )
            serialized = json.dumps(findings)
            self.assertEqual(findings[0]["rule"], "credential-assignment")
            self.assertNotIn(secret, serialized)

    def test_unsafe_manifest_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            source.mkdir()
            manifest = base / "manifest.jsonl"
            header = {
                "excludes": [],
                "record_type": "header",
                "schema_version": 1,
            }
            record = {
                "path": "../escape",
                "record_type": "file",
                "sha256": "0" * 64,
                "size": 0,
            }
            manifest.write_text(
                json.dumps(header) + "\n" + json.dumps(record) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.verify_manifest(source, manifest)

    def test_sqlite_check_does_not_create_sidecars(self):
        with tempfile.TemporaryDirectory() as temporary:
            database = Path(temporary) / "state.sqlite"
            connection = sqlite3.connect(str(database))
            connection.execute("CREATE TABLE example (id INTEGER PRIMARY KEY)")
            connection.execute("INSERT INTO example DEFAULT VALUES")
            connection.commit()
            connection.close()

            report = AUDIT.sqlite_report(database)
            self.assertTrue(report["ok"])
            self.assertEqual(report["quick_check"], ["ok"])
            self.assertEqual(report["foreign_key_violations"], 0)
            self.assertEqual(report["created_sidecars"], [])


if __name__ == "__main__":
    unittest.main()
