import unittest
import pandas as pd
from pathlib import Path

from modules.verification import verify_project


class TestMissingFields(unittest.TestCase):

    def test_missing_bill_fields(self):

        base_dir = Path(__file__).resolve().parent

        df = pd.read_csv(
            base_dir / "data" / "csv" / "project_records.csv"
        )

        project_record = df[
            df["project_id"] == "MPL001"
        ].iloc[0].to_dict()

        incomplete_bill = {
            "project_id": "MPL001",
            "document_type": "bill",
            "source_file": "bill.pdf",
            "fields": [
                {
                    "field": "project_id",
                    "raw_value": "MPL001",
                    "page": 1
                },
                {
                    "field": "expenditure_amount",
                    "raw_value": "Rs. 7,50,000",
                    "page": 1
                }
            ]
        }

        result = verify_project(
            project_record,
            [incomplete_bill]
        )

        missing_findings = [
            finding for finding in result["findings"]
            if finding["check_type"] == "missing_field"
        ]

        missing_fields = [
            finding["field"] for finding in missing_findings
        ]

        self.assertIn("bill_number", missing_fields)
        self.assertIn("bill_date", missing_fields)

        print("\nMissing fields detected:", missing_fields)


if __name__ == "__main__":
    unittest.main(verbosity=2)