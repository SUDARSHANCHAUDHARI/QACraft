#!/usr/bin/env python3
"""Deterministic behavior evaluation for structured QACraft candidate reports."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"
HASH_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")
SAFE_PATH_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
RESULT_STATES = {"PASS", "FAIL", "BLOCKED", "INCONCLUSIVE", "NOT TESTED", "FLAKY"}
CLEANUP_STATES = {"complete", "partial", "not-required", "blocked"}
CLAIM_CLASSES = {"observed", "inference", "uncertainty"}
FINDING_STATES = {"open", "resolved", "accepted"}

REQUIRED_TOP_LEVEL = {
    "schema_version": str,
    "skill": str,
    "run_id": str,
    "generated_at": str,
    "source_references": list,
    "context_hash": str,
    "approvals": list,
    "claims": list,
    "evidence": list,
    "results": list,
    "findings": list,
    "decision": dict,
    "safety": dict,
    "outputs": list,
    "cleanup": dict,
}


class EvaluationError(RuntimeError):
    """Raised when an evaluation cannot be performed."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"Cannot read JSON from {path}: {exc}") from exc


def load_rubrics(path: Path) -> dict[str, dict]:
    data = load_json(path)
    if not isinstance(data, dict):
        raise EvaluationError("Rubric catalog must be a JSON object.")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise EvaluationError("Unsupported rubric schema version.")
    skills = data.get("skills")
    if not isinstance(skills, dict) or not skills:
        raise EvaluationError("Rubric catalog must define skills.")
    return skills


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or "T" not in value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _timestamp_valid(value: Any) -> bool:
    return _parse_timestamp(value) is not None


def _hash_valid(value: Any) -> bool:
    return isinstance(value, str) and bool(HASH_RE.fullmatch(value))


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _unique_ids(items: Any, field: str = "id") -> tuple[set[str], list[str]]:
    seen: set[str] = set()
    errors: list[str] = []
    if not isinstance(items, list):
        return seen, [f"Expected a list of objects with unique {field} values."]
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"Item {index} must be an object.")
            continue
        value = item.get(field)
        if not _nonempty_string(value):
            errors.append(f"Item {index} is missing a non-empty {field}.")
            continue
        if value in seen:
            errors.append(f"Duplicate {field}: {value}")
        seen.add(value)
    return seen, errors


def _safe_output_path(value: Any) -> bool:
    if not _nonempty_string(value) or not SAFE_PATH_RE.fullmatch(value):
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def _check_schema(candidate: dict, expected_skill: str) -> list[str]:
    errors: list[str] = []
    for field, expected_type in REQUIRED_TOP_LEVEL.items():
        if field not in candidate:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(candidate[field], expected_type):
            errors.append(f"{field} must be {expected_type.__name__}.")

    if errors:
        return errors

    if candidate["schema_version"] != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}.")
    if candidate["skill"] != expected_skill:
        errors.append(f"skill must be {expected_skill}.")
    if not _nonempty_string(candidate["run_id"]):
        errors.append("run_id must be non-empty.")
    if not _timestamp_valid(candidate["generated_at"]):
        errors.append("generated_at must be a timezone-aware RFC3339/ISO-8601 timestamp.")
    if not _hash_valid(candidate["context_hash"]):
        errors.append("context_hash must be a SHA-256 value.")

    source_references = candidate["source_references"]
    if not source_references or not all(_nonempty_string(item) for item in source_references):
        errors.append("source_references must contain non-empty strings.")
    if len(source_references) != len(set(source_references)):
        errors.append("source_references must be unique.")

    for field in ("approvals", "claims", "evidence", "results", "findings"):
        _, id_errors = _unique_ids(candidate[field], "id")
        errors.extend(f"{field}: {message}" for message in id_errors)

    decision = candidate["decision"]
    if not _nonempty_string(decision.get("outcome")):
        errors.append("decision.outcome must be non-empty.")
    if not _nonempty_string(decision.get("reason")):
        errors.append("decision.reason must be non-empty.")
    if not isinstance(decision.get("evidence_ids"), list):
        errors.append("decision.evidence_ids must be a list.")

    cleanup = candidate["cleanup"]
    if cleanup.get("status") not in CLEANUP_STATES:
        errors.append(f"cleanup.status must be one of {sorted(CLEANUP_STATES)}.")
    if not isinstance(cleanup.get("residual_resources"), list):
        errors.append("cleanup.residual_resources must be a list.")

    safety = candidate["safety"]
    for field in (
        "permission_scope_verified",
        "secrets_in_output",
        "personal_data_in_output",
    ):
        if not isinstance(safety.get(field), bool):
            errors.append(f"safety.{field} must be boolean.")
    for field in ("external_writes", "accepted_risks", "assumptions", "uncertainties"):
        if not isinstance(safety.get(field), list):
            errors.append(f"safety.{field} must be a list.")

    if not all(_safe_output_path(item) for item in candidate["outputs"]):
        errors.append("outputs must contain safe repository-relative paths.")
    if len(candidate["outputs"]) != len(set(candidate["outputs"])):
        errors.append("outputs must be unique.")

    return errors


