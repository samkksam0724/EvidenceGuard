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


def assess_project(verification_result):
    """Assess every finding and give one overall status for the project."""
    assessed = []

    for finding in verification_result["findings"]:
        item = dict(finding)
        item["reliability_status"] = assess_finding(finding)
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