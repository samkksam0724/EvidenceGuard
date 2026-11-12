
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

files = [
    BASE_DIR / "data/synthetic/sample_extraction.json",
    BASE_DIR / "data/synthetic/sample_verification.json"
]

for file_path in files:

    with open(file_path, "r") as file:
        data = json.load(file)

    print("\nFile:", file_path.name)
    print("Project ID:", data["project_id"])

    if "fields" in data:
        print("Extracted fields:", len(data["fields"]))

    if "findings" in data:
        print("Verification findings:", len(data["findings"]))

print("\nJSON files loaded successfully!")
