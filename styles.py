import streamlit as st

def apply_styles():
    st.markdown(
        """
        <style>
        body { font-family: 'Red Hat Display Pro', sans-serif; }
        .content { text-align: center; }
        .header { font-size: 2em; }
        .step { font-size: 1.2em; }
        .sidebar-image { width: 100%; max-width: 150px; display: block; margin: 0 auto; }
        .sidebar-footer { text-align: center; padding: 10px; }
        </style>
        """,
        unsafe_allow_html=True
    )
