from __future__ import annotations

import streamlit as st

from pages.crm_page import render_crm_page
from pages.task_page import render_task_page


st.set_page_config(page_title="AI Banking UI", page_icon="🏦", layout="wide")
st.title("🏦 AI Banking UI")
st.write("Task and CRM dashboards for the banking agents.")

task_tab, crm_tab = st.tabs(["Task Agent", "CRM Agent"])

with task_tab:
    render_task_page()

with crm_tab:
    render_crm_page()