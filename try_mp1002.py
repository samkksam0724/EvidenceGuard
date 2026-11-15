import pandas as pd
from pathlib import Path
from modules.verification import verify_project

BASE_DIR = Path(__file__).resolve().parent

df = pd.read_csv(BASE_DIR / "data" / "csv" / "project_records.csv")
project_record = df[df["project_id"] == "MPL002"].iloc[0].to_dict()

bill = {
    "project_id": "MPL002",
    "document_type": "bill",
    "source_file": "bill.pdf",
    "fields": [
        {"field": "project_id", "raw_value": "MPL002", "page": 1},
        {"field": "expenditure_amount", "raw_value": "Rs. 11,50,000", "page": 1},
    ],
}

result = verify_project(project_record, [bill])

for finding in result["findings"]:
    print(finding)
from modules.reliability import assess_project

report = assess_project(result)

print("\nOVERALL STATUS:", report["overall_status"])
print("COUNTS:", report["status_counts"])
print()
for f in report["findings"]:
    print(f["field"], "->", f["reliability_status"])