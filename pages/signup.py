import streamlit as st
from db_backend.auth_ops import create_user
from db_backend.student_ops import create_student_record

if "user_id" in st.session_state:
    st.rerun()

st.title("CMS Student Sign Up")

email = st.text_input("Email")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
year = st.number_input("Year", min_value=1, step=1)
major = st.text_input("Major")

if st.button("Sign Up"):

    try:
        result = create_user(email, username, password, role="student")
        create_student_record(
            result["user_id"],
            year,
            major
        )
        st.session_state.user_id = result["user_id"]
        st.session_state.role = result["role"]
        st.success("Signup successful")
        st.rerun()

    except Exception as e:
        st.error("Signup failed. Email may already exist.")

st.stop()