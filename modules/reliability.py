STATUS_SUPPORTED = "Supported"
STATUS_CONFLICTING = "Conflicting"
STATUS_INSUFFICIENT = "Insufficient Evidence"
STATUS_UNREADABLE = "Unreadable"

OCR_CONFIDENCE_THRESHOLD = 60

# Order of importance for the overall project status
STATUS_PRIORITY = [
    STATUS_CONFLICTING,
    STATUS_UNREADABLE,
    STATUS_INSUFFICIENT,
    STATUS_SUPPORTED,
]

# What to ask for when two sources disagree on a field
CONFLICT_REQUESTS = {
    "expenditure_amount": (
        "Request the original bill and expenditure statement, and ask the "
        "implementing agency to explain the difference"
    ),
    "sanctioned_amount": (
        "Request the original sanction order and confirm the sanctioned "
        "amount with the sanctioning authority"
    ),
    "sanction_date": "Request the original sanction order to confirm the date",
    "completion_date": (
        "Request the original completion report and confirm the completion "
        "date with the implementing agency"
    ),
    "bill_date": "Request the original bill to confirm the bill date",
    "project_id": "Request the original documents and confirm the correct project ID",
}


def _has_low_ocr(sources):
    """True if any source has an extraction confidence below the threshold."""
    for source in sources:
        confidence = source.get("confidence", source.get("ocr_confidence"))
        if confidence is not None and confidence < OCR_CONFIDENCE_THRESHOLD:
            return True
    return False


def _has_unparseable_value(sources):
    """A value was found in the document but could not be normalized."""
    for source in sources:
        value = source.get("value")
        if (
            isinstance(value, (str, int, float))
            and value != ""
            and source.get("normalized_value") is None
        ):
            return True
    return False


def assess_finding(finding):
    """Map one verification finding to one of the four statuses."""
    sources = finding.get("sources", [])
    result = finding.get("result")

    # Unreliable text comes first: we can't trust anything read from it
    if _has_low_ocr(sources):
        return STATUS_UNREADABLE

    if result == "conflict":
        return STATUS_CONFLICTING

    if result == "pass":
        return STATUS_SUPPORTED

    # result == "unable"
    if finding.get("check_type") == "missing_field":
        return STATUS_INSUFFICIENT

    if _has_unparseable_value(sources):
        return STATUS_UNREADABLE

    return STATUS_INSUFFICIENT


def _source_name(finding):
    for source in finding.get("sources", []):
        name = source.get("source_file")
        if name and name != "project_records.csv":
            return name
    return "the supporting document"


def suggest_evidence(finding, status):
    """Say what the reviewer should ask for. Empty text if nothing is needed."""
    field = finding.get("field", "this field")
    source_name = _source_name(finding)

    if status == STATUS_SUPPORTED:
        return ""

    if status == STATUS_CONFLICTING:
        text = CONFLICT_REQUESTS.get(
            field,
            f"Request the original documents for {field} and ask the "
            "implementing agency to explain the mismatch",
        )
        difference = finding.get("difference")
        if difference not in (None, "", 0):
            text += f" (difference: Rs. {difference})"
        return text

    if status == STATUS_UNREADABLE:
        return (
            f"Request a clearer or digital copy of {source_name}, "
            f"so {field} can be read reliably"
        )

    # Insufficient Evidence
    if finding.get("check_type") == "missing_field":
        return f"Request a copy of {source_name} that clearly shows {field}"

    return (
        f"Request supporting document(s) that state {field}, "
        "so it can be compared with the project record"
    )


def assess_project(verification_result):
    """Assess every finding and give one overall status for the project."""
    assessed = []

    for finding in verification_result["findings"]:
        item = dict(finding)
        status = assess_finding(finding)
        item["reliability_status"] = status
        item["suggested_evidence"] = suggest_evidence(finding, status)
        assessed.append(item)

    counts = {status: 0 for status in STATUS_PRIORITY}
    for item in assessed:
        counts[item["reliability_status"]] += 1

    overall = STATUS_SUPPORTED
    for status in STATUS_PRIORITY:
        if counts[status] > 0:
            overall = status
            break

    return {
        "project_id": verification_result["project_id"],
        "overall_status": overall,
        "status_counts": counts,
        "findings": assessed,
    }