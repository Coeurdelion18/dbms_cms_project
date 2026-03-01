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


# ---------- LOGOUT ----------

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()


st.title("Admin Dashboard")


# ---------- CREATE COURSE ----------

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


# ---------- VIEW COURSE DETAILS ----------

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


# ---------- CREATE ASSIGNMENT ----------

st.subheader("Create Assignment")
courses = student_ops.view_all_courses()
if courses:
    course_df = pd.DataFrame(courses)
    with st.form("assignment_form"):
        selected_course = st.selectbox("Course", course_df["course_code"].tolist())
        assignment_title = st.text_input("Assignment Title")
        due_date = st.date_input("Due Date")
        max_marks = st.number_input("Max Marks", min_value=1, step=1)
        submitted = st.form_submit_button("Create Assignment")

        if submitted:
            try:
                admin_ops.create_assignment(selected_course, assignment_title, due_date, max_marks)
                st.success("Assignment created")
                st.rerun()

            except Exception as e:
                st.error(str(e))


# DELETE ASSIGNMENT
st.subheader("Delete Assignment")

selected_course = st.selectbox("Course", course_df["course_code"].tolist())

course_assignments = admin_ops.view_course_assignments(selected_course)

if course_assignments:
    course_delete_df = pd.DataFrame(course_assignments)
    st.subheader("Select assignment to delete")
    st.dataframe(course_delete_df, use_container_width=True)
    options = {
        f"{a['title']} (ID: {a['assignment_id']})": a["assignment_id"]
        for a in course_assignments
    }
    with st.form("delete_assignment_form"):
        selected_label = st.selectbox("Assignment", list(options.keys()))
        confirm = st.checkbox("Confirm deletion")
        submitted = st.form_submit_button("Confirm Delete")
        if submitted:
            if not confirm:
                st.warning("Please confirm deletion.")

            else:
                try:
                    admin_ops.delete_assignment(options[selected_label])
                    st.success("Assignment deleted successfully.")
                    st.rerun()

                except Exception as e:
                    st.error(str(e))

else:
    st.info("No assignments available for this course.")



# ---------- UPLOAD GRADES ----------

st.subheader("Upload Assignment Marks")

assignment_course = st.selectbox("Course", course_df["course_code"].tolist(), key="assignment_course")
course_assignments = admin_ops.view_course_assignments(assignment_course)

if course_assignments:
    students = admin_ops.view_course_roster(assignment_course)
    if not students:
        st.info("No students enrolled in this course.")
    else:
        student_df = pd.DataFrame(students)
        assignment_df = pd.DataFrame(course_assignments)

        st.subheader("Select assignment to upload grades for")
        with st.form("upload_grade_form"):
            assignment_options = {
                f"{row['title']} (ID: {row['assignment_id']})": row["assignment_id"]
                for _, row in assignment_df.iterrows()
            }
            
            assignment_id = st.selectbox(
                "Assignment",
                list(assignment_options.keys())
            )
            assignment_id = assignment_options[assignment_id]

            student_options = {
                f"{row['user_name']} ({row['email']})": row["student_id"]
                for _, row in student_df.iterrows()
            }

            selected_student_label = st.selectbox(
                "Student",
                list(student_options.keys())
            )
            student_id = student_options[selected_student_label]

            marks = st.number_input("Marks Obtained", min_value=0, step=1)
            submitted = st.form_submit_button("Upload Grade")

            if submitted:
                try:
                    admin_ops.upload_grade(student_id, assignment_id, marks)
                    st.success("Grade uploaded")
                    
                except Exception as e:
                    st.error(str(e))
else:
    st.info("No assignments available for this course.")


# ---------- ASSIGN COURSE GRADE ----------

st.subheader("Assign Final Course Grade")
all_courses = st.selectbox("Course", course_df["course_code"].tolist(), key="all_courses")
if all_courses:
    students = admin_ops.view_course_roster(all_courses)
    if not students:
        st.info("No students enrolled in this course.")
    else:
        student_df = pd.DataFrame(students)
        course_df = pd.DataFrame(courses)
        st.subheader("Select student to assign course grade")
        with st.form("assign_course_grade_form"):
            student_options = {
                f"{row['user_name']} ({row['email']})": row["student_id"]
                for _, row in student_df.iterrows()
            }
            
            selected_student_label = st.selectbox(
                "Student",
                list(student_options.keys())
            )
            student_id = student_options[selected_student_label]
            
            grade = st.text_input("Input Letter Grade")
            submitted = st.form_submit_button("Assign Grade")
            
            if submitted:
                try:
                    admin_ops.assign_course_grade(student_id, all_courses, grade)
                    st.success("Course grade assigned")
                    
                except Exception as e:
                    st.error(str(e))


# ---------- VIEW COURSE ROSTER ----------

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