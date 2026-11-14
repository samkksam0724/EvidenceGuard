import unittest
import pandas as pd
from pathlib import Path

from modules.verification import verify_project


class TestCompleteDocuments(unittest.TestCase):

    def test_all_four_documents(self):

        base_dir = Path(__file__).resolve().parent

        df = pd.read_csv(
            base_dir / "data" / "csv" / "project_records.csv"
        )

        project_record = df[
            df["project_id"] == "MPL001"
        ].iloc[0].to_dict()

        documents = [
            {
                "project_id": "MPL001",
                "document_type": "sanction_order",
                "source_file": "sanction_order.pdf",
                "fields": [
                    {"field": "project_id", "raw_value": "MPL001", "page": 1},
                    {"field": "sanctioned_amount", "raw_value": "Rs. 8,00,000", "page": 1},
                    {"field": "sanction_date", "raw_value": "2026-01-10", "page": 1}
                ]
            },
            {
                "project_id": "MPL001",
                "document_type": "expenditure_statement",
                "source_file": "expenditure_statement.pdf",
                "fields": [
                    {"field": "project_id", "raw_value": "MPL001", "page": 1},
                    {"field": "expenditure_amount", "raw_value": "Rs. 7,50,000", "page": 1}
                ]
            },
            {
                "project_id": "MPL001",
                "document_type": "bill",
                "source_file": "bill.pdf",
                "fields": [
                    {"field": "project_id", "raw_value": "MPL001", "page": 1},
                    {"field": "expenditure_amount", "raw_value": "Rs. 7,50,000", "page": 1},
                    {"field": "bill_number", "raw_value": "BILL-MPL001-001", "page": 1},
                    {"field": "bill_date", "raw_value": "2026-03-11", "page": 1}
                ]
            },
            {
                "project_id": "MPL001",
                "document_type": "completion_report",
                "source_file": "completion_report.pdf",
                "fields": [
                    {"field": "project_id", "raw_value": "MPL001", "page": 1},
                    {"field": "completion_date", "raw_value": "2026-06-15", "page": 1}
                ]
            }
        ]

        result = verify_project(project_record, documents)

        print("\nPROJECT:", result["project_id"])
        print("\nFINDINGS:")

        for finding in result["findings"]:
            print(
                finding["field"],
                "|",
                finding["check_type"],
                "|",
                finding["result"]
            )

        self.assertEqual(result["project_id"], "MPL001")

        amount_findings = [
            finding for finding in result["findings"]
            if finding["field"] == "expenditure_amount"
        ]

        self.assertEqual(len(amount_findings), 1)
        self.assertEqual(amount_findings[0]["result"], "pass")


if __name__ == "__main__":
    unittest.main(verbosity=2)