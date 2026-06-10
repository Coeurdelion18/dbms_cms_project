import streamlit as st
import pandas as pd

import db_backend.instructor_ops as instructor_ops

# ---------- ACCESS CONTROL ----------

if "user_id" not in st.session_state:
    st.rerun()

if st.session_state.role != "instructor":
    st.error("Access denied")
    st.stop()

instructor_id = st.session_state.user_id

# ---------- LOGOUT ----------

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.title("Instructor Dashboard")

# ---------- LOAD COURSES ----------

courses = instructor_ops.view_courses(instructor_id)

if not courses:
    st.info("You are not assigned to any course offerings.")
    st.stop()

course_df = pd.DataFrame(courses)

course_options = {
    f"{row['course_code']} ({row['semester']} {row['offering_year']})":
    row["offering_id"]
    for _, row in course_df.iterrows()
}

# ---------- CREATE ASSIGNMENT ----------

st.subheader("Create Assignment")

with st.form("assignment_form"):
    selected_course = st.selectbox(
        "Course",
        list(course_options.keys())
    )

    assignment_title = st.text_input("Assignment Title")
    due_date = st.date_input("Due Date")
    max_marks = st.number_input(
        "Max Marks",
        min_value=1,
        step=1
    )

    submitted = st.form_submit_button("Create Assignment")

    if submitted:
        try:
            offering_id = course_options[selected_course]

            instructor_ops.create_assignment(
                offering_id,
                assignment_title,
                due_date,
                max_marks
            )

            st.success("Assignment created")
            st.rerun()

        except Exception as e:
            st.error(str(e))

# ---------- DELETE ASSIGNMENT ----------

st.subheader("Delete Assignment")

selected_course = st.selectbox(
    "Course",
    list(course_options.keys()),
    key="delete_course"
)

offering_id = course_options[selected_course]

course_assignments = instructor_ops.view_course_assignments(
    offering_id
)

if course_assignments:
    course_delete_df = pd.DataFrame(course_assignments)

    st.dataframe(
        course_delete_df,
        use_container_width=True
    )

    options = {
        f"{a['title']} (ID: {a['assignment_id']})":
        a["assignment_id"]
        for a in course_assignments
    }

    with st.form("delete_assignment_form"):
        selected_label = st.selectbox(
            "Assignment",
            list(options.keys())
        )

        confirm = st.checkbox("Confirm deletion")

        submitted = st.form_submit_button(
            "Confirm Delete"
        )

        if submitted:
            if not confirm:
                st.warning(
                    "Please confirm deletion."
                )
            else:
                try:
                    instructor_ops.delete_assignment(
                        options[selected_label]
                    )

                    st.success(
                        "Assignment deleted successfully."
                    )

                    st.rerun()

                except Exception as e:
                    st.error(str(e))
else:
    st.info(
        "No assignments available for this course offering."
    )

# ---------- UPLOAD GRADES ----------

st.subheader("Upload Assignment Marks")
bulk_marks_button = st.button("Click for bulk upload", key="mass_marks_upload")

if bulk_marks_button:
    st.switch_page("pages/bulk_marks_upload.py")

assignment_course = st.selectbox(
    "Course",
    list(course_options.keys()),
    key="assignment_course"
)

offering_id = course_options[assignment_course]

course_assignments = instructor_ops.view_course_assignments(
    offering_id
)

if course_assignments:
    students = instructor_ops.view_course_roster(
        offering_id
    )

    if not students:
        st.info(
            "No students enrolled in this course offering."
        )

    else:
        student_df = pd.DataFrame(students)
        assignment_df = pd.DataFrame(course_assignments)

        with st.form("upload_grade_form"):

            assignment_options = {
                f"{row['title']} (ID: {row['assignment_id']})":
                row["assignment_id"]
                for _, row in assignment_df.iterrows()
            }

            assignment_id = st.selectbox(
                "Assignment",
                list(assignment_options.keys())
            )

            assignment_id = assignment_options[
                assignment_id
            ]

            student_options = {
                f"{row['user_name']} ({row['email']})":
                row["student_id"]
                for _, row in student_df.iterrows()
            }

            selected_student_label = st.selectbox(
                "Student",
                list(student_options.keys())
            )

            student_id = student_options[
                selected_student_label
            ]

            marks = st.number_input(
                "Marks Obtained",
                min_value=0,
                step=1
            )

            submitted = st.form_submit_button(
                "Upload Grade"
            )

            if submitted:
                try:
                    instructor_ops.upload_grade(
                        student_id,
                        assignment_id,
                        marks
                    )

                    st.success(
                        "Grade uploaded successfully."
                    )

                except Exception as e:
                    st.error(str(e))

else:
    st.info(
        "No assignments available for this course offering."
    )

# ---------- ASSIGN FINAL COURSE GRADE ----------

st.subheader("Assign Final Course Grade")
bulk_grade_upload = st.button("Click for bulk grade upload", key="bulk_grade_upload")
if bulk_grade_upload:
    st.switch_page("pages/bulk_grade_upload.py")
    
selected_course = st.selectbox(
    "Course",
    list(course_options.keys()),
    key="final_grade_course"
)

offering_id = course_options[selected_course]

students = instructor_ops.view_course_roster(
    offering_id
)

if not students:
    st.info(
        "No students enrolled in this course offering."
    )

else:
    student_df = pd.DataFrame(students)

    with st.form("assign_course_grade_form"):

        student_options = {
            f"{row['user_name']} ({row['email']})":
            row["student_id"]
            for _, row in student_df.iterrows()
        }

        selected_student_label = st.selectbox(
            "Student",
            list(student_options.keys())
        )

        student_id = student_options[
            selected_student_label
        ]

        grade = st.text_input(
            "Input Letter Grade"
        )

        submitted = st.form_submit_button(
            "Assign Grade"
        )

        if submitted:
            try:
                instructor_ops.assign_course_grade(
                    student_id,
                    offering_id,
                    grade
                )

                st.success(
                    "Course grade assigned successfully."
                )

            except Exception as e:
                st.error(str(e))