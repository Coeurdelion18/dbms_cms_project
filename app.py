import streamlit as st
from db_backend.auth_ops import authenticate_user

if "user_id" not in st.session_state:
    st.title("Course Management Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            result = authenticate_user(email, password)

            if result:
                st.session_state.user_id = result["user_id"]
                st.session_state.role = result["role"]
                st.success("Login successful")
                st.rerun()

            else:
                st.error("Invalid credentials")
    with col2:
        if st.button("Sign Up"):
            st.switch_page("pages/signup.py")

    st.stop()


student_pages = [
    st.Page("pages/student_dashboard.py", title="Dashboard"),
    # st.Page("pages/student_courses.py", title="Courses"),
    # st.Page("pages/student_grades.py", title="Grades"),
]

admin_pages = [
    st.Page("pages/admin_dashboard.py", title="Admin Dashboard"),
    # st.Page("pages/admin_courses.py", title="Courses"),
    # st.Page("pages/admin_assignments.py", title="Assignments"),
    # st.Page("pages/admin_grades.py", title="Upload Grades"),
]


role = st.session_state.get("role")
if role == "student":
    nav = st.navigation(student_pages)

else:
    nav = st.navigation(admin_pages)

nav.run()