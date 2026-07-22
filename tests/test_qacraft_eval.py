import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "qacraft.py"
RUBRICS = ROOT / "evaluations" / "rubrics.json"
sys.path.insert(0, str(ROOT / "scripts"))

from qacraft_eval import evaluate_candidate, evaluate_file, load_rubrics  # noqa: E402


SUCCESS_OUTCOMES = {
    "feature-qa": "PASS",
    "ticket-review": "READY",
    "bug-report": "CONFIRMED DEFECT",
    "verify-fix": "FIXED",
    "release-qa": "PASS",
}


def sha(character: str) -> str:
    return character * 64


def valid_candidate(skill: str, rubric: dict) -> dict:
    return {
        "schema_version": "1.0.0",
        "skill": skill,
        "run_id": f"{skill}-run-001",
        "generated_at": "2026-07-22T12:00:00Z",
        "source_references": ["ticket:QA-100", "commit:abc123"],
        "context_hash": sha("a"),
        "approvals": [
            {
                "id": f"approval-{index}",
                "gate": gate,
                "approver": "QA Lead",
                "role": "release-approver",
                "approved_at": "2026-07-22T10:00:00Z",
                "expires_at": "2026-07-23T10:00:00Z",
                "context_hash": sha("a"),
                "document_hash": sha("b"),
                "valid": True,
            }
            for index, gate in enumerate(rubric["required_gates"], 1)
        ],
        "claims": [
            {
                "id": "claim-1",
                "text": "The expected result was directly observed.",
                "classification": "observed",
                "evidence_ids": ["evidence-1"],
            }
        ],
        "evidence": [
            {
                "id": "evidence-1",
                "type": "trace",
                "source_reference": "ticket:QA-100",
                "captured_at": "2026-07-22T11:30:00Z",
                "integrity_hash": sha("c"),
                "privacy_reviewed": True,
            }
        ],
        "results": [
            {
                "id": "result-1",
                "required": True,
                "status": "PASS",
                "expected": "The approved expected state is visible.",
                "actual": "The approved expected state was observed.",
                "evidence_ids": ["evidence-1"],
            }
        ],
        "findings": [],
        "decision": {
            "outcome": SUCCESS_OUTCOMES[skill],
            "reason": "The evidence supports the selected outcome.",
            "evidence_ids": ["evidence-1"],
        },
        "safety": {
            "permission_scope_verified": True,
            "secrets_in_output": False,
            "personal_data_in_output": False,
            "external_writes": [],
            "accepted_risks": [],
            "assumptions": [],
            "uncertainties": [],
        },
        "outputs": list(rubric["required_outputs"]),
        "cleanup": {
            "status": "complete",
            "residual_resources": [],
        },
    }


class QACraftEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rubrics = load_rubrics(RUBRICS)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def test_rubric_catalog_covers_priority_skills(self):
        self.assertEqual(
            set(self.rubrics),
            {
                "feature-qa",
                "ticket-review",
                "bug-report",
                "verify-fix",
                "release-qa",
            },
        )

    def test_valid_candidates_pass_every_rubric(self):
        for skill, rubric in self.rubrics.items():
            with self.subTest(skill=skill):
                report = evaluate_candidate(valid_candidate(skill, rubric), rubric, skill)
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["score"], report["max_score"])
                self.assertEqual(report["summary"]["failed_checks"], [])

    def test_hallucination_control_requires_evidence_for_observed_claims(self):
        rubric = self.rubrics["feature-qa"]
        candidate = valid_candidate("feature-qa", rubric)
        candidate["claims"][0]["evidence_ids"] = []
        report = evaluate_candidate(candidate, rubric, "feature-qa")
        self.assertFalse(report["passed"])
        self.assertIn("source_grounding", report["summary"]["failed_checks"])

    def test_approval_gate_check_detects_missing_gate(self):
        rubric = self.rubrics["release-qa"]
        candidate = valid_candidate("release-qa", rubric)
        candidate["approvals"].pop()
        report = evaluate_candidate(candidate, rubric, "release-qa")
        self.assertIn("approval_gates", report["summary"]["failed_checks"])

    def test_evidence_check_detects_unproven_result(self):
        rubric = self.rubrics["verify-fix"]
        candidate = valid_candidate("verify-fix", rubric)
        candidate["results"][0]["evidence_ids"] = []
        report = evaluate_candidate(candidate, rubric, "verify-fix")
        self.assertIn("evidence_quality", report["summary"]["failed_checks"])

    def test_verdict_check_rejects_pass_with_required_failure(self):
        rubric = self.rubrics["feature-qa"]
        candidate = valid_candidate("feature-qa", rubric)
        candidate["results"][0]["status"] = "FAIL"
        report = evaluate_candidate(candidate, rubric, "feature-qa")
        self.assertIn("verdict_discipline", report["summary"]["failed_checks"])

    def test_verdict_check_requires_recorded_conditional_risk(self):
        rubric = self.rubrics["release-qa"]
        candidate = valid_candidate("release-qa", rubric)
        candidate["decision"]["outcome"] = "CONDITIONAL PASS"
        report = evaluate_candidate(candidate, rubric, "release-qa")
        self.assertIn("verdict_discipline", report["summary"]["failed_checks"])

        candidate["safety"]["accepted_risks"] = [
            "Risk QA-200 approved until 2026-07-30."
        ]
        report = evaluate_candidate(candidate, rubric, "release-qa")
        self.assertTrue(report["passed"], report)

    def test_safety_check_rejects_unapproved_external_write(self):
        rubric = self.rubrics["bug-report"]
        candidate = valid_candidate("bug-report", rubric)
        candidate["safety"]["external_writes"] = [
            {
                "system": "issue-tracker",
                "approved": False,
                "idempotency_key": "",
            }
        ]
        report = evaluate_candidate(candidate, rubric, "bug-report")
        self.assertIn("safety_boundaries", report["summary"]["failed_checks"])

    def test_output_contract_detects_missing_required_output(self):
        rubric = self.rubrics["ticket-review"]
        candidate = valid_candidate("ticket-review", rubric)
        candidate["outputs"].pop()
        report = evaluate_candidate(candidate, rubric, "ticket-review")
        self.assertIn("output_contract", report["summary"]["failed_checks"])

    def test_schema_check_rejects_unsafe_output_path(self):
        rubric = self.rubrics["feature-qa"]
        candidate = valid_candidate("feature-qa", rubric)
        candidate["outputs"].append("../outside.txt")
        report = evaluate_candidate(candidate, rubric, "feature-qa")
        self.assertIn("schema_conformance", report["summary"]["failed_checks"])
        self.assertEqual(report["score"], 0)

    def test_evaluate_file_and_cli_return_machine_readable_report(self):
        rubric = self.rubrics["feature-qa"]
        candidate = valid_candidate("feature-qa", rubric)
        with tempfile.TemporaryDirectory() as directory:
            candidate_path = Path(directory) / "candidate.json"
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")

            direct = evaluate_file(candidate_path, RUBRICS)
            self.assertTrue(direct["passed"])

            result = self.run_cli("evaluate", "--input", str(candidate_path))
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["passed"])
            self.assertEqual(report["skill"], "feature-qa")

    def test_cli_returns_one_for_failed_evaluation(self):
        rubric = self.rubrics["feature-qa"]
        candidate = valid_candidate("feature-qa", rubric)
        candidate["results"][0]["status"] = "BLOCKED"
        with tempfile.TemporaryDirectory() as directory:
            candidate_path = Path(directory) / "candidate.json"
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
            result = self.run_cli("evaluate", "--input", str(candidate_path))
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)["passed"])

    def test_cli_lists_all_evaluation_rubrics(self):
        result = self.run_cli("eval-list")
        self.assertEqual(result.returncode, 0, result.stderr)
        for skill in self.rubrics:
            self.assertIn(f"/{skill}", result.stdout)


if __name__ == "__main__":
    unittest.main()
