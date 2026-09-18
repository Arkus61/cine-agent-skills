# Technical QC

## Evidence classes

- **Measurement:** `supplied-measurement-report` records a value for an identified metric and master version. Preserve the report's units and source pointer.
- **Inspection:** `supplied-inspection-record` records an observable finding for an identified check and version. A path or filename without review findings is not inspection.
- **Deliverable verification:** `supplied-deliverable-record` verifies one identified deliverable against the current master.
- **Human approval:** `supplied-human-decision` covers the exact current version and review scope. The skill never creates this decision itself.

Every observation repeats the evidence's exact check, criterion, value, units, and version. Evidence for one check cannot be reassigned to another metric. The evidence source points to the report or decision record, never merely to the master filename; query strings, fragments, `./`, or path traversal segments do not turn the same master path into evidence. Every deliverable-verification record uses `deliverable:<known-id>`, `verified`, and null units. Every human-approval record uses a nonempty decision scope, `approved`, and null units. These internal rules also apply to historical and superseded records. `applicable` additionally means current and bound to the observation, deliverable, or approval; prior records may remain unbound only when marked `historical` or `superseded`.

## Review areas

Video geometry covers resolution, frame rate, aspect ratio, scan or cadence assumptions, duration, and framing. Frame integrity distinguishes missing and duplicate frames from intentional holds. Black-frame review distinguishes authored black, leader, or tail from unintended gaps. Artifact review includes compression damage, blocking, banding, ringing, frozen frames, flashes, contamination, and other visible defects without claiming an inspection that was not supplied.

Audio review keeps channel count and channel mapping/layout separate. Review sync against the identified version and stated tolerance. Sample peak, true peak, loudness, clipping, phase, dropouts, distortion, and intelligibility are different observations. EBU R 128 identifies programme loudness, loudness range, and maximum true peak as distinct descriptors; it does not supply a universal target for every project.

Caption and title checks distinguish file or stream presence from content accuracy, timing, relevant nonspeech information, speaker identification, readability, placement, and safe-area review. Metadata saying a caption track exists does not establish accessibility quality. Use exact title/caption item references when they are supplied.

VFX and color checks look for current-version completion, temporary elements, edge or grain integration, display-path consistency, shot matching, and unintended changes. These are review plans until the agent receives applicable inspection evidence.

## Result discipline

Use `pass` or `fail` only from applicable evidence for the current master and a `supplied` criterion. An `unresolved` criterion uses `review` and cannot pass or fail until the requirement is replaced by a concrete supplied value or qualitative criterion. Use `human-review` when a required qualitative decision is explicitly outstanding. Use `planned` when the master, requirement, or evidence is unavailable. Any required `planned`, `fail`, or `human-review` result blocks readiness.

Machine comparisons use typed operands. Frame rate and duration are finite values greater than zero; channel count is a positive integer; sample peak, true peak, and loudness are finite numbers, excluding booleans and numeric strings. Resolution, aspect ratio, and channel layout are non-empty strings. Supplied presence checks use `present` or `absent` with boolean values: `present` requires expected and observed `true`, while `absent` requires expected and observed `false`. A contradictory operator/value pair is invalid, and a pass/fail result that disagrees with the operator semantics is diagnosed. Unresolved presence requirements may remain `review`. A machine-comparable operator with incompatible operands is invalid rather than silently inconclusive; qualitative `review` criteria remain inspection decisions.
