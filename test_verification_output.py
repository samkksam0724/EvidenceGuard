import unittest
import pandas as pd
from pathlib import Path

from modules.verification import verify_project


class TestVerificationOutput(unittest.TestCase):

    def test_output_structure(self):

        base_dir = Path(__file__).resolve().parent

        df = pd.read_csv(
            base_dir / "data" / "csv" / "project_records.csv"
        )

        project_record = df[
            df["project_id"] == "MPL001"
        ].iloc[0].to_dict()

        bill = {
            "project_id": "MPL001",
            "document_type": "bill",
            "source_file": "bill.pdf",
            "fields": [
                {"field": "project_id", "raw_value": "MPL001", "page": 1},
                {"field": "expenditure_amount", "raw_value": "750000", "page": 1},
                {"field": "bill_number", "raw_value": "BILL-MPL001-001", "page": 1},
                {"field": "bill_date", "raw_value": "2026-03-11", "page": 1}
            ]
        }

        result = verify_project(project_record, [bill])

        self.assertIn("project_id", result)
        self.assertIn("findings", result)

        required_keys = {
            "field",
            "sources",
            "check_type",
            "result",
            "explanation"
        }

        allowed_results = {"pass", "conflict", "unable"}

        for finding in result["findings"]:

            self.assertTrue(required_keys.issubset(finding.keys()))

            self.assertIn(
                finding["result"],
                allowed_results
            )

            self.assertIsInstance(finding["sources"], list)

        print("\nVerification output structure is valid.")
        print("Total findings:", len(result["findings"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)