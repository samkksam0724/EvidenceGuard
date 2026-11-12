
# Standard document types

DOCUMENT_TYPES = [
    "sanction_order",
    "expenditure_statement",
    "bill",
    "completion_report"
]


# Standard fields extracted from documents

FIELD_NAMES = [
    "project_id",
    "work_name",
    "location",
    "sanctioned_amount",
    "expenditure_amount",
    "sanction_date",
    "completion_date",
    "implementing_agency",
    "vendor",
    "bill_number"
]


# Evidence reliability statuses

RELIABILITY_STATUSES = [
    "Supported",
    "Conflicting",
    "Insufficient Evidence",
    "Unreadable"
]


# Extraction methods

EXTRACTION_METHODS = [
    "pdf_text",
    "ocr"
]
