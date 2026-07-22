# QACraft behavior evaluations

QACraft includes a local, deterministic evaluator for structured QA candidate reports. It does not call an AI model, browse the network, access customer systems, or infer missing evidence.

## Covered skills

### Core release and defect workflows

- `/feature-qa`
- `/ticket-review`
- `/bug-report`
- `/verify-fix`
- `/release-qa`

### Phase 3.4 expansion

- `/test-plan`
- `/regression-scope`
- `/customer-issue-repro`
- `/api-qa`
- `/staged-rollout-check`

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

The candidate schema skill enumeration is kept equal to the rubric catalog.

## Published fixture catalog

`evaluations/fixtures.json` is the authoritative list of published examples and targeted failures.

The catalog records:

- fixture path,
- selected skill,
- whether the evaluation must pass,
- the policy check or checks a negative fixture must fail.

Passing examples are provided for the original `/feature-qa` rubric and all five Phase 3.4 skills. Targeted negative fixtures cover:

| Skill | Targeted failure |
|---|---|
| `/test-plan` | missing required output |
| `/regression-scope` | observed claim without evidence |
| `/customer-issue-repro` | missing required approval |
| `/api-qa` | secrets declared in output |
| `/staged-rollout-check` | `CONTINUE` with a required failed result |

`qacraft release-check` evaluates every catalog entry. It fails when a fixture is missing, produces the wrong pass/fail result, or does not trigger its declared failed check.

## Commands

List available rubrics:

```bash
qacraft eval-list
```

Evaluate a passing example:

```bash
qacraft evaluate \
  --input evaluations/examples/api-qa-pass.json
```

Evaluate a targeted failure fixture:

```bash
qacraft evaluate \
  --input evaluations/fixtures/api-qa-secret-output.json
```

The second command is expected to return exit code `1` and include `safety_boundaries` in the failed checks.

Override the skill only when the caller intentionally wants to validate that the candidate matches a specific rubric:

```bash
qacraft evaluate \
  --skill api-qa \
  --input candidate.json
```

The report is emitted as JSON on standard output and follows `schemas/evaluation-report.schema.json`.

## Rubric design rules

Every rubric must:

- copy approval-gate text exactly from the canonical `SKILL.md`,
- use only decisions present in the canonical result states or ordered decision policy,
- copy the output contract exactly,
- identify which outcomes are treated as successful by the generic evaluator,
- declare additional safety records required for conditional outcomes,
- remain deterministic and network-free.

Planning and scoping outcomes such as `APPROVED`, `TARGETED`, and `BROAD` are workflow decisions, not proof that the product passed execution. Customer reproduction outcomes such as `NOT REPRODUCED` are also not a dismissal of the report.

## Scope and limitations

The evaluator checks the internal consistency and policy conformance of supplied structured data. It does not prove that the evidence is genuine, that an external system behaved as claimed, or that runtime permissions were actually enforced. Those controls remain the responsibility of the execution environment, evidence store, and approval system.
