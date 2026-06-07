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

# CREATE INSTRUCTOR PROFILE

st.subheader("Create Instructor Profile")
mass_instructor_button = st.button("Click for bulk upload", key="bulk_instructor_button")

if mass_instructor_button:
    st.switch_page("pages/mass_instructor_creation.py")

with st.form("create_instructor_form"):
    instructor_name = st.text_input("Instructor Name")
    instructor_username = st.text_input("Instructor Username")
    instructor_email = st.text_input("Instructor Email")
    instructor_password = st.text_input("Temporary Password")
    submit_instructor = st.form_submit_button("Create Instructor Profile")

    if submit_instructor:
        try:
            admin_ops.create_instructor_account(
                instructor_username, 
                instructor_email,
                instructor_password,
                instructor_name 
            )
            st.success("Instructor profile created successfully")
            st.rerun()
        
        except Exception as e:
            st.error(str(e))

# CREATE STUDENT PROFILE

st.subheader("Create Student Profile")
mass_student_button = st.button("Click for bulk upload", key="bulk_student_button")

if mass_student_button:
    st.switch_page("pages/mass_student_creation.py")

with st.form("create_student_form"):
    student_name = st.text_input("Student Name")
    student_id = st.text_input("Student ID")
    student_year = st.number_input("Student Year of Entry", step=1)
    student_major = st.text_input("Student Major")
    student_username = st.text_input("Student Username")
    student_email = st.text_input("Student Email")
    student_password = st.text_input("Student Password")
    submit_student = st.form_submit_button("Create Student Profile")

    if submit_student:
        try:
            admin_ops.create_student_account(
                student_name,
                student_username,
                student_id, 
                student_email,
                student_password,
                student_year,
                student_major 
            )
            st.success("Student profile created successfully")
            st.rerun()
        
        except Exception as e:
            st.error(str(e))

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

# UPDATE COURSE

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