
import pandas as pd
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import timedelta


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "data" / "csv" / "project_records.csv"

OUTPUT_DIR = BASE_DIR / "data" / "documents"


# Read project records
df = pd.read_csv(CSV_PATH)


def format_amount(amount):
    """Format amounts in Indian currency style."""
    return "Rs. " + format(int(amount), ",")


def create_pdf(filename, title, lines):
    """Create a simple text-based PDF document."""

    filename.parent.mkdir(parents=True, exist_ok=True)

    pdf = canvas.Canvas(str(filename), pagesize=A4)

    width, height = A4
    y = height - 70

    pdf.setTitle(title)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, title)

    y -= 40

    pdf.setFont("Helvetica", 11)

    for line in lines:
        pdf.drawString(50, y, str(line))
        y -= 25

    pdf.save()


# Generate four documents for every project
for _, project in df.iterrows():

    project_id = project["project_id"]

    work_name = project["work_name"]
    location = project["location"]
    agency = project["implementing_agency"]

    sanctioned = int(project["sanctioned_amount"])
    expenditure = int(project["expenditure_amount"])

    sanction_date = pd.to_datetime(project["sanction_date"])
    completion_date = pd.to_datetime(project["completion_date"])

    # Create project-specific folder
    project_folder = OUTPUT_DIR / project_id
    project_folder.mkdir(parents=True, exist_ok=True)


    # ---------------------------------
    # 1. SANCTION ORDER
    # ---------------------------------

    sanction_lines = [
        "Government of India - Synthetic Sample",
        "Document Type: Sanction Order",
        f"Project ID: {project_id}",
        f"Work Name: {work_name}",
        f"Location: {location}",
        f"Sanctioned Amount: {format_amount(sanctioned)}",
        f"Sanction Date: {sanction_date.date()}",
        f"Implementing Agency: {agency}",
        "Status: Approved"
    ]

    create_pdf(
        project_folder / "sanction_order.pdf",
        "SANCTION ORDER",
        sanction_lines
    )


    # ---------------------------------
    # 2. EXPENDITURE STATEMENT
    # ---------------------------------

    expense_1 = round(expenditure * 0.40)
    expense_2 = round(expenditure * 0.35)
    expense_3 = expenditure - expense_1 - expense_2

    expenditure_lines = [
        "Government of India - Synthetic Sample",
        "Document Type: Expenditure Statement",
        f"Project ID: {project_id}",
        f"Work Name: {work_name}",
        f"Sanctioned Amount: {format_amount(sanctioned)}",
        f"Total Expenditure: {format_amount(expenditure)}",
        "",
        "Expense Breakdown:",
        f"Material Costs: {format_amount(expense_1)}",
        f"Labour Costs: {format_amount(expense_2)}",
        f"Other Costs: {format_amount(expense_3)}",
        f"Statement Date: {completion_date.date()}"
    ]

    create_pdf(
        project_folder / "expenditure_statement.pdf",
        "EXPENDITURE STATEMENT",
        expenditure_lines
    )


    # ---------------------------------
    # 3. BILL
    # ---------------------------------

    bill_date = sanction_date + timedelta(days=60)

    # Deliberately introduce one discrepancy
    bill_amount = expenditure

    if project_id == "MPL002":
        bill_amount = expenditure + 50000

    bill_lines = [
        "Government of India - Synthetic Sample",
        "Document Type: Final Bill",
        f"Bill Number: BILL-{project_id}-001",
        f"Project ID: {project_id}",
        f"Work Name: {work_name}",
        f"Vendor: {agency}",
        f"Bill Date: {bill_date.date()}",
        f"Bill Amount: {format_amount(bill_amount)}",
        "Payment Status: Recorded"
    ]

    create_pdf(
        project_folder / "bill.pdf",
        "PROJECT BILL",
        bill_lines
    )


    # ---------------------------------
    # 4. COMPLETION REPORT
    # ---------------------------------

    completion_lines = [
        "Government of India - Synthetic Sample",
        "Document Type: Completion Report",
        f"Project ID: {project_id}",
        f"Work Name: {work_name}",
        f"Location: {location}",
        f"Implementing Agency: {agency}",
        f"Completion Date: {completion_date.date()}",
        "Completion Status: Completed",
        f"Reported Expenditure: {format_amount(expenditure)}"
    ]

    create_pdf(
        project_folder / "completion_report.pdf",
        "COMPLETION REPORT",
        completion_lines
    )


print("Synthetic dataset generated successfully!")

print("\nGenerated documents:")

for project_folder in sorted(OUTPUT_DIR.iterdir()):

    if project_folder.is_dir():

        print(f"\n{project_folder.name}:")

        for document in sorted(project_folder.iterdir()):
            print(" -", document.name)
