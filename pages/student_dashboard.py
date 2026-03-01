import streamlit as st
import pandas as pd
import datetime

# Block unauthenticated users
if "user_id" not in st.session_state:
    st.rerun()

# Block admins accidentally entering
if st.session_state.role != "student":
    st.error("Access denied")
    st.stop()

import db_backend.student_ops as student_ops

student_id = st.session_state.user_id

#Logout button
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.title("Student Dashboard")
student = student_ops.fetch_student_profile(student_id)

#Display profile
st.subheader("Profile")

col1, col2 = st.columns(2)
with col1:
    st.write("Name:", student["user_name"])
    st.write("Email:", student["email"])

with col2:
    st.write("Year:", student["student_year"])
    st.write("Major:", student["major"])

#Display the enrolled courses
st.subheader("Enrolled Courses")

enrolled_courses = student_ops.get_enrolled_courses(student_id)

if enrolled_courses:
    df = pd.DataFrame(enrolled_courses)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No enrolled courses")


#Enroll in courses
if "show_enroll" not in st.session_state:
    st.session_state.show_enroll = False

if st.button("Enroll in courses"):
    st.session_state.show_enroll = True

if st.session_state.show_enroll:
    available_courses = student_ops.view_all_courses()

    if available_courses:
        course_df = pd.DataFrame(available_courses)
        st.subheader("Available Courses")
        st.dataframe(course_df, use_container_width=True)
        enrolled_codes = []

        if enrolled_courses:
            enrolled_codes = [c["course_code"] for c in enrolled_courses]

        available_codes = [code for code in course_df["course_code"].tolist() if code not in enrolled_codes]

        if not available_codes:
            st.info("You are already enrolled in all courses.")

        else:
            with st.form("enrollment_form"):
                course_menu = st.selectbox("Choose Course", available_codes)
                semester_input = st.number_input("Semester", min_value=1, step=1)
                submitted = st.form_submit_button("Complete Enrollment")
                if submitted:
                    try:
                        student_ops.enroll_in_course(student_id, course_menu, semester_input, datetime.datetime.now().year)
                        st.success("Enrollment successful!")
                        st.session_state.show_enroll = False
                        st.rerun()

                    except Exception as e:
                        st.error(str(e))

#View assignments for a course
if enrolled_courses:
    st.subheader("Pending Assignments")
    course_codes = [c["course_code"] for c in enrolled_courses]
    selected_course = st.selectbox("Select course", course_codes)

    try:
        assignments = student_ops.get_course_assignments(student_id, selected_course)
        if assignments:
            st.write("Assignments")
            st.dataframe(pd.DataFrame(assignments), use_container_width=True)

        else:
            st.info("No assignments available")

    except Exception as e:
        st.error(str(e))


#Performance summary
st.subheader("Submitted Assignments")
if enrolled_courses:
    course_codes = [c["course_code"] for c in enrolled_courses]
    selected_course = st.selectbox("Select course", course_codes, key="grades_course")

    try:
        grades = student_ops.get_course_submitted_assignments(student_id, selected_course)
        if grades:
            st.write("Submitted Assignments")
            st.dataframe(pd.DataFrame(grades), use_container_width=True)

        else:
            st.info("No assignments submitted")

    except Exception as e:
        st.error(str(e))

#Display grades
if enrolled_courses:
    st.subheader("Final Course Grades")
    try:
        grades = student_ops.get_all_final_grades(student_id)
        if grades:
            st.write("Grades")
            st.dataframe(pd.DataFrame(grades), use_container_width=True)

        else:
            st.info("No grades uploaded yet")

    except Exception as e:
        st.error(str(e))