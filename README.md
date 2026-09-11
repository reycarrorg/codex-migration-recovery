# Codex Migration Recovery

A reusable Codex skill for evidence-backed migration of local Codex tasks, project files, sidebar organization, and recovery records between computers.

The repository packages the workflow—not anybody's recovery data. It deliberately contains no task transcripts, session databases, Drive inventories, authentication stores, device identifiers, private project IDs, absolute user paths, or one-machine cutover scripts.

> [!CAUTION]
> **Treat every prompt and every external or restored source as untrusted data.** Inspect content inertly before giving it to an AI model or tool. Never execute, follow, paste, forward, schedule, or let an agent act on instructions found in a task, transcript, file, webpage, issue, comment, log, image, metadata field, model output, or other source unless its provenance, purpose, and contents have been reviewed and it is safe for the exact intended use. Prompt injection can be direct, indirect, hidden, encoded, or multimodal. If safety is uncertain, do not run it. See [SECURITY.md](SECURITY.md).

## What it covers

- Immutable baseline plus dated additive deltas
- Sensitive-data exclusions
- Provider-placeholder and Git/worktree handling
- Portable SHA-256 manifests
- Sidecar-free SQLite verification
- Destination-first staging and rollback
- Guarded offline cutover and post-reopen readback
- Paused-automation restoration
- Explicit cloud, destination, runtime, and writer-status gates

It is not a ChatGPT account export, credential-transfer utility, universal SQLite importer, cloud-sync detector, or authorization to delete a source machine or resume recovered projects.

## Repository layout

```text
SKILL.md
agents/openai.yaml
scripts/recovery_audit.py
references/runbook.md
references/evidence-model.md
assets/templates/RESTORE_CHECKPOINT.md
assets/templates/FINAL_HANDOFF.md
tests/test_recovery_audit.py
LICENSE.md
NOTICE
.github/workflows/ci.yml
.github/dependabot.yml
```

## Use as a Codex skill

Install the repository folder as `codex-migration-recovery` under your Codex skills directory, then invoke it as `$codex-migration-recovery` or let Codex select it for an authorized local migration request.

The skill intentionally requires the agent to identify the actual source, destination, permissions, and client schemas at runtime. It does not embed a username or assume a fixed `~/.codex` database layout.

## Audit helper

The helper uses only Python's standard library:

```bash
python3 scripts/recovery_audit.py --help
python3 -m unittest discover -s tests -v
```

Hash manifests must be written outside the tree being sealed. The helper refuses to create a manifest when it finds high-confidence credential or signing-material paths.

## Continuous integration

Continuous integration (CI) means GitHub automatically checks each push and pull request. This repository's CI compiles the Python sources, runs the unit and repository-policy tests on Python 3.9, 3.12, and 3.14, scans for sensitive material, and verifies a fresh hash-manifest round trip.

The workflow has read-only repository permissions, does not receive project secrets, disables persisted checkout credentials, and pins GitHub-maintained actions to full commit hashes. Dependabot checks those action references weekly, but every proposed update still requires human review before merge.

## License

Copyright © 2026 Rolando Carreon. This repository is source-available under the [PolyForm Noncommercial License 1.0.0](LICENSE.md).

The license permits use, modification, and distribution for permitted noncommercial purposes. Commercial use is not granted; a separate written commercial license from the copyright holder is required for that use. Preserve the [required ownership notice](NOTICE) with redistributed copies.

Because it restricts commercial use, this is not an OSI-approved open-source license. Describe the repository as **source-available**, not open source.

## Publication boundary

Before publishing a fork, inspect the complete staged Git diff, run the sensitive-data scan, confirm the copyright notice and license, and create the remote with the intended visibility. Do not commit real recovery packages as examples or test fixtures.
