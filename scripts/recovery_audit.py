#!/usr/bin/env python3
"""Deterministic, side-effect-bounded audits for Codex recovery packages."""

import argparse
import fnmatch
import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
from pathlib import Path, PurePosixPath


SCHEMA_VERSION = 1
DEFAULT_EXCLUDES = (
    ".git",
    ".git/**",
    "__pycache__",
    "**/__pycache__/**",
)
SENSITIVE_BASENAMES = {
    ".codex-global-state.json",
    ".env",
    "auth.json",
    "cookies",
    "cookies-journal",
    "credentials",
    "credentials.json",
    "id_ed25519",
    "id_rsa",
    "login data",
    "web data",
}
SENSITIVE_COMPONENTS = {".aws", ".gnupg", ".ssh", "keychains"}
SENSITIVE_EXTENSIONS = {".key", ".mobileprovision", ".p12", ".pfx"}
TEXT_SCAN_EXTENSIONS = {
    ".cfg",
    ".conf",
    ".env",
    ".ini",
    ".json",
    ".md",
    ".properties",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
}
MAX_TEXT_SCAN_BYTES = 2 * 1024 * 1024
CONTENT_RULES = (
    (
        "private-key-material",
        re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "credential-assignment",
        re.compile(
            rb"(?i)[\"']?(?:access_token|refresh_token|session_token|api_key|client_secret|password)[\"']?\s*[:=]\s*[\"'][^\"']{8,}[\"']"
        ),
    ),
    (
        "bearer-token",
        re.compile(rb"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{16,}"),
    ),
    (
        "provider-token-prefix",
        re.compile(
            rb"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{16,}|AKIA[0-9A-Z]{16})"
        ),
    ),
)


class AuditError(Exception):
    """Raised when an audit input violates a safety or format invariant."""


def json_print(value):
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


def inside(candidate, parent):
    try:
        candidate.relative_to(parent)
        return True
    except ValueError:
        return False


def relative_posix(root, path):
    return path.relative_to(root).as_posix()


def excluded(relative_path, patterns):
    pure = PurePosixPath(relative_path)
    return any(
        fnmatch.fnmatchcase(relative_path, pattern) or pure.match(pattern)
        for pattern in patterns
    )


def iter_entries(root, patterns):
    """Yield regular files and symlinks without following symlinked directories."""
    root = root.resolve()
    for current, directories, filenames in os.walk(str(root), followlinks=False):
        current_path = Path(current)
        directories.sort()
        filenames.sort()

        retained_directories = []
        symlink_directories = []
        for name in directories:
            path = current_path / name
            relative = relative_posix(root, path)
            if excluded(relative, patterns):
                continue
            if path.is_symlink():
                symlink_directories.append(path)
            else:
                retained_directories.append(name)
        directories[:] = retained_directories

        for path in symlink_directories:
            yield "symlink", path

        for name in filenames:
            path = current_path / name
            relative = relative_posix(root, path)
            if excluded(relative, patterns):
                continue
            if path.is_symlink():
                yield "symlink", path
            elif path.is_file():
                yield "file", path


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def sensitive_findings(root, patterns):
    findings = []
    root = root.resolve()
    for entry_type, path in iter_entries(root, patterns):
        relative = relative_posix(root, path)
        lower_parts = [part.lower() for part in PurePosixPath(relative).parts]
        basename = path.name.lower()

        if basename in SENSITIVE_BASENAMES:
            findings.append({"path": relative, "rule": "sensitive-filename"})
            continue
        if any(part in SENSITIVE_COMPONENTS for part in lower_parts):
            findings.append({"path": relative, "rule": "sensitive-directory"})
            continue
        if path.suffix.lower() in SENSITIVE_EXTENSIONS:
            findings.append({"path": relative, "rule": "sensitive-extension"})
            continue
        if entry_type == "symlink":
            continue
        if path.suffix.lower() not in TEXT_SCAN_EXTENSIONS:
            continue
        try:
            if path.stat().st_size > MAX_TEXT_SCAN_BYTES:
                continue
            content = path.read_bytes()
        except OSError:
            findings.append({"path": relative, "rule": "unreadable-sensitive-scan"})
            continue
        for rule_name, pattern in CONTENT_RULES:
            if pattern.search(content):
                findings.append({"path": relative, "rule": rule_name})
                break
    return findings


