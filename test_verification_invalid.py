import unittest
import pandas as pd
from pathlib import Path

from modules.verification import verify_project


class TestInvalidValues(unittest.TestCase):

    def test_invalid_expenditure_amount(self):

        base_dir = Path(__file__).resolve().parent

        df = pd.read_csv(
            base_dir / "data" / "csv" / "project_records.csv"
        )

        project_record = df[
            df["project_id"] == "MPL001"
        ].iloc[0].to_dict()

        invalid_bill = {
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
                    "raw_value": "eleven lakh",
                    "page": 1
                },
                {
                    "field": "bill_number",
                    "raw_value": "BILL-MPL001-001",
                    "page": 1
                },
                {
                    "field": "bill_date",
                    "raw_value": "2026-03-11",
                    "page": 1
                }
            ]
        }

        result = verify_project(
            project_record,
            [invalid_bill]
        )

        expenditure_findings = [
            finding for finding in result["findings"]
            if finding["field"] == "expenditure_amount"
        ]

        self.assertEqual(len(expenditure_findings), 1)

        self.assertEqual(
            expenditure_findings[0]["result"],
            "unable"
        )

        print(
            "\nInvalid amount result:",
            expenditure_findings[0]["result"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)