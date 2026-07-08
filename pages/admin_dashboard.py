import streamlit as st
import pandas as pd
from api_client import get, post

# ---------- ACCESS CONTROL ----------

if "user_id" not in st.session_state or "access_token" not in st.session_state:
    st.rerun()

if st.session_state.role != "admin":
    st.error("Access denied")
    st.stop()

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
            post("/admin/instructors", {
                "user_name": instructor_username,
                "email": instructor_email,
                "password": instructor_password,
                "instructor_name": instructor_name,
            })
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
    student_year = st.number_input("Student Year of Entry", step=1)
    student_major = st.text_input("Student Major")
    student_username = st.text_input("Student Username")
    student_email = st.text_input("Student Email")
    student_password = st.text_input("Student Password")
    submit_student = st.form_submit_button("Create Student Profile")

    if submit_student:
        try:
            post("/admin/students", {
                "name": student_name,
                "user_name": student_username,
                "email": student_email,
                "password": student_password,
                "student_year": int(student_year),
                "major": student_major,
            })
            st.success("Student profile created successfully")
            st.rerun()

        except Exception as e:
            st.error(str(e))

# CREATE COURSE

st.subheader("Create Course")
with st.form("create_course_form"):
    course_code = st.text_input("Course Code")
    title = st.text_input("Course Title")
    credits = st.number_input("Credits", min_value=1, step=1)
    submitted = st.form_submit_button("Create Course")

    if submitted:
        try:
            post("/admin/courses", {
                "course_code": course_code,
                "title": title,
                "credits": int(credits),
            })
            st.success("Course created successfully")
            st.rerun()

        except Exception as e:
            st.error(str(e))

# UPDATE COURSE

# VIEW COURSE DETAILS

st.subheader("View Course Details")
courses = get("/admin/offerings")
if courses:
    course_df = pd.DataFrame(courses)
    course_options = {
        f"{row['course_code']} ({row['semester']} {row['offering_year']})": row["offering_id"]
        for _, row in course_df.iterrows()
    }
    selected_course_for_details = st.selectbox(
        "Select Course",
        list(course_options.keys()),
        key="course_details_select",
    )

    if st.button("Show Details"):
        try:
            details = get(f"/admin/offerings/{course_options[selected_course_for_details]}")
            # Display details in a dataframe for a clean tabular view
            st.dataframe(pd.DataFrame([details]), use_container_width=True)
        except Exception as e:
            st.error(str(e))
else:
    st.info("No courses available yet.")



# VIEW COURSE ROSTER

st.subheader("View Course Roster")

if courses:
    selected_course = st.selectbox("Choose Course", list(course_options.keys()))
    if st.button("Show Roster"):
        try:
            roster = get(f"/admin/offerings/{course_options[selected_course]}/roster")
            if roster:
                st.dataframe(pd.DataFrame(roster), use_container_width=True)
            else:
                st.info("No students enrolled")

        except Exception as e:
            st.error(str(e))
