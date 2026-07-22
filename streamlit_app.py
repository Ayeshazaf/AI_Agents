from __future__ import annotations

import streamlit as st

from pages.crm_page import render_crm_page
from pages.rag_page import render_rag_page
from pages.task_page import render_task_page
from pages.reporting_page import render_reporting_page

st.set_page_config(page_title="AI Banking UI", page_icon="🏦", layout="wide")
st.title("🏦 AI Banking UI")
st.write("Task and CRM dashboards for the banking agents.")

task_tab, crm_tab , rag_tab , reporting_tab= st.tabs(["Task Agent", "CRM Agent", "RAG Agent", "Reporting"])

with task_tab:
    render_task_page()

with crm_tab:
    render_crm_page()

with rag_tab:
    render_rag_page()
    
with reporting_tab:
    render_reporting_page()