def manifest_records(root, patterns):
    root = root.resolve()
    records = []
    for entry_type, path in iter_entries(root, patterns):
        relative = relative_posix(root, path)
        if entry_type == "symlink":
            records.append(
                {
                    "path": relative,
                    "record_type": "symlink",
                    "target": os.readlink(str(path)),
                }
            )
        else:
            records.append(
                {
                    "path": relative,
                    "record_type": "file",
                    "sha256": sha256_file(path),
                    "size": path.stat().st_size,
                }
            )
    records.sort(key=lambda item: item["path"])
    return records


def write_manifest(root, output, patterns):
    root = root.resolve()
    output = output.resolve()
    if not root.is_dir():
        raise AuditError("root is not a directory: {}".format(root))
    if inside(output, root):
        raise AuditError("manifest output must be outside the tree being sealed")

    findings = sensitive_findings(root, patterns)
    if findings:
        raise AuditError(
            "sensitive-data scan found {} path(s); run scan-sensitive for rules".format(
                len(findings)
            )
        )

    records = manifest_records(root, patterns)
    output.parent.mkdir(parents=True, exist_ok=True)
    header = {
        "excludes": list(patterns),
        "record_type": "header",
        "schema_version": SCHEMA_VERSION,
    }
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=output.name + ".", suffix=".tmp", dir=str(output.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(header, ensure_ascii=False, sort_keys=True) + "\n")
            for record in records:
                handle.write(
                    json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
                )
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, str(output))
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise
    return {"files_and_symlinks": len(records), "manifest": str(output)}


def safe_manifest_relative(value):
    if not isinstance(value, str) or not value:
        raise AuditError("manifest path must be a non-empty string")
    pure = PurePosixPath(value)
    if (
        value in (".", "..")
        or pure.is_absolute()
        or any(part in ("", ".", "..") for part in pure.parts)
    ):
        raise AuditError("unsafe manifest path: {}".format(value))
    return pure


def load_manifest(path):
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise AuditError("manifest could not be read: {}".format(exc))
    if not lines:
        raise AuditError("manifest is empty")
    try:
        header = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise AuditError("manifest header is invalid JSON: {}".format(exc))
    if (
        not isinstance(header, dict)
        or header.get("record_type") != "header"
        or header.get("schema_version") != SCHEMA_VERSION
    ):
        raise AuditError("manifest header or schema version is unsupported")
    patterns = header.get("excludes", [])
    if not isinstance(patterns, list) or not all(isinstance(item, str) for item in patterns):
        raise AuditError("manifest excludes must be an array of strings")

    records = []
    seen = set()
    for line_number, line in enumerate(lines[1:], start=2):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AuditError(
                "manifest line {} is invalid JSON: {}".format(line_number, exc)
            )
        if not isinstance(record, dict):
            raise AuditError("manifest line {} is not an object".format(line_number))
        relative = safe_manifest_relative(record.get("path"))
        relative_text = relative.as_posix()
        if relative_text in seen:
            raise AuditError("duplicate manifest path: {}".format(relative_text))
        seen.add(relative_text)
        if record.get("record_type") not in ("file", "symlink"):
            raise AuditError("unsupported record type for {}".format(relative_text))
        records.append(record)
    return patterns, records


def verify_manifest(root, manifest):
    root = root.resolve()
    if not root.is_dir():
        raise AuditError("root is not a directory: {}".format(root))
    patterns, records = load_manifest(manifest)
    expected = {record["path"]: record for record in records}
    observed = {
        relative_posix(root, path): (entry_type, path)
        for entry_type, path in iter_entries(root, patterns)
    }

    missing = sorted(set(expected) - set(observed))
    extra = sorted(set(observed) - set(expected))
    mismatches = []
    for relative in sorted(set(expected) & set(observed)):
        record = expected[relative]
        entry_type, path = observed[relative]
        if record["record_type"] != entry_type:
            mismatches.append({"path": relative, "reason": "type"})
            continue
        if entry_type == "symlink":
            if os.readlink(str(path)) != record.get("target"):
                mismatches.append({"path": relative, "reason": "symlink-target"})
            continue
        try:
            expected_size = int(record.get("size"))
        except (TypeError, ValueError):
            mismatches.append({"path": relative, "reason": "invalid-size"})
            continue
        if path.stat().st_size != expected_size:
            mismatches.append({"path": relative, "reason": "size"})
            continue
        if sha256_file(path) != record.get("sha256"):
            mismatches.append({"path": relative, "reason": "sha256"})

    return {
        "extra": extra,
        "manifest_records": len(records),
        "mismatches": mismatches,
        "missing": missing,
        "ok": not missing and not extra and not mismatches,
    }


