import json
import unittest
import pandas as pd
from pathlib import Path

from modules.verification import verify_project


class TestSampleExtraction(unittest.TestCase):

    def test_sample_extraction_compatibility(self):

        base_dir = Path(__file__).resolve().parent

        df = pd.read_csv(
            base_dir / "data" / "csv" / "project_records.csv"
        )

        project_record = df[
            df["project_id"] == "MPL001"
        ].iloc[0].to_dict()

        with open(
            base_dir / "data" / "synthetic" / "sample_extraction.json",
            "r"
        ) as file:
            sample = json.load(file)

        result = verify_project(project_record, [sample])

        self.assertEqual(result["project_id"], "MPL001")

        self.assertTrue(
            any(
                finding["field"] == "expenditure_amount"
                and finding["result"] == "pass"
                for finding in result["findings"]
            )
        )

        self.assertTrue(
            any(
                finding["field"] == "bill_number"
                and finding["result"] == "unable"
                for finding in result["findings"]
            )
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)