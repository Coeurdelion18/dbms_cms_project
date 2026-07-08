import streamlit as st
from api_client import post

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
        result = post("/students/signup", {
            "email": email,
            "username": username,
            "password": password,
            "year": int(year),
            "major": major,
        })
        st.session_state.user_id = result["user_id"]
        st.session_state.role = result["role"]
        st.session_state.access_token = result["access_token"]
        st.success("Signup successful")
        st.rerun()

    except Exception as e:
        st.error("Signup failed. Email may already exist.")

st.stop()
