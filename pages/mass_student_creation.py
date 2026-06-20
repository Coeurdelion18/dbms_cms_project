import streamlit as st
import pandas as pd
from api_client import post

# ---------- ACCESS CONTROL ----------

if "user_id" not in st.session_state:
    st.rerun()

if st.session_state.role != "admin":
    st.error("Access denied")
    st.stop()

admin_id = st.session_state.user_id

st.title("Bulk Upload for Admins")

#Upload student profiles
st.subheader("Upload Student Profiles")

student_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"],
    key="student_upload"
)

if student_file is not None:

    df = pd.read_excel(student_file)

    if df["email"].duplicated().any():

        duplicates = (
            df[df["email"].duplicated()]
            ["email"]
            .tolist()
        )

        st.error(
            f"Duplicate emails in file: {duplicates}"
        )

        st.stop()

    st.dataframe(df)

    required = {
        "name",
        "user_name",
        "student_id",
        "email",
        "password",
        "student_year",
        "major"
    }

    missing = required - set(df.columns)

    if missing:
        st.error(
            f"Missing columns: {missing}"
        )

        st.stop()

    if st.button(
        "Import Students"
    ):

        results = []

        for _, row in df.iterrows():

            try:

                response = post("/admin/students", {
                    "name": row["name"],
                    "user_name": row["user_name"],
                    "student_id": int(row["student_id"]),
                    "email": row["email"],
                    "password": row["password"],
                    "student_year": int(row["student_year"]),
                    "major": row["major"],
                })
                idx = response["student_id"]

                results.append(
                    {
                        "Student ID": idx,
                        "Student Name": row["user_name"],
                        "Status": "Success"
                    }
                )

            except Exception as e:

                results.append(
                    {
                        "Student ID": None,
                        "Student Name": row["user_name"],
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
            f"Imported {success_count} students."
        )

        if failure_count:

            st.warning(
                f"{failure_count} rows failed."
            )