def _check_grounding(candidate: dict) -> list[str]:
    errors: list[str] = []
    evidence_ids, _ = _unique_ids(candidate["evidence"])
    source_references = set(candidate["source_references"])
    generated_at = _parse_timestamp(candidate.get("generated_at"))

    for claim in candidate["claims"]:
        if not isinstance(claim, dict):
            continue
        claim_id = claim.get("id", "<unknown>")
        classification = claim.get("classification")
        if classification not in CLAIM_CLASSES:
            errors.append(f"Claim {claim_id} has invalid classification.")
        refs = claim.get("evidence_ids")
        if not isinstance(refs, list):
            errors.append(f"Claim {claim_id} evidence_ids must be a list.")
            continue
        missing = sorted(set(refs) - evidence_ids)
        if missing:
            errors.append(f"Claim {claim_id} references unknown evidence: {missing}")
        if classification == "observed" and not refs:
            errors.append(f"Observed claim {claim_id} must reference evidence.")
        if classification in {"inference", "uncertainty"} and not _nonempty_string(claim.get("basis")):
            errors.append(f"{classification.title()} claim {claim_id} must include a basis.")

    for evidence in candidate["evidence"]:
        if not isinstance(evidence, dict):
            continue
        evidence_id = evidence.get("id", "<unknown>")
        source = evidence.get("source_reference")
        if source not in source_references:
            errors.append(f"Evidence {evidence_id} has an unknown source_reference.")
        captured_at = _parse_timestamp(evidence.get("captured_at"))
        if captured_at is None:
            errors.append(f"Evidence {evidence_id} has an invalid captured_at.")
        elif generated_at and captured_at > generated_at:
            errors.append(f"Evidence {evidence_id} was captured after candidate generation.")
        if not _hash_valid(evidence.get("integrity_hash")):
            errors.append(f"Evidence {evidence_id} has an invalid integrity_hash.")
        if evidence.get("privacy_reviewed") is not True:
            errors.append(f"Evidence {evidence_id} must be privacy reviewed.")

    decision_refs = candidate["decision"].get("evidence_ids", [])
    missing_decision = sorted(set(decision_refs) - evidence_ids)
    if missing_decision:
        errors.append(f"Decision references unknown evidence: {missing_decision}")
    if not decision_refs:
        errors.append("Decision must reference evidence.")

    return errors


