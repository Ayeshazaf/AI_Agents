from __future__ import annotations

import os
from typing import Any

import httpx
import streamlit as st
from shared.logging_config import logger

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _upload_file(file) -> str:
    try:
        files = {"file": (file.name, file.getvalue())}
        response = httpx.post(f"{API_BASE_URL}/rag-agent/upload", files=files, timeout=100.0)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            return str(payload.get("message") or payload.get("assistant_response") or payload)
        return str(payload)
    except Exception as exc:
        logger.warning("Unable to upload file to backend: %s", exc)
        return f"Backend unavailable: {exc}"



def _fetch_rag_data() -> list[dict[str, Any]]:
    try:
        response = httpx.get(f"{API_BASE_URL}/rag", timeout=100.0)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, list) else []
    except Exception as exc:
        logger.warning("Unable to fetch RAG data from backend: %s", exc)
        return []
    
def _send_rag_message(user_message: str) -> str:
    try:
        response = httpx.post(f"{API_BASE_URL}/rag-agent/chat", json={"user_message": user_message}, timeout=100.0)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            return str(payload.get("message") or payload.get("assistant_response") or payload)
        return str(payload)
    except Exception as exc:
        logger.warning("Unable to send RAG message to backend: %s", exc)
        return f"Backend unavailable: {exc}"
    
def render_rag_page() -> None:
    st.title("📚 RAG Agent")
    st.write("Retrieve information and chat with the RAG assistant from one screen.")
    left, right = st.columns([2, 1])

    with left:
        st.subheader("💬 AI Assistant")
        user_message = st.text_input("Type your message here:", key="rag_user_message")
        if st.button("Send", key="rag_send_button"):
            if user_message.strip():
                st.session_state.rag_last_message = user_message
                st.write(f"User: {user_message}")
                assistant_response = _send_rag_message(user_message)
                st.session_state.rag_last_response = assistant_response
                st.write(assistant_response)
            else:
                st.warning("Please enter a message before sending.")

    with right:
        st.subheader("📋 RAG Data")
        rag_data = _upload_file(st.file_uploader("Upload a file for RAG processing", type=["txt", "pdf", "docx"]))
        if rag_data:
            for item in rag_data:
                st.write(item)
                
if __name__ == "__main__":
    st.set_page_config(page_title="RAG Agent", page_icon="📚", layout="wide")
    render_rag_page()
    st.write("This page allows you to upload files for RAG processing and chat with the RAG assistant.")