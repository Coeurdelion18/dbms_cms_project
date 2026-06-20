import streamlit as st
import pandas as pd
from api_client import get, post

# ---------- ACCESS CONTROL ----------

if "user_id" not in st.session_state:
    st.rerun()

if st.session_state.role != "instructor":
    st.error("Access denied")
    st.stop()

instructor_id = st.session_state.user_id

# ---------- PAGE ----------

st.title("Upload Final Course Grades in Bulk")

# ---------- COURSE SELECTION ----------

courses = get(f"/instructors/{instructor_id}/courses")

if not courses:
    st.info(
        "You are not assigned to any course offerings."
    )
    st.stop()

course_df = pd.DataFrame(courses)

course_options = {
    f"{row['course_code']} ({row['semester']} {row['offering_year']})":
    row["offering_id"]
    for _, row in course_df.iterrows()
}

selected_course = st.selectbox(
    "Course",
    list(course_options.keys())
)

offering_id = course_options[
    selected_course
]

# ---------- FILE UPLOAD ----------

st.subheader(
    "Upload Final Course Grades"
)

grades_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"],
    key="course_grade_upload"
)

if grades_file is not None:

    df = pd.read_excel(
        grades_file
    )

    required = {
        "student_id",
        "grade"
    }

    missing = (
        required -
        set(df.columns)
    )

    if missing:
        st.error(
            f"Missing columns: {missing}"
        )
        st.stop()

    if df["student_id"].duplicated().any():

        duplicates = (
            df[
                df["student_id"]
                .duplicated()
            ]
            ["student_id"]
            .tolist()
        )

        st.error(
            f"Duplicate student IDs in file: {duplicates}"
        )

        st.stop()

    st.dataframe(
        df,
        use_container_width=True
    )

    if st.button(
        "Upload Final Grades"
    ):

        results = []

        for _, row in df.iterrows():

            try:

                post("/instructors/course-grades", {
                    "student_id": int(row["student_id"]),
                    "offering_id": offering_id,
                    "grade": str(row["grade"]),
                })

                results.append(
                    {
                        "Student ID": row["student_id"],
                        "Grade": row["grade"],
                        "Status": "Success"
                    }
                )

            except Exception as e:

                results.append(
                    {
                        "Student ID": row["student_id"],
                        "Grade": row["grade"],
                        "Status": f"Failed: {str(e)}"
                    }
                )

        st.dataframe(
            pd.DataFrame(results),
            use_container_width=True
        )

        success_count = sum(
            1 for r in results
            if r["Status"] == "Success"
        )

        failure_count = (
            len(results)
            - success_count
        )

        st.success(
            f"Uploaded grades for {success_count} students."
        )

        if failure_count:

            st.warning(
                f"{failure_count} rows failed."
            )
