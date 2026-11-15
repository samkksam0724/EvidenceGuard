import unittest

from modules.reliability import assess_finding, assess_project, suggest_evidence

class TestReliability(unittest.TestCase):

    def test_supported(self):
        finding = {
            "field": "project_id",
            "check_type": "project_id_consistency",
            "result": "pass",
            "sources": [{"value": "MPL002", "normalized_value": "MPL002"}],
        }
        self.assertEqual(assess_finding(finding), "Supported")

    def test_conflicting(self):
        finding = {
            "field": "expenditure_amount",
            "check_type": "cross_document",
            "result": "conflict",
            "sources": [
                {"value": 1100000, "normalized_value": 1100000},
                {"value": "Rs. 11,50,000", "normalized_value": 1150000},
            ],
        }
        self.assertEqual(assess_finding(finding), "Conflicting")

    def test_insufficient_evidence(self):
        finding = {
            "field": "bill_number",
            "check_type": "missing_field",
            "result": "unable",
            "sources": [{"value": None, "normalized_value": None}],
        }
        self.assertEqual(assess_finding(finding), "Insufficient Evidence")

    def test_unreadable_value(self):
        finding = {
            "field": "expenditure_amount",
            "check_type": "cross_document",
            "result": "unable",
            "sources": [
                {"value": 750000, "normalized_value": 750000},
                {"value": "eleven lakh", "normalized_value": None},
            ],
        }
        self.assertEqual(assess_finding(finding), "Unreadable")

    def test_unreadable_low_ocr(self):
        finding = {
            "field": "expenditure_amount",
            "check_type": "cross_document",
            "result": "pass",
            "sources": [
                {"value": 750000, "normalized_value": 750000,
                 "ocr_confidence": 40},
            ],
        }
        self.assertEqual(assess_finding(finding), "Unreadable")

    def test_overall_status_is_conflicting(self):
        verification_result = {
            "project_id": "MPL002",
            "findings": [
                {"field": "project_id", "check_type": "project_id_consistency",
                 "result": "pass", "sources": []},
                {"field": "expenditure_amount", "check_type": "cross_document",
                 "result": "conflict", "sources": []},
                {"field": "bill_number", "check_type": "missing_field",
                 "result": "unable", "sources": []},
            ],
        }
        report = assess_project(verification_result)
        self.assertEqual(report["overall_status"], "Conflicting")
        self.assertEqual(report["status_counts"]["Insufficient Evidence"], 1)
    def test_suggestion_for_conflict(self):
        finding = {
            "field": "expenditure_amount",
            "check_type": "cross_document",
            "result": "conflict",
            "difference": 50000,
            "sources": [],
        }
        text = suggest_evidence(finding, "Conflicting")
        self.assertIn("bill", text)
        self.assertIn("50000", text)

    def test_no_suggestion_when_supported(self):
        finding = {"field": "project_id", "result": "pass", "sources": []}
        self.assertEqual(suggest_evidence(finding, "Supported"), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)