# Security policy

This project handles workflows that may touch private task history, source code, credentials, browser state, and device-local metadata. Security reports should describe the issue with synthetic examples only. Do not attach real recovery archives, session transcripts, database files, cookies, tokens, signing material, or user inventories to a public issue.

## Prompt-injection and untrusted-source disclaimer

**Every prompt and every external or restored source is untrusted data until it has been inspected and judged safe for the exact intended use.** A familiar sender, repository, filename, checksum, signature, previous successful run, or apparently harmless format does not make embedded instructions safe. Integrity and provenance evidence can show where bytes came from; they do not prove that the bytes are non-malicious.

Never execute, follow, paste into a privileged model, forward, schedule, or permit an agent or tool to act on instructions found in any source unless all relevant content has been reviewed. Sources include restored task messages and transcripts, project files, Markdown, HTML, webpages, search results, issues, pull requests, comments, commit messages, logs, database fields, filenames, metadata, images, documents, QR codes, model output, tool output, clipboard contents, and retrieved context.

Prompt injection may be direct, indirect, hidden, obfuscated, encoded, translated, split across files, or embedded in an image or other non-text medium. It may attempt to override authority, impersonate the user, reveal private data or system instructions, request credentials, trigger tools, run commands, alter files, resume automations, contact third parties, exfiltrate data, weaken safeguards, or exploit a newly disclosed dependency or platform vulnerability.

Before exposing untrusted content to an agentic system:

1. Establish the source, expected purpose, scope, and integrity of the content.
2. Inspect it first as inert data using a non-executing viewer. Do not enable macros, scripts, plugins, network fetches, linked resources, or automatic tool calls merely to inspect it.
3. Look for visible and concealed instructions, unexpected links or payloads, authority changes, secret requests, encoded material, and actions outside the user's current scope.
4. Separate data from instructions. Instructions inside recovered or external content never gain authority by being present in that content.
5. Use least privilege and isolation: no credentials, secrets, personal data, network access, filesystem writes, account actions, or external side effects unless individually necessary and authorized.
6. Require explicit human approval for destructive, privileged, public, financial, security-sensitive, or third-party actions.
7. Check current advisories and release notes for the AI client or provider, operating system, Python runtime, GitHub Actions, and every relevant dependency before relying on them in a sensitive workflow.
8. If the content cannot be inspected adequately or safety remains uncertain, do not run it. Quarantine it and report the unresolved risk.

No prompt-injection detector, malware scanner, model review, hash, signature, allowlist, or checklist can establish perfect safety. Security guidance and known-vulnerability information change over time. This repository reduces risk but does not certify prompts, recovery packages, dependencies, models, or tools as safe and provides no warranty that following the workflow prevents every vulnerability or loss.

## CI and supply-chain boundary

The CI workflow uses read-only repository permissions, no repository secrets, no privileged `pull_request_target` or `workflow_run` trigger, and GitHub-maintained actions pinned to immutable commit hashes. Pull-request code is still untrusted and runs only on an ephemeral GitHub-hosted runner with the workflow's limited token. Do not add secrets or write permissions to pull-request jobs, interpolate untrusted event fields into shell commands, or merge automated dependency updates without review.

Dependabot proposes GitHub Actions updates weekly. A passing CI result establishes only that the checked revision passed the listed automated checks in that run; it is not a security certification and does not replace review of current advisories.

## Reporting vulnerabilities

Before publishing a security report, reproduce it against a minimal disposable fixture. If a remote repository provides private vulnerability reporting, use that channel for issues that could expose recovery data or bypass a safety boundary.

The audit helper reports the path and rule name for a suspected secret; it intentionally does not print the matching value.