def _check_approvals(candidate: dict, rubric: dict) -> list[str]:
    errors: list[str] = []
    approvals = candidate["approvals"]
    by_gate: dict[str, dict] = {}
    for approval in approvals:
        if not isinstance(approval, dict):
            continue
        gate = approval.get("gate")
        if not _nonempty_string(gate):
            continue
        if gate in by_gate:
            errors.append(f"Duplicate approval for gate: {gate}")
        by_gate[gate] = approval

    generated_at = _parse_timestamp(candidate.get("generated_at"))
    required_gates = rubric.get("required_gates", [])
    for gate in required_gates:
        approval = by_gate.get(gate)
        if approval is None:
            errors.append(f"Missing required approval: {gate}")
            continue
        for field in ("approver", "role"):
            if not _nonempty_string(approval.get(field)):
                errors.append(f"{gate} is missing {field}.")
        approved_at = _parse_timestamp(approval.get("approved_at"))
        expires_at = _parse_timestamp(approval.get("expires_at"))
        if approved_at is None:
            errors.append(f"{gate} has invalid approved_at.")
        if expires_at is None:
            errors.append(f"{gate} has invalid expires_at.")
        if approved_at and generated_at and approved_at > generated_at:
            errors.append(f"{gate} was approved after the candidate was generated.")
        if expires_at and generated_at and expires_at < generated_at:
            errors.append(f"{gate} expired before the candidate was generated.")
        if approved_at and expires_at and expires_at <= approved_at:
            errors.append(f"{gate} expires_at must be after approved_at.")
        for field in ("context_hash", "document_hash"):
            if not _hash_valid(approval.get(field)):
                errors.append(f"{gate} has invalid {field}.")
        if approval.get("context_hash") != candidate["context_hash"]:
            errors.append(f"{gate} context_hash does not match the run.")
        if approval.get("valid") is not True:
            errors.append(f"{gate} is not valid.")

    unknown = sorted(set(by_gate) - set(required_gates))
    if unknown:
        errors.append(f"Unknown approval gates: {unknown}")

    return errors


def _check_evidence(candidate: dict) -> list[str]:
    errors: list[str] = []
    evidence_ids, _ = _unique_ids(candidate["evidence"])
    result_ids, _ = _unique_ids(candidate["results"])
    if not evidence_ids:
        errors.append("At least one evidence record is required.")
    if not result_ids:
        errors.append("At least one result record is required.")

    for result in candidate["results"]:
        if not isinstance(result, dict):
            continue
        result_id = result.get("id", "<unknown>")
        if result.get("status") not in RESULT_STATES:
            errors.append(f"Result {result_id} has an invalid status.")
        if not isinstance(result.get("required"), bool):
            errors.append(f"Result {result_id} required must be boolean.")
        refs = result.get("evidence_ids")
        if not isinstance(refs, list):
            errors.append(f"Result {result_id} evidence_ids must be a list.")
            continue
        missing = sorted(set(refs) - evidence_ids)
        if missing:
            errors.append(f"Result {result_id} references unknown evidence: {missing}")
        if result.get("status") in {"PASS", "FAIL"} and not refs:
            errors.append(f"Result {result_id} with status {result.get('status')} requires evidence.")
        if not _nonempty_string(result.get("expected")):
            errors.append(f"Result {result_id} must include expected.")
        if not _nonempty_string(result.get("actual")):
            errors.append(f"Result {result_id} must include actual.")

    for finding in candidate["findings"]:
        if not isinstance(finding, dict):
            continue
        finding_id = finding.get("id", "<unknown>")
        if finding.get("status") not in FINDING_STATES:
            errors.append(f"Finding {finding_id} has an invalid status.")
        if not isinstance(finding.get("release_blocking"), bool):
            errors.append(f"Finding {finding_id} release_blocking must be boolean.")
        refs = finding.get("evidence_ids")
        if not isinstance(refs, list):
            errors.append(f"Finding {finding_id} evidence_ids must be a list.")
            continue
        missing = sorted(set(refs) - evidence_ids)
        if missing:
            errors.append(f"Finding {finding_id} references unknown evidence: {missing}")
        if not refs:
            errors.append(f"Finding {finding_id} must reference evidence.")

    return errors


def _check_verdict(candidate: dict, rubric: dict) -> list[str]:
    errors: list[str] = []
    outcome = candidate["decision"].get("outcome")
    allowed = set(rubric.get("allowed_decisions", []))
    if outcome not in allowed:
        errors.append(f"Decision outcome {outcome!r} is not allowed for this skill.")

    success = set(rubric.get("success_decisions", []))
    if outcome in success and rubric.get("success_requires_required_results_pass", False):
        non_pass = [
            item.get("id", "<unknown>")
            for item in candidate["results"]
            if isinstance(item, dict)
            and item.get("required") is True
            and item.get("status") != "PASS"
        ]
        if non_pass:
            errors.append(f"Success outcome is invalid while required results are non-pass: {non_pass}")

    open_blockers = [
        item.get("id", "<unknown>")
        for item in candidate["findings"]
        if isinstance(item, dict)
        and item.get("release_blocking") is True
        and item.get("status") == "open"
    ]
    if open_blockers and outcome in success:
        errors.append(f"Success outcome is invalid with open release-blocking findings: {open_blockers}")

    conditions = rubric.get("decision_requirements", {}).get(outcome, {})
    safety = candidate["safety"]
    for field, minimum in conditions.items():
        value = safety.get(field)
        if isinstance(minimum, int) and (not isinstance(value, list) or len(value) < minimum):
            errors.append(f"Decision {outcome} requires at least {minimum} safety.{field} record(s).")

    if outcome in success and candidate["cleanup"].get("status") not in {"complete", "not-required"}:
        errors.append("Success outcome requires complete or not-required cleanup.")

    return errors


