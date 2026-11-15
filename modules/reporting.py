from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

STATUS_COLORS = {
    "Supported": colors.HexColor("#2e7d32"),
    "Conflicting": colors.HexColor("#c62828"),
    "Insufficient Evidence": colors.HexColor("#b26a00"),
    "Unreadable": colors.HexColor("#616161"),
}


def _describe_sources(sources):
    parts = []
    for source in sources:
        where = source.get("source_file", "unknown")
        if source.get("page") is not None:
            where += f" (page {source['page']})"
        parts.append(f"{where}: {source.get('value')}")
    return "<br/>".join(escape(p) for p in parts)


def build_report(report, decision=None, justification=None):
    """Build the reviewer report and return it as PDF bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()
    small = styles["BodyText"].clone("small")
    small.fontSize = 8
    small.leading = 10

    story = []
    story.append(Paragraph("EvidenceGuard - Reviewer Report", styles["Title"]))
    story.append(Paragraph(
        f"Project: <b>{escape(str(report['project_id']))}</b><br/>"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["BodyText"],
    ))
    story.append(Spacer(1, 8))

    overall = report["overall_status"]
    color = STATUS_COLORS.get(overall, colors.black).hexval()[2:]
    story.append(Paragraph(
        f"Overall status: <font color='#{color}'><b>{escape(overall)}</b></font>",
        styles["Heading2"],
    ))

    counts = ", ".join(f"{k}: {v}" for k, v in report["status_counts"].items())
    story.append(Paragraph(escape(counts), styles["BodyText"]))
    story.append(Spacer(1, 10))

    header = ["Field", "Check", "Status", "Explanation", "Difference", "Evidence", "Suggested evidence"]   
    rows = [header]
    for f in report["findings"]:
        rows.append([
            Paragraph(escape(f["field"]), small),
            Paragraph(escape(f["check_type"]), small),
            Paragraph(escape(f["reliability_status"]), small),
            Paragraph(escape(f["explanation"]), small),
            Paragraph(escape(str(f.get("difference", ""))), small),
            Paragraph(_describe_sources(f.get("sources", [])), small),
            Paragraph(escape(f.get("suggested_evidence", "")), small),
        
        ])

    table = Table(
        rows,
        colWidths=[70, 80, 75, 150, 45, 190, 150],
        repeatRows=1,
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263238")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Reviewer decision", styles["Heading2"]))
    if decision:
        story.append(Paragraph(f"Decision: <b>{escape(decision)}</b>", styles["BodyText"]))
        story.append(Paragraph(
            f"Justification: {escape(justification or '(none given)')}",
            styles["BodyText"],
        ))
    else:
        story.append(Paragraph("No decision recorded.", styles["BodyText"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Note: Supported means no inconsistency was detected in the "
        "available checks. It does not prove the project is genuine.",
        small,
    ))

    doc.build(story)
    return buffer.getvalue()