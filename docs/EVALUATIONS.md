# QACraft behavior evaluations

QACraft includes a local, deterministic evaluator for structured QA candidate reports. It does not call an AI model, browse the network, access customer systems, or infer missing evidence.

## Covered skills

- `/feature-qa`
- `/ticket-review`
- `/bug-report`
- `/verify-fix`
- `/release-qa`

The skill-specific rules are stored in `evaluations/rubrics.json` and are derived from each canonical skill's approval gates, ordered decision policy, result states, and output contract.

## Evaluation checks

Every candidate receives seven checks:

1. `schema_conformance` — required fields, types, identifiers, timestamps, hashes, and safe output paths.
2. `source_grounding` — observed claims require evidence; inferences and uncertainties must be labelled and explain their basis.
3. `approval_gates` — every required gate must be valid, version-bound, and tied to the candidate context hash.
4. `evidence_quality` — results and findings must reference existing, integrity-bound, privacy-reviewed evidence.
5. `verdict_discipline` — success outcomes cannot hide required non-pass results, open release blockers, missing accepted risk, or incomplete cleanup.
6. `safety_boundaries` — permissions must be verified; secrets and personal data must not be present; external writes require approval and idempotency.
7. `output_contract` — every skill-specific required output must be listed.

A candidate passes only when all seven checks pass. Failed evaluations return exit code `1`. Invalid input or a missing rubric returns exit code `2`.

## Candidate schema

The complete schema is `schemas/evaluation-candidate.schema.json`. A candidate includes:

- run identity and source references,
- a SHA-256 context hash,
- version-bound approval records,
- classified claims,
- privacy-reviewed evidence with integrity hashes,
- required and optional result records,
- findings and release-blocking state,
- a final decision and its evidence,
- safety declarations,
- the produced output list,
- cleanup status and residual resources.

A passing example is available at `evaluations/examples/feature-qa-pass.json`.

## Commands

List available rubrics:

```bash
python3 scripts/qacraft.py eval-list
```

Evaluate a candidate:

```bash
python3 scripts/qacraft.py evaluate \
  --input evaluations/examples/feature-qa-pass.json
```

Override the skill only when the caller intentionally wants to validate that the candidate matches a specific rubric:

```bash
python3 scripts/qacraft.py evaluate \
  --skill feature-qa \
  --input candidate.json
```

The report is emitted as JSON on standard output and follows `schemas/evaluation-report.schema.json`.

## Scope and limitations

The evaluator checks the internal consistency and policy conformance of supplied structured data. It does not prove that the evidence is genuine, that an external system behaved as claimed, or that runtime permissions were actually enforced. Those controls remain the responsibility of the execution environment, evidence store, and approval system.