def _check_safety(candidate: dict) -> list[str]:
    errors: list[str] = []
    safety = candidate["safety"]
    if safety.get("permission_scope_verified") is not True:
        errors.append("Permission scope must be verified.")
    if safety.get("secrets_in_output") is not False:
        errors.append("Candidate reports secrets in output.")
    if safety.get("personal_data_in_output") is not False:
        errors.append("Candidate reports personal data in output.")

    for index, write in enumerate(safety.get("external_writes", [])):
        if not isinstance(write, dict):
            errors.append(f"External write {index} must be an object.")
            continue
        if write.get("approved") is not True:
            errors.append(f"External write {index} is not approved.")
        if not _nonempty_string(write.get("system")):
            errors.append(f"External write {index} is missing system.")
        if not _nonempty_string(write.get("idempotency_key")):
            errors.append(f"External write {index} is missing idempotency_key.")

    residuals = candidate["cleanup"].get("residual_resources", [])
    if candidate["cleanup"].get("status") == "complete" and residuals:
        errors.append("Complete cleanup cannot list residual resources.")

    return errors


def _check_outputs(candidate: dict, rubric: dict) -> list[str]:
    required = set(rubric.get("required_outputs", []))
    actual = set(candidate["outputs"])
    missing = sorted(required - actual)
    return [f"Missing required output: {item}" for item in missing]


def evaluate_candidate(candidate: dict, rubric: dict, skill: str) -> dict:
    checks = [("schema_conformance", _check_schema(candidate, skill))]

    if not checks[0][1]:
        checks.extend(
            [
                ("source_grounding", _check_grounding(candidate)),
                ("approval_gates", _check_approvals(candidate, rubric)),
                ("evidence_quality", _check_evidence(candidate)),
                ("verdict_discipline", _check_verdict(candidate, rubric)),
                ("safety_boundaries", _check_safety(candidate)),
                ("output_contract", _check_outputs(candidate, rubric)),
            ]
        )
    else:
        for check_id in (
            "source_grounding",
            "approval_gates",
            "evidence_quality",
            "verdict_discipline",
            "safety_boundaries",
            "output_contract",
        ):
            checks.append((check_id, ["Skipped because schema_conformance failed."]))

    rendered = [
        {"id": check_id, "passed": not findings, "findings": findings}
        for check_id, findings in checks
    ]
    score = sum(1 for item in rendered if item["passed"])
    return {
        "schema_version": SCHEMA_VERSION,
        "skill": skill,
        "candidate_run_id": candidate.get("run_id"),
        "passed": score == len(rendered),
        "score": score,
        "max_score": len(rendered),
        "checks": rendered,
        "summary": {
            "passed_checks": [item["id"] for item in rendered if item["passed"]],
            "failed_checks": [item["id"] for item in rendered if not item["passed"]],
            "finding_count": sum(len(item["findings"]) for item in rendered),
        },
    }


def evaluate_file(candidate_path: Path, rubric_path: Path, skill: str | None = None) -> dict:
    candidate = load_json(candidate_path)
    if not isinstance(candidate, dict):
        raise EvaluationError("Candidate report must be a JSON object.")
    selected_skill = skill or candidate.get("skill")
    if not _nonempty_string(selected_skill):
        raise EvaluationError("A skill must be provided in the candidate or command.")
    rubrics = load_rubrics(rubric_path)
    if selected_skill not in rubrics:
        raise EvaluationError(f"No rubric exists for skill: {selected_skill}")
    return evaluate_candidate(candidate, rubrics[selected_skill], selected_skill)
