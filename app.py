import streamlit as st
import pandas as pd
import tempfile
import os
from datetime import datetime

from detection import detect_defects
from analytics import get_risk_level, get_recommendation


st.set_page_config(page_title="Quality Inspection Analytics")

st.title("AI-Powered Quality Inspection & Defect Analytics Platform")

st.caption(
    "A computer vision and analytics dashboard for industrial defect detection."
)

st.write("Upload a reference image and a test image for inspection.")


# batch id input
st.sidebar.header("Inspection Controls")
batch_id = st.sidebar.text_input("Batch ID", "B101")


# image uploads
reference_file = st.file_uploader(
    "Upload Reference Image",
    type=["jpg", "jpeg", "png"]
)

test_file = st.file_uploader(
    "Upload Test Image",
    type=["jpg", "jpeg", "png"]
)


# button to run inspection
if st.button("Run Inspection"):

    if reference_file is None or test_file is None:
        st.warning("Please upload both images first.")

    else:
        # create temp files for OpenCV
        temp_ref = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        )

        temp_test = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        )

        temp_ref.write(reference_file.read())
        temp_test.write(test_file.read())

        temp_ref.flush()
        temp_test.flush()

        temp_ref.close()
        temp_test.close()

        # defect detection
        result = detect_defects(
            temp_ref.name,
            temp_test.name
        )

        if "error" in result:
            st.error(result["error"])

        else:
            status = result["status"]
            defect_count = result["defect_count"]
            total_area = result["total_area"]
            severity_score = result["severity_score"]

            risk_level = get_risk_level(severity_score)
            recommendation = get_recommendation(risk_level)

            # KPI cards
            st.subheader("Inspection Metrics")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Defect Count", defect_count)

            with col2:
                st.metric("Defect Area", round(total_area, 2))

            with col3:
                st.metric("Severity Score", severity_score)

            # PASS FAIL result
            st.subheader("Inspection Result")

            if status == "PASS":
                st.success("PASS")
            else:
                st.error("FAIL")

            # risk analysis
            st.subheader("Risk Analysis")
            st.info(f"Risk Level: {risk_level}")

            st.subheader("Recommendation")
            st.warning(recommendation)

            # save inspection history
            history_file = "inspection_history.csv"

            new_row = pd.DataFrame([{
                "date": datetime.now().strftime("%Y-%m-%d"),
                "batch_id": batch_id,
                "defect_count": defect_count,
                "total_area": total_area,
                "severity_score": severity_score,
                "status": status
            }])

            if os.path.exists(history_file):
                existing_data = pd.read_csv(history_file)

                updated_data = pd.concat(
                    [existing_data, new_row],
                    ignore_index=True
                )

                updated_data.to_csv(
                    history_file,
                    index=False
                )
            else:
                new_row.to_csv(
                    history_file,
                    index=False
                )

            # processed image
            st.subheader("Processed Image")
            st.image(
                result["processed_image"],
                channels="BGR"
            )
# analytics dashboard
history_file = "inspection_history.csv"

if os.path.exists(history_file):

    history_df = pd.read_csv(history_file)

    if len(history_df) > 0:

        st.markdown("---")
        st.header("Inspection Analytics Dashboard")

        total_inspections = len(history_df)

        pass_count = len(
            history_df[
                history_df["status"] == "PASS"
            ]
        )

        fail_count = total_inspections - pass_count

        pass_rate = (pass_count / total_inspections) * 100
        failure_rate = (fail_count / total_inspections) * 100

        avg_severity = history_df[
            "severity_score"
        ].mean()

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.metric("Total Inspections", total_inspections)

        with k2:
            st.metric("Pass Rate", f"{pass_rate:.2f}%")

        with k3:
            st.metric("Failure Rate", f"{failure_rate:.2f}%")

        with k4:
            st.metric("Avg Severity", f"{avg_severity:.2f}")

        st.subheader("Inspection History")
        st.dataframe(history_df)

        st.subheader("Defects by Batch")

        batch_defects = history_df.groupby(
            "batch_id"
        )["defect_count"].sum()

        st.bar_chart(batch_defects)

        st.subheader("Severity Trend")
        st.line_chart(
            history_df["severity_score"]
        )
        worst_batch = history_df.groupby(
            "batch_id"
        )["defect_count"].sum().idxmax()

        highest_defects = history_df.groupby(
            "batch_id"
        )["defect_count"].sum().max()

        st.subheader("Business Insights")

        st.info(
            f"Batch {worst_batch} has highest defects "
            f"({highest_defects}). Immediate quality review recommended."
        )