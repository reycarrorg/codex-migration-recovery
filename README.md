# Codex Migration Recovery

## Moved to the skills collection

**The maintained package now lives in [reycarrorg/skills](https://github.com/reycarrorg/skills/tree/main/skills/codex-migration-recovery).**

Canonical folder: `skills/codex-migration-recovery`. Use the collection for installation and future updates. This standalone repository remains available for original source history, provenance, and earlier CI evidence; it is no longer the primary distribution.

The complete audit helper, skill instructions, references, templates, tests, license, and attribution were already carried into the collection. No personal recovery packages or credentials are included. Consolidation does not start a migration, modify live Codex state, or resume restored work.

## Install with Codex's built-in skill installer

```sh
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo reycarrorg/skills \
  --path skills/codex-migration-recovery \
  --name codex-migration-recovery
```

Do not overwrite an existing destination. Helper location and skill discovery vary by Codex version; follow the [maintained installation guide](https://github.com/reycarrorg/skills/blob/main/docs/INSTALL.md).

## Install manually with Git

Clone the collection into a separate folder, record `git rev-parse HEAD`, and copy its complete `skills/codex-migration-recovery` directory into your agent's documented skills location. Do not install the collection repository root as a single skill. The installation guide covers optional local links and `pull --ff-only` / fast-forward-only updates while preserving local changes.

## Prompt an agent to install it

```text
Install skills/codex-migration-recovery from reycarrorg/skills.
Preserve any existing installation and local changes, run the collection
validator and recovery-helper tests, and report the source commit and installed path.
Do not run a migration, restore live state, or resume automations during installation.
```

## Audit helper and earlier CI

The helper uses only Python's standard library. Its source is preserved in both the original history and the maintained collection.

```sh
python3 scripts/recovery_audit.py --help
python3 -m unittest discover -s tests -v
```

The standalone [CI workflow](.github/workflows/ci.yml) remains for this preserved source. The collection's [validation workflow](https://github.com/reycarrorg/skills/blob/main/.github/workflows/validate.yml) validates the maintained packages. Existing CI evidence describes the revision and environment actually tested, not a new live migration.

## Design and test provenance

Original authoring date: September 11, 2026. Codex Desktop `26.908.40401` (build `8837`); session-start CLI `0.154.0-alpha.6.1`, final bundled CLI readback `0.154.0-alpha.6.2`; recorded model request `gpt-5.6-sol`, reasoning `xhigh`. These are historical request records, not current model requirements or independent backend attestation.

The original [PROVENANCE.json](PROVENANCE.json) is unchanged. See the [maintained skill README](https://github.com/reycarrorg/skills/blob/main/skills/codex-migration-recovery/README.md) for the full reference table and current instructions.

## License

Copyright 2026 Rolando Carreon. [PolyForm Noncommercial 1.0.0](LICENSE.md) and the [required ownership notice](NOTICE) remain unchanged. The skill is source-available for uses allowed by those noncommercial terms; commercial use is not granted. It is not an OSI-approved open-source project.
