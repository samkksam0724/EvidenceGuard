import pandas as pd
from pathlib import Path
from modules.verification import verify_project

BASE_DIR = Path(__file__).resolve().parent

df = pd.read_csv(
    BASE_DIR / "data" / "csv" / "project_records.csv"
)

project_record = df[
    df["project_id"] == "MPL001"
].iloc[0].to_dict()

matching_bill = {
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
        },
        {
            "field": "bill_date",
            "raw_value": "2026-03-11",
            "page": 1
        },
        {
            "field": "bill_number",
            "raw_value": "BILL-MPL001-001",
            "page": 1
        },
    ],
}

result = verify_project(project_record, [matching_bill])

print("\nPROJECT:", result["project_id"])
print("\nVERIFICATION FINDINGS:")

for finding in result["findings"]:
    print("\nField:", finding["field"])
    print("Check:", finding["check_type"])
    print("Result:", finding["result"])
    print("Explanation:", finding["explanation"])

    if "difference" in finding:
        print("Difference:", finding["difference"])