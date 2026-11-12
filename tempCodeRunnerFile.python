
import pdfplumber
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENT_DIR = BASE_DIR / "data" / "documents"

pdf_files = list(DOCUMENT_DIR.rglob("*.pdf"))

print("Total PDF documents:", len(pdf_files))

for pdf_path in sorted(pdf_files):

    with pdfplumber.open(pdf_path) as pdf:

        text = ""

        for page in pdf.pages:
            text += page.extract_text() or ""

    print("\n-----------------------------")
    print("File:", pdf_path.name)
    print("Project:", pdf_path.parent.name)
    print(text)

assert len(pdf_files) == 12, "Expected 12 PDF documents!"

print("\nAll 12 PDF documents generated successfully.")