def sqlite_report(path):
    path = path.resolve()
    if not path.is_file():
        raise AuditError("SQLite file is missing: {}".format(path))
    sidecars = [Path(str(path) + suffix) for suffix in ("-wal", "-shm")]
    before = {str(item): item.exists() for item in sidecars}
    uri = path.as_uri() + "?mode=ro&immutable=1"
    try:
        connection = sqlite3.connect(uri, uri=True)
        try:
            quick_check = [row[0] for row in connection.execute("PRAGMA quick_check")]
            foreign_key_violations = len(
                connection.execute("PRAGMA foreign_key_check").fetchall()
            )
            table_count = connection.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            ).fetchone()[0]
        finally:
            connection.close()
    except sqlite3.Error as exc:
        raise AuditError("SQLite check failed for {}: {}".format(path, exc))
    after = {str(item): item.exists() for item in sidecars}
    created_sidecars = [item for item in after if after[item] and not before[item]]
    wal_present = Path(str(path) + "-wal").exists()
    return {
        "created_sidecars": created_sidecars,
        "foreign_key_violations": foreign_key_violations,
        "ok": quick_check == ["ok"] and foreign_key_violations == 0 and not created_sidecars,
        "path": str(path),
        "quick_check": quick_check,
        "table_count": table_count,
        "wal_present": wal_present,
        "warning": (
            "A WAL sidecar exists; verify a consistent disposable backup to include WAL data."
            if wal_present
            else None
        ),
    }


def combined_excludes(values):
    return tuple(DEFAULT_EXCLUDES) + tuple(values or ())


def command_scan_sensitive(args):
    root = args.root.resolve()
    if not root.is_dir():
        raise AuditError("root is not a directory: {}".format(root))
    findings = sensitive_findings(root, combined_excludes(args.exclude))
    json_print({"findings": findings, "ok": not findings, "root": str(root)})
    return 0 if not findings else 1


def command_hash_tree(args):
    result = write_manifest(
        args.root, args.output, combined_excludes(args.exclude)
    )
    result["ok"] = True
    json_print(result)
    return 0


def command_verify_manifest(args):
    result = verify_manifest(args.root, args.manifest)
    json_print(result)
    return 0 if result["ok"] else 1


def command_check_sqlite(args):
    reports = [sqlite_report(path) for path in args.paths]
    result = {"databases": reports, "ok": all(report["ok"] for report in reports)}
    json_print(result)
    return 0 if result["ok"] else 1


def build_parser():
    parser = argparse.ArgumentParser(
        description="Audit staged Codex migration packages without external dependencies."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sensitive = subparsers.add_parser(
        "scan-sensitive", help="report likely secret-bearing paths without values"
    )
    sensitive.add_argument("root", type=Path)
    sensitive.add_argument("--exclude", action="append", default=[])
    sensitive.set_defaults(handler=command_scan_sensitive)

    hash_tree = subparsers.add_parser(
        "hash-tree", help="write a deterministic JSONL SHA-256 manifest"
    )
    hash_tree.add_argument("root", type=Path)
    hash_tree.add_argument("--output", required=True, type=Path)
    hash_tree.add_argument("--exclude", action="append", default=[])
    hash_tree.set_defaults(handler=command_hash_tree)

    verify = subparsers.add_parser(
        "verify-manifest", help="verify every manifest path and detect extras"
    )
    verify.add_argument("root", type=Path)
    verify.add_argument("--manifest", required=True, type=Path)
    verify.set_defaults(handler=command_verify_manifest)

    sqlite_parser = subparsers.add_parser(
        "check-sqlite", help="run immutable read-only SQLite integrity checks"
    )
    sqlite_parser.add_argument("paths", nargs="+", type=Path)
    sqlite_parser.set_defaults(handler=command_check_sqlite)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (AuditError, OSError) as exc:
        json_print({"error": str(exc), "ok": False})
        return 1


if __name__ == "__main__":
    sys.exit(main())
