from datetime import datetime

import pandas as pd
import streamlit as st

from modules.reliability import assess_project
from modules.verification import verify_project
from sample_extractions import SAMPLE_EXTRACTIONS

STATUS_ICONS = {
    "Supported": "🟢 Supported",
    "Conflicting": "🔴 Conflicting",
    "Insufficient Evidence": "🟡 Insufficient Evidence",
    "Unreadable": "⚪ Unreadable",
}

DECISIONS = [
    "Accept finding",
    "Request additional evidence",
    "Mark for manual review",
]


def describe_sources(sources):
    parts = []
    for source in sources:
        page = source.get("page")
        where = source.get("source_file", "unknown")
        if page is not None:
            where += f" (page {page})"
        parts.append(f"{where}: {source.get('value')}")
    return " | ".join(parts)


def findings_table(report):
    rows = []
    for f in report["findings"]:
        rows.append({
            "Field": f["field"],
            "Check": f["check_type"],
            "Status": STATUS_ICONS[f["reliability_status"]],
            "Explanation": f["explanation"],
            "Difference": f.get("difference", ""),
            "Evidence": describe_sources(f.get("sources", [])),
        })
    return pd.DataFrame(rows)


st.set_page_config(page_title="EvidenceGuard", layout="wide")

st.title("EvidenceGuard")
st.subheader("MPLADS Document Verification Assistant")
st.write("Upload project records and supporting documents.")

csv_file = st.file_uploader("Upload Project CSV", type=["csv"])
pdf_files = st.file_uploader(
    "Upload Supporting PDFs",
    type=["pdf"],
    accept_multiple_files=True,
)

df = None
if csv_file:
    csv_file.seek(0)
    df = pd.read_csv(csv_file)
    st.write("Project records preview:")
    st.dataframe(df, use_container_width=True)

if csv_file and pdf_files:
    st.success("Documents uploaded successfully!")

    st.write("Uploaded documents:")
    for pdf in pdf_files:
        st.write(pdf.name)

    selected = st.selectbox("Select project to verify", df["project_id"])

    if st.button("Run Verification"):
        documents = SAMPLE_EXTRACTIONS.get(selected)
        if documents is None:
            st.warning(f"No extraction data available yet for {selected}.")
        else:
            record = df[df["project_id"] == selected].iloc[0].to_dict()
            verification = verify_project(record, documents)
            st.session_state["report"] = assess_project(verification)

report = st.session_state.get("report")

if report:
    st.divider()
    st.header(f"Results for {report['project_id']}")

    st.markdown(f"### Overall: {STATUS_ICONS[report['overall_status']]}")

    cols = st.columns(4)
    for col, (status, count) in zip(cols, report["status_counts"].items()):
        col.metric(status, count)

    st.dataframe(findings_table(report), use_container_width=True)

    st.caption(
        "Supported means no inconsistency was detected in the available "
        "checks. It does not prove the project is genuine."
    )

    st.divider()
    st.header("Reviewer decision")

    decision = st.radio("Decision", DECISIONS)
    justification = st.text_area("Justification")

    if st.button("Save Decision"):
        log = st.session_state.setdefault("decision_log", [])
        log.append({
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Project": report["project_id"],
            "Overall status": report["overall_status"],
            "Decision": decision,
            "Justification": justification,
        })
        st.success("Decision recorded.")

log = st.session_state.get("decision_log")
if log:
    st.subheader("Decision log (this session)")
    st.dataframe(pd.DataFrame(log), use_container_width=True)