# Mastering/QC forward — partial r2 metadata

Validated against the frozen Task 7 contract after commit `36d0306`.

```text
PYTHONPATH=src .venv/bin/python -m cine_skills validate-artifact mastering-qc-plan docs/mastering-forward-partial-r2-metadata.json --root . --format json
{"command": "validate-artifact", "errors": [], "valid": true}
```

The plan records six supplied r2 evidence records and passes only four exact metadata checks: video resolution, frame rate, duration, and audio channel count. The remaining 20 required checks remain `planned`; the r2 picture-sound master is only `present`, the captions and QC-report deliverables remain `planned`, approval is `pending`, and readiness is `not-ready`. Historical r1 approval is retained but not transferred to r2. No media measurement, inspection, or approval is invented.
