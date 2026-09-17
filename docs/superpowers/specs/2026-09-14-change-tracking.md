# Source Freshness Contract — Design Draft

Status: design only; no current CLI capability is implied.

## Boundary

Freshness is separate from schema/reference validation and creative approval. A valid plan can be stale, and fresh media can remain unapproved. Preserve legacy package inventories. Store the freshness sidecar outside the exact project root until an additive profile explicitly permits it.

## Snapshot

A snapshot records a contract version, project identity, source nodes and directed dependency edges. Each node has a unique stable key, a project-relative file path and optionally a JSON Pointer identifying a record. An edge A → B means B was authored using A. Reject unknown nodes, duplicate keys and cycles before comparison.

File nodes hash raw bytes using SHA-256. Therefore formatting-only changes conservatively mark dependents stale. Record nodes hash the enclosing raw file initially; this conservative rule is explicit and cannot support claims of record-local precision within the same file. A later canonical-record hashing mode requires its own versioned contract and tests.

Selective shot tracking initially requires separate shot source files. Do not claim record-level isolation when two shots share one file-level node.

## Operations

Capture is an explicit baseline-creation operation, never a side effect of validation. Compare is read-only: load the baseline, safely resolve nodes under the supplied project directory, measure current bytes, and compute the declared downstream closure. Neither operation approves content or regenerates artifacts.

Paths cannot escape the project root through traversal or symlinks. Unreadable files and malformed snapshots produce diagnostics, not guessed hashes. No model output is executed.

## States

- `fresh`: all required recorded inputs exist and match their baseline digests, with no changed or unknown ancestor.
- `stale`: a required input changed or a previously recorded input was deleted, directly or transitively.
- `unknown`: no baseline, unrecorded dependency or unreadable input prevents comparison.

If both stale and unknown evidence exists, report stale plus the unknown reasons. Freshness does not imply complete dependency discovery: the report lists its declared coverage and warns when a requested output lacks a baseline node.

Diagnostics and node lists are sorted. Repeated comparison of identical inputs returns the same semantic report; elapsed time and machine paths are not part of that report.

## Acceptance

1. Capture two independent shot source files and their dependent output nodes.
2. Change one camera file under the same shot ID; its downstream closure becomes stale, the second branch remains fresh.
3. Compare without altering any source, baseline or output bytes.
4. Delete a recorded source; its closure is stale with a missing-source reason.
5. Supply no baseline or an unreadable node; never return fresh for affected outputs.
6. Reject a dependency cycle and an escaping path deterministically.
7. A fresh result with no media inspection retains awaiting-media status; no approval field is synthesized.

## Implementation handoff

Before implementation, choose the exact serialized node/edge schema and public function signatures in a dedicated test-first plan. Candidate module: `src/cine_skills/project_freshness.py`; candidate tests: `tests/test_project_freshness.py`. Do not extend ProjectIndex with loosely defined state or replace the accepted validators as part of this work.
