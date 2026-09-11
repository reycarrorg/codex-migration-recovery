# Migration and recovery runbook

Read this reference for an authorized capture, transfer, restore, or cutover. Adapt file locations and application-specific details to the current machines; the sequence describes evidence gates, not fixed product internals.

## 1. Define the recovery contract

Record:

- source and destination device identity;
- resolved home, Documents, cloud-storage, project, and Codex-state roots;
- source writer and required quiescence signal;
- current app/client versions and applicable instructions;
- baseline, additive delta, and final-checkpoint locations;
- component capture cutoffs;
- allowed local copies and external destinations;
- forbidden credentials, destructive actions, publication, billing, and automatic resumes;
- completion evidence and required user actions.

Do not treat file dates or old task instructions as current authority.

## 2. Inspect before capture

Inventory live source state and the sealed baseline without modifying either. Prefer existing manifests and exact changed or missing paths over repeated whole-tree scans.

Distinguish:

1. local Codex sessions and indexes;
2. account-side ChatGPT history;
3. application databases and desktop registries;
4. task artifacts, attachments, memories, and skills;
5. project files, Git object stores, worktrees, dirty files, and untracked files;
6. configuration safe to recreate;
7. credentials and machine secrets that must be reauthenticated instead of copied;
8. application binaries and runtime readiness.

Check free space and provider-placeholder state before bulk work.

## 3. Build a baseline or additive delta

Never rewrite a sealed baseline. Create a separately dated delta for anything newer, missing, or previously blocked.

- Copy; do not move or delete source state.
- Preserve relative paths, source provenance, timestamps where useful, and per-component cutoffs.
- Materialize cloud placeholders deliberately. A visible name or zero-byte link is not content.
- Record provider failures individually and stop retrying unchanged failures after a bounded attempt.
- Inspect Git common directories and worktree relationships before creating bundles.
- Capture dirty, staged, untracked, ignored-but-required, and unborn-repository state separately from commit history.
- Exclude authentication stores, cookies, tokens, keychains, signing identities, provisioning profiles, passwords, and unneeded device enrollment.
- Restoreable automations must be captured as definitions with their paused state, never as executable queues.

Run `scan-sensitive` before sealing. Write the hash manifest outside the package tree so the manifest does not modify or include itself.

## 4. Verify the package

Use the deterministic helper or equivalent checks:

- verify every manifest path, size, and SHA-256;
- reject traversal and duplicate manifest paths;
- record symlinks without following them;
- test archive entry paths before extraction;
- check SQLite only on a consistent disposable copy or through an immutable read-only URI;
- record `quick_check`, foreign-key violations, schema/version notes, and any absent WAL-dependent data;
- compare expected and observed counts without converting old counts into current expectations.

Keep `local_integrity_verified`, `cloud_upload_verified`, `destination_download_verified`, and `destination_restore_verified` separate.

## 5. Prepare the destination

Inspect and back up the destination first. Preserve new destination tasks, settings, projects, and files.

Restore baseline to staging, then apply deltas in chronological order, then apply any explicitly designated final checkpoints. Verify after each layer. Remap absolute paths and project roots only where runtime references require it; do not rewrite historical provenance.

Prefer supported import, task, project, and sidebar APIs. Do not assume a feature that imports another product also supports local Codex databases.

For schema-bound data:

- inspect both exact schemas and client versions;
- use explicit columns rather than `SELECT *`;
- test on disposable copies;
- preserve destination-only rows and settings;
- validate counts, constraints, foreign keys, and representative content;
- avoid importing goals, queues, logs, or executable state unless separately authorized;
- never copy a source global-state file wholesale.

## 6. Perform a guarded offline cutover

When a live-state replacement is required:

1. Finish and verify the staged candidate.
2. Write a self-contained checkpoint and exact command before the app is closed.
3. Require a complete app and app-server quit.
4. Recheck process absence in the cutover script.
5. Preflight every external dependency in the user's actual Terminal environment; prefer absolute system paths or standard-library helpers for critical logic.
6. Take a fresh, consistent destination backup.
7. Install through a same-filesystem staged file and atomic rename.
8. Move or quarantine old database sidecars with the backup before replacing a database.
9. Restore only explicitly paused automation definitions.
10. Reopen once and validate through supported application readback.

If a preflight fails before writes, report that no rollback is needed. If a later step fails, identify the exact mutation boundary and rollback artifact before retrying.

## 7. Validate after reopening

Check independent evidence layers:

- database integrity and live counts;
- session-file presence;
- representative original task histories;
- project cards, roots, assignments, ordering, pins, and sidebar sections;
- unavailable-host or unavailable-source indicators;
- automation pause state;
- configured versus observed model and reasoning;
- actual instruction discovery and policy loading;
- representative project and exported-document readability.

Application normalization may legitimately remove an empty wrapper or rewrite ordering. Compare pre-cutover and post-reopen state before calling that data loss. Record any persistent difference truthfully.

## 8. Close or hand off

Use the checkpoint and final-handoff templates. Report restored, preserved-as-reference, blocked, excluded, and unknown material separately. Retain source devices until destination validation and any shared-writer handoff are complete.

Restoration completion does not authorize backlog execution, source erasure, shared-record writes, software installation, release, publication, or purchased-resource use.
