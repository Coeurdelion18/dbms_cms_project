import streamlit as st
import pandas as pd
import db_backend.admin_ops as admin_ops

# ---------- ACCESS CONTROL ----------

if "user_id" not in st.session_state:
    st.rerun()

if st.session_state.role != "admin":
    st.error("Access denied")
    st.stop()

admin_id = st.session_state.user_id

st.title("Bulk Upload for Admins")

#Upload instructor profiles
st.subheader("Upload Instructor Profiles")
instructor_file = st.file_uploader("Upload Excel File", type=["xlsx"], key="instructor_upload")

if instructor_file is not None:
    df = pd.read_excel(instructor_file)

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
        "instructor_name",
        "user_name",
        "email",
        "password"
    }
    
    missing = required - set(df.columns)
    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    if st.button("Import Instructors"):

        results = []

        for _, row in df.iterrows():

            try:
                idx = admin_ops.create_instructor_account(
                    user_name=row["user_name"],
                    email=row["email"],
                    password=row["password"],
                    instructor_name=row["instructor_name"]
                )

                results.append({
                    "Instructor ID": idx,
                    "Instructor Name": row["instructor_name"],
                    "Status": "Success"
                })

            except Exception as e:

                results.append({
                    "Instructor ID": None,
                    "Instructor Name": row["instructor_name"],
                    "Status": f"Failed: {str(e)}"
                })

        st.dataframe(
            pd.DataFrame(results),
            use_container_width=True
        )

        success_count = sum(
            1 for r in results
            if r["Status"] == "Success"
        )

        failure_count = len(results) - success_count

        st.success(
            f"Imported {success_count} instructors."
        )

        if failure_count:
            st.warning(
                f"{failure_count} rows failed."
            )