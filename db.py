from sqlalchemy import create_engine
import streamlit as st

def get_engine():
    return create_engine(
        f"postgresql://{st.secrets['db_user']}:{st.secrets['db_pass']}@{st.secrets['db_host']}/{st.secrets['db_name']}"
    )
