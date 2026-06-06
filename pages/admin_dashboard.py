import streamlit as st
import pandas as pd

# ---------- ACCESS CONTROL ----------

if "user_id" not in st.session_state:
    st.rerun()

if st.session_state.role != "admin":
    st.error("Access denied")
    st.stop()

import db_backend.admin_ops as admin_ops
import db_backend.student_ops as student_ops

admin_id = st.session_state.user_id


# LOGOUT

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()


st.title("Admin Dashboard")


# CREATE COURSE

st.subheader("Create Course")
with st.form("create_course_form"):
    instructor = st.text_input("Instructor Name")
    course_code = st.text_input("Course Code")
    title = st.text_input("Course Title")
    credits = st.number_input("Credits", min_value=1, step=1)
    submitted = st.form_submit_button("Create Course")

    if submitted:
        try:
            admin_ops.create_course(instructor, course_code, title, credits)
            st.success("Course created successfully")
            st.rerun()

        except Exception as e:
            st.error(str(e))


# VIEW COURSE DETAILS

st.subheader("View Course Details")
courses = student_ops.view_all_courses()
if courses:
    course_df = pd.DataFrame(courses)
    selected_course_for_details = st.selectbox(
        "Select Course",
        course_df["course_code"].tolist(),
        key="course_details_select",
    )

    if st.button("Show Details"):
        try:
            details = admin_ops.get_course_details(selected_course_for_details)
            # Display details in a dataframe for a clean tabular view
            st.dataframe(pd.DataFrame([details]), use_container_width=True)
        except Exception as e:
            st.error(str(e))
else:
    st.info("No courses available yet.")



# VIEW COURSE ROSTER

st.subheader("View Course Roster")

if courses:
    selected_course = st.selectbox("Choose Course", course_df["course_code"].tolist())
    if st.button("Show Roster"):
        try:
            roster = admin_ops.view_course_roster(selected_course)
            if roster:
                st.dataframe(pd.DataFrame(roster), use_container_width=True)
            else:
                st.info("No students enrolled")

        except Exception as e:
            st.error(str(e))