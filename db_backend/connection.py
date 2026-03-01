#We're using mysql-connector-python for the connections

# db_backend/connection.py
import streamlit as st
import mysql.connector
from mysql.connector import Error

@st.cache_resource #When you get a connection now, it belongs to the streamlit cache. You no longer have to open connections each time, you can use the same one
#This is useful because streamlit executes the whole script each time
def get_connection():

    try:
        conn = mysql.connector.connect(
            host="localhost",          # change if needed
            user="root",               # your mysql username
            password="dbms_manager", # change this
            database="course_management",  # your DB name
            autocommit=False           # important for transactions
        )

        return conn

    except Error as e:
        print("Database connection failed:", e)
        raise
