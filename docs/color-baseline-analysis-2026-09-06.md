# Color baseline observations

Raw output: `color-baseline-2026-09-06.md`. No skill, schema or implementation was provided to the baseline agent.

Both scenarios correctly distinguished intent from verified input. DAY rejected treating a Log filename as camera metadata and refused approval without media/display review. INK kept ACEScg provisional, protected cyan eyes/silver-white hair, and refused unsupported HDR approval. Both offered useful matching/normalization, VFX and review actions; neither claimed actual image inspection or operations.

Observed gaps are structural: free-form Markdown rather than `color-plan.json`; no CL item identities; no registered metadata/inspection records with exact item/version/value binding; review and display states expressed as prose rather than machine constraints. Baseline already handles the evidence discipline, so the new skill should supply a concise reference/output contract and retain its useful creative reasoning, not add generic pressure warnings. Persuasion wording micro-tests are not applicable to this reference contract; independent application forwards remain required.

Ruling: use a dedicated color semantic module/test file and structured metadata/inspection/approval states, following accepted postproduction modules. This avoids further growth of the shared dispatcher. Cost if wrong: narrow interface adjustment at post-package integration.
