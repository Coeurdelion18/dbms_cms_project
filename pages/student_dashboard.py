import streamlit as st
import pandas as pd
import os 

# Block unauthenticated users
if "user_id" not in st.session_state:
    st.rerun()

# Block admins accidentally entering
if st.session_state.role != "student":
    st.error("Access denied")
    st.stop()

import db_backend.student_ops as student_ops

UPLOAD_DIR = "uploads"
student_id = st.session_state.user_id

# Logout button
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.title("Student Dashboard")

student = student_ops.fetch_student_profile(student_id)

# Display profile
st.subheader("Profile")

col1, col2 = st.columns(2)

with col1:
    st.write("Name:", student["user_name"])
    st.write("Email:", student["email"])

with col2:
    st.write("Year:", student["student_year"])
    st.write("Major:", student["major"])

# Display enrolled courses
st.subheader("Enrolled Courses")

enrolled_courses = student_ops.get_enrolled_courses(
    student_id
)

if enrolled_courses:
    df = pd.DataFrame(enrolled_courses)
    st.dataframe(df, use_container_width=True)

else:
    st.info("No enrolled courses")

# Enroll in courses
if "show_enroll" not in st.session_state:
    st.session_state.show_enroll = False

if st.button("Enroll in courses"):
    st.session_state.show_enroll = True

if st.session_state.show_enroll:

    available_courses = (
        student_ops.view_all_courses()
    )

    if available_courses:

        course_df = pd.DataFrame(
            available_courses
        )

        st.subheader(
            "Available Course Offerings"
        )

        st.dataframe(
            course_df,
            use_container_width=True
        )

        enrolled_offerings = []

        if enrolled_courses:
            enrolled_offerings = [
                c["offering_id"]
                for c in enrolled_courses
            ]

        available_offerings = course_df[
            ~course_df["offering_id"].isin(
                enrolled_offerings
            )
        ]

        if available_offerings.empty:

            st.info(
                "You are already enrolled in all course offerings."
            )

        else:

            offering_options = {
                f"{row['course_code']} ({row['semester']} {row['offering_year']})":
                row["offering_id"]
                for _, row in available_offerings.iterrows()
            }

            with st.form("enrollment_form"):

                selected_offering = (
                    st.selectbox(
                        "Choose Course Offering",
                        list(
                            offering_options.keys()
                        )
                    )
                )

                submitted = (
                    st.form_submit_button(
                        "Complete Enrollment"
                    )
                )

                if submitted:

                    try:

                        offering_id = (
                            offering_options[
                                selected_offering
                            ]
                        )

                        student_ops.enroll_in_course(
                            student_id,
                            offering_id
                        )

                        st.success(
                            "Enrollment successful!"
                        )

                        st.session_state.show_enroll = False

                        st.rerun()

                    except Exception as e:
                        st.error(str(e))

# Pending assignments
if enrolled_courses:

    st.subheader(
        "Pending Assignments"
    )

    course_options = {
        f"{c['course_code']} ({c['semester']} {c['offering_year']})":
        c["offering_id"]
        for c in enrolled_courses
    }

    selected_course = st.selectbox(
        "Select course",
        list(course_options.keys()),
        key="pending_assignments"
    )

    offering_id = course_options[
        selected_course
    ]

    try:

        assignments = (
            student_ops.get_course_assignments(
                student_id,
                offering_id
            )
        )

        if assignments:

            st.write("Assignments")

            # st.dataframe(
            #     pd.DataFrame(assignments),
            #     use_container_width=True
            # )
            assignments_df = pd.DataFrame(assignments)
            c1, c2, c3, c4 = st.columns([3,2,1,2])
            c1.write("Title")
            c2.write("Due Date")
            c3.write("Max Marks")
            c4.write("Upload Assignment")

            for idx, row in assignments_df.iterrows():
                c1, c2, c3, c4 = st.columns([3,2,1,2])
                c1.write(row["title"])
                c2.write(row["due_date"])
                c3.write(row["max_marks"])
                submission = c4.file_uploader("Upload Submission", key=f"assignment_upload_{idx}")
                #Add file upload functionality

                if submission is not None:
                    filename = f"{student_id}_{row['assignment_id']}.pdf"
                    filepath = os.path.join(UPLOAD_DIR, filename)

                    with open(filepath, 'wb') as f:
                        f.write(submission.getbuffer())
                    
                    st.success(f"Uploaded {submission.name}")
                    student_ops.upload_assignment_submission(student_id, row['assignment_id'], filepath)

        else:
            st.info(
                "No assignments available"
            )

    except Exception as e:
        st.error(str(e))

# Submitted assignments
st.subheader(
    "Submitted Assignments"
)

if enrolled_courses:

    course_options = {
        f"{c['course_code']} ({c['semester']} {c['offering_year']})":
        c["offering_id"]
        for c in enrolled_courses
    }

    selected_course = st.selectbox(
        "Select course",
        list(course_options.keys()),
        key="grades_course"
    )

    offering_id = course_options[
        selected_course
    ]

    try:

        grades = (
            student_ops.get_course_submitted_assignments(
                student_id,
                offering_id
            )
        )

        if grades:

            st.write(
                "Submitted Assignments"
            )

            st.dataframe(
                pd.DataFrame(grades),
                use_container_width=True
            )

        else:
            st.info(
                "No assignments submitted"
            )

    except Exception as e:
        st.error(str(e))

# Final grades
if enrolled_courses:

    st.subheader(
        "Final Course Grades"
    )

    try:

        grades = (
            student_ops.get_all_final_grades(
                student_id
            )
        )

        if grades:

            st.write("Grades")

            st.dataframe(
                pd.DataFrame(grades),
                use_container_width=True
            )

        else:
            st.info(
                "No grades uploaded yet"
            )

    except Exception as e:
        st.error(str(e))