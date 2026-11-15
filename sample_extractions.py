def _doc(project_id, doc_type, source_file, pairs):
    return {
        "project_id": project_id,
        "document_type": doc_type,
        "source_file": source_file,
        "fields": [
            {"field": name, "raw_value": value, "page": 1}
            for name, value in pairs
        ],
    }


def _project_docs(pid, sanction_amt, sanction_date, expenditure_statement_amt,
                  bill_amt, bill_no, bill_date, completion_date):
    return [
        _doc(pid, "sanction_order", "sanction_order.pdf", [
            ("project_id", pid),
            ("sanctioned_amount", sanction_amt),
            ("sanction_date", sanction_date),
        ]),
        _doc(pid, "expenditure_statement", "expenditure_statement.pdf", [
            ("project_id", pid),
            ("expenditure_amount", expenditure_statement_amt),
        ]),
        _doc(pid, "bill", "bill.pdf", [
            ("project_id", pid),
            ("expenditure_amount", bill_amt),
            ("bill_number", bill_no),
            ("bill_date", bill_date),
        ]),
        _doc(pid, "completion_report", "completion_report.pdf", [
            ("project_id", pid),
            ("completion_date", completion_date),
        ]),
    ]


# Stand-in extraction data until the PDF extraction module is ready.
# MPL002 deliberately has a bill amount that differs from the CSV.
SAMPLE_EXTRACTIONS = {
    "MPL001": _project_docs(
        "MPL001", "Rs. 8,00,000", "2026-01-10", "Rs. 7,50,000",
        "Rs. 7,50,000", "BILL-MPL001-001", "2026-03-11", "2026-06-15",
    ),
    "MPL002": _project_docs(
        "MPL002", "Rs. 12,00,000", "2026-02-05", "Rs. 11,00,000",
        "Rs. 11,50,000", "BILL-MPL002-001", "2026-04-10", "2026-07-20",
    ),
    "MPL003": _project_docs(
        "MPL003", "Rs. 6,00,000", "2026-03-12", "Rs. 5,80,000",
        "Rs. 5,80,000", "BILL-MPL003-001", "2026-05-20", "2026-08-25",
    ),
}