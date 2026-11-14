
from modules.normalization import (
    normalize_amount,
    normalize_date,
    normalize_project_id,
    normalize_text,
)


# Maps different document field names to a common verification field.
FIELD_ALIASES = {
    "bill_amount": "expenditure_amount",
    "total_expenditure": "expenditure_amount",
    "reported_expenditure": "expenditure_amount",
    "sanctioned_amount": "sanctioned_amount",
    "material_cost": "material_cost",
    "labour_cost": "labour_cost",
    "other_cost": "other_cost",
}

# Fields expected in each document type.
REQUIRED_FIELDS = {
    "sanction_order": [
        "project_id",
        "sanctioned_amount",
        "sanction_date",
    ],
    "expenditure_statement": [
        "project_id",
        "expenditure_amount",
    ],
    "bill": [
        "project_id",
        "bill_number",
        "bill_date",
        "expenditure_amount",
    ],
    "completion_report": [
        "project_id",
        "completion_date",
    ],
}


def get_normalized_value(field, value):
    """Apply the appropriate normalisation function to a field."""

    if field in ("sanctioned_amount", "expenditure_amount",
                 "material_cost", "labour_cost", "other_cost"):
        return normalize_amount(value)

    if field in ("sanction_date", "completion_date", "bill_date",
                 "statement_date"):
        return normalize_date(value)

    if field == "project_id":
        return normalize_project_id(value)

    return normalize_text(value, casefold=True)


def extract_fields(document):
    """
    Convert a document's fields list into a dictionary.

    Keeps the original field information, including page and raw value.
    """

    result = {}

    for item in document.get("fields", []):
        field_name = item.get("field")

        if field_name:
            result[field_name] = item

    return result


def make_source(source_file, value, normalized_value=None, page=None):
    """Create a consistent source entry for a finding."""

    return {
        "source_file": source_file,
        "value": value,
        "normalized_value": normalized_value,
        "page": page,
    }


def create_finding(
    field,
    sources,
    check_type,
    result,
    explanation,
    difference=None,
):
    """Create one structured verification finding."""

    finding = {
        "field": field,
        "sources": sources,
        "check_type": check_type,
        "result": result,
        "explanation": explanation,
    }

    if difference is not None:
        finding["difference"] = difference

    return finding


