# Recovery evidence model

Use this reference when writing checkpoints, manifests, receipts, or final reports.

## Status vocabulary

- `VERIFIED`: the named artifact or behavior passed a current destination-side check.
- `PRESERVED`: recoverable bytes or references exist, but the associated behavior was not run.
- `BLOCKED`: an attempted required check could not complete; include the concrete cause and retained evidence.
- `EXCLUDED`: deliberately omitted by scope, security, portability, or product boundary.
- `UNKNOWN`: not checked or not observable; never convert this to success.
- `PENDING_USER`: completion requires a specific user action, confirmation, login, physical device, or authority.

Avoid using `complete` without naming the layer that is complete.

## Independent gates

Track these separately when they apply:

| Gate | Minimum evidence |
| --- | --- |
| Source capture | Source inventory, component cutoff, byte copy, and failures |
| Local package integrity | Manifest verification and archive/database checks |
| Cloud receipt | Authoritative sync or remote readback, not folder placement |
| Destination download | Destination-side size/hash verification |
| Staged restoration | Verified staged structure and schema-compatible candidate |
| Application cutover | Offline install plus successful reopen |
| Runtime loading | Current task evidence that instructions/config were applied |
| Project readiness | Appropriate static/build/runtime checks for that project |
| Shared-writer cutover | Source quiescence evidence or explicit user confirmation |

## Required report fields

Include, as applicable:

- source and destination identifiers;
- actual local paths and client versions;
- recovery layers and application order;
- manifest counts and hash failures;
- session, task, project, section, turn, and item counts with timestamps;
- Git histories, dirty state, placeholders, and non-Git project coverage;
- credentials and other deliberate exclusions;
- configured, requested, and observed model settings separately;
- automation status;
- source and destination writer status;
- rollback locations;
- capture cutoffs and known missing later activity;
- exact remaining user action.

## Truthful count changes

Counts may grow during validation because the destination is active. Application startup may normalize empty projects, stale assignments, ordering, or caches. Record both the pre-launch candidate and the stable post-reopen readback, explain the difference from evidence, and use the stable live count in the final status.

Do not infer that a visible task contains its transcript, that a project association proves source files exist, or that a local build proves device, signing, provider, hosted, or release readiness.
