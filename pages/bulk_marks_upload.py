import streamlit as st
import pandas as pd
import db_backend.instructor_ops as instructor_ops

if "user_id" not in st.session_state:
    st.rerun()

if st.session_state.role != "instructor":
    st.error("Access denied")
    st.stop()

instructor_id = st.session_state.user_id

st.title("Upload Assignment Marks in Bulk")

#Select the course
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

selected_course = st.selectbox("Course", list(course_options.keys()))
if selected_course:
    offering_id = course_options[selected_course]

    assignment_options = instructor_ops.view_course_assignments(offering_id)

    if not assignment_options:
        st.info("No assignments available for this course")
        st.stop()
    
    assignments_df = pd.DataFrame(assignment_options)
    assignments = {
        f"{row['title']} (ID: {row['assignment_id']})":
        row["assignment_id"]
        for _, row in assignments_df.iterrows()
    }
    selected_assignment = st.selectbox("Assignments", list(assignments.keys()))

    if selected_assignment:
        a_id = assignments[selected_assignment]
        #Upload marks
        st.subheader("Upload Assignment Marks")
        marks_file = st.file_uploader("Upload Excel File", type=["xlsx"], key="marks_upload")

        if marks_file is not None:
            df = pd.read_excel(marks_file)

            required = {
                "student_id",
                "marks_obtained"
            }

            missing = required - set(df.columns)
            if missing:
                st.error(f"Missing columns: {missing}")
                st.stop()

            if df["student_id"].duplicated().any():
                duplicates = (
                    df[df["student_id"].duplicated()]["student_id"].tolist()
                    )
                st.error(f"Duplicates in file: {duplicates}")
                st.stop()
            
            st.dataframe(df)

            if st.button("Upload marks"):
                results = []
                for _, row in df.iterrows():

                    try:
                        _, s_id = instructor_ops.upload_grade(
                            student_id=row["student_id"],
                            assignment_id=a_id,
                            marks_obtained=row["marks_obtained"]
                        )

                        results.append({
                            "Student ID": s_id,
                            "Status": "Success"
                        })
                    
                    except Exception as e:
                        results.append({
                            "Student ID": row["student_id"],
                            "Status": f"Failed: {str(e)}"
                        })
                    
                st.dataframe(pd.DataFrame(results), use_container_width=True)