def verify_project(project_record, extracted_documents):
    """
    Verify extracted documents against one project CSV record.

    Parameters:
        project_record: Dictionary representing one CSV row.
        extracted_documents: List of extracted document dictionaries.

    Returns:
        Dictionary containing project_id and verification findings.
    """

    findings = []

    project_id = normalize_project_id(
        project_record.get("project_id")
    )

    csv_source = "project_records.csv"

    # -------------------------------------------------
    # 1. Check project IDs across all documents.
    # -------------------------------------------------

    for document in extracted_documents:
        document_fields = extract_fields(document)
        source_file = document.get("source_file", "Unknown document")

        project_field = document_fields.get("project_id")

        if not project_field:
            findings.append(create_finding(
                "project_id",
                [make_source(csv_source, project_record.get("project_id"))],
                "project_id_consistency",
                "unable",
                f"Project ID is missing from {source_file}."
            ))
            continue

        raw_id = project_field.get("raw_value")
        normalized_id = normalize_project_id(raw_id)

        sources = [
            make_source(csv_source, project_record.get("project_id"),
                        project_id),
            make_source(
                source_file,
                raw_id,
                normalized_id,
                project_field.get("page"),
            ),
        ]

        if normalized_id == project_id:
            result = "pass"
            explanation = "Project IDs match."
        else:
            result = "conflict"
            explanation = "Project ID differs from the CSV reference."

        findings.append(create_finding(
            "project_id",
            sources,
            "project_id_consistency",
            result,
            explanation,
        ))

    # -------------------------------------------------
    # 2. Check expenditure and sanctioned amounts.
    # -------------------------------------------------

    amount_fields = {
        "sanctioned_amount": "sanctioned_amount",
        "expenditure_amount": "expenditure_amount",
    }

    for common_field, csv_field in amount_fields.items():

        reference_value = project_record.get(csv_field)

        if reference_value is None:
            continue

        reference_normalized = normalize_amount(reference_value)

        sources = [
            make_source(
                csv_source,
                reference_value,
                reference_normalized,
            )
        ]

        for document in extracted_documents:
            document_fields = extract_fields(document)
            source_file = document.get("source_file", "Unknown document")

            for original_field, item in document_fields.items():
                mapped_field = FIELD_ALIASES.get(
                    original_field, original_field
                )

                if mapped_field != common_field:
                    continue

                raw_value = item.get("raw_value")
                normalized_value = item.get("normalized_value")

                # Prefer normalising the raw value ourselves.
                try:
                    normalized_value = normalize_amount(raw_value)
                except ValueError:
                    normalized_value = None

                sources.append(make_source(
                    source_file,
                    raw_value,
                    normalized_value,
                    item.get("page"),
                ))

        comparable_values = [
            source["normalized_value"]
            for source in sources
            if source["normalized_value"] is not None
        ]

        if len(comparable_values) < 2:
            result = "unable"
            difference = None
            explanation = (
                f"Not enough valid values to verify {common_field}."
            )
        elif all(value == comparable_values[0]
                 for value in comparable_values):
            result = "pass"
            difference = 0
            explanation = (
                f"All available {common_field} values match."
            )
        else:
            result = "conflict"
            difference = max(comparable_values) - min(comparable_values)
            explanation = (
                f"Conflicting {common_field} values were found "
                "across the CSV and supporting documents."
            )

        findings.append(create_finding(
            common_field,
            sources,
            "cross_document",
            result,
            explanation,
            difference,
        ))

    # -------------------------------------------------
    # 3. Check date validity and logical date order.
    # -------------------------------------------------

    reference_dates = {}

    for field in ("sanction_date", "completion_date"):
        raw_value = project_record.get(field)

        if raw_value is not None:
            try:
                reference_dates[field] = normalize_date(raw_value)
            except ValueError:
                findings.append(create_finding(
                    field,
                    [make_source(csv_source, raw_value)],
                    "date_validity",
                    "unable",
                    f"The CSV contains an invalid {field}."
                ))

    document_dates = {}

    for document in extracted_documents:
        document_fields = extract_fields(document)
        source_file = document.get("source_file", "Unknown document")

        for field in ("sanction_date", "completion_date", "bill_date",
                      "statement_date"):

            item = document_fields.get(field)

            if not item:
                continue

            raw_value = item.get("raw_value")

            try:
                normalized_value = normalize_date(raw_value)
            except ValueError:
                findings.append(create_finding(
                    field,
                    [make_source(
                        source_file, raw_value, page=item.get("page")
                    )],
                    "date_validity",
                    "unable",
                    f"Invalid date found in {source_file}."
                ))
                continue

            if normalized_value is not None:
                document_dates[field] = {
                    "value": normalized_value,
                    "source_file": source_file,
                    "raw_value": raw_value,
                    "page": item.get("page"),
                }

    # Compare dates with their corresponding CSV fields.
    for field, reference_value in reference_dates.items():
        document_date = document_dates.get(field)

        if not document_date:
            continue

        sources = [
            make_source(csv_source, project_record.get(field),
                        reference_value),
            make_source(
                document_date["source_file"],
                document_date["raw_value"],
                document_date["value"],
                document_date["page"],
            ),
        ]

        result = (
            "pass" if reference_value == document_date["value"]
            else "conflict"
        )

        findings.append(create_finding(
            field,
            sources,
            "date_consistency",
            result,
            "Dates match." if result == "pass"
            else "Document date differs from the CSV reference.",
        ))

    # Check logical order: sanction <= bill <= completion.
    ordered_dates = {}

    for field in ("sanction_date", "bill_date", "completion_date"):
        if field in reference_dates:
            ordered_dates[field] = reference_dates[field]
        elif field in document_dates:
            ordered_dates[field] = document_dates[field]["value"]

    if "bill_date" in document_dates:
        ordered_dates["bill_date"] = document_dates["bill_date"]["value"]

    date_sequence = [
        ordered_dates[field]
        for field in ("sanction_date", "bill_date", "completion_date")
        if field in ordered_dates
    ]

    if len(date_sequence) >= 2:
        valid_order = all(
            date_sequence[index] <= date_sequence[index + 1]
            for index in range(len(date_sequence) - 1)
        )

        findings.append(create_finding(
            "date_order",
            [
                make_source(csv_source, ordered_dates)
            ],
            "logical_date_order",
            "pass" if valid_order else "conflict",
            "Project dates follow a logical order."
            if valid_order else
            "A project date occurs before an earlier required milestone.",
        ))

    # -------------------------------------------------
    # 4. Check expenditure breakdown arithmetic.
    # -------------------------------------------------

    for document in extracted_documents:
        document_fields = extract_fields(document)
        source_file = document.get("source_file", "Unknown document")

        breakdown_fields = (
            "material_cost", "labour_cost", "other_cost"
        )

        if not all(field in document_fields for field in breakdown_fields):
            continue

        try:
            amounts = {
                field: normalize_amount(
                    document_fields[field].get("raw_value")
                )
                for field in breakdown_fields
            }

            total = normalize_amount(
                document_fields.get(
                    "expenditure_amount", {}
                ).get("raw_value")
            )

            if total is None or any(
                value is None for value in amounts.values()
            ):
                raise ValueError("Missing arithmetic value.")

            calculated_total = sum(amounts.values())
            valid = calculated_total == total

            findings.append(create_finding(
                "expenditure_breakdown",
                [
                    make_source(source_file, amounts),
                    make_source(source_file, total),
                ],
                "internal_arithmetic",
                "pass" if valid else "conflict",
                "Expense breakdown equals the reported total."
                if valid else
                "Expense breakdown does not equal the reported total.",
                abs(calculated_total - total),
            ))

        except (ValueError, TypeError):
            findings.append(create_finding(
                "expenditure_breakdown",
                [make_source(source_file, None)],
                "internal_arithmetic",
                "unable",
                "Unable to verify arithmetic because values are missing "
                "or invalid.",
            ))

    # -------------------------------------------------
    # 5. Check required fields in each document.
    # -------------------------------------------------

    for document in extracted_documents:
        document_fields = extract_fields(document)
        document_type = document.get("document_type")
        source_file = document.get("source_file", "Unknown document")

        required_fields = REQUIRED_FIELDS.get(document_type, [])

        for field in required_fields:
            item = document_fields.get(field)

            if item is None or item.get("raw_value") in (None, ""):
                findings.append(create_finding(
                    field,
                    [make_source(source_file, None)],
                    "missing_field",
                    "unable",
                    f"Required field '{field}' is missing "
                    f"from {source_file}.",
                ))

    # -------------------------------------------------
    # 6. Check duplicate bill numbers within this project.
    # -------------------------------------------------

    bill_numbers = {}

    for document in extracted_documents:
        document_fields = extract_fields(document)
        item = document_fields.get("bill_number")

        if not item:
            continue

        bill_number = normalize_text(
            item.get("raw_value"), casefold=True
        )

        if bill_number is None:
            continue

        bill_numbers.setdefault(bill_number, []).append(
            document.get("source_file", "Unknown document")
        )

    for bill_number, source_files in bill_numbers.items():
        if len(source_files) > 1:
            findings.append(create_finding(
                "bill_number",
                [
                    make_source(source_file, bill_number)
                    for source_file in source_files
                ],
                "duplicate_bill",
                "conflict",
                "The same bill number appears more than once "
                "in the supplied documents.",
            ))

    return {
        "project_id": project_id,
        "findings": findings,
    }
