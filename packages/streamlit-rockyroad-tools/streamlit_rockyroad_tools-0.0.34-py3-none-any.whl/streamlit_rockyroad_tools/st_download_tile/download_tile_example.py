import streamlit as st
import sys
import os

# Ensure package import works when running example directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_rockyroad_tools import st_download_tile

st.set_page_config(page_title="Download Tile Example")

st.markdown("## st_download_tile example")

if 'clicked' not in st.session_state:
    st.session_state.clicked = False


def on_click_handler(name: str):
    st.session_state.clicked = True
    st.toast(f"Download clicked by {name}")

res = st_download_tile(
    title="Dealer Parts Price and Availability",
    body="Click to download the latest report.",
    url="/fake/report.csv",
    key="dl1",
    on_click=on_click_handler,
    args=["Alice"],
)

st.write("Return value:", res)

if st.session_state.clicked:
    st.success("You clicked the download tile!")
