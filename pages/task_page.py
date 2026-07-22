from __future__ import annotations

import os
from typing import Any

import httpx
import streamlit as st
from shared.logging_config import logger

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _fetch_tasks() -> list[dict[str, Any]]:
    try:
        print(f"Fetching tasks from backend at {API_BASE_URL}/tasks")
        response = httpx.get(f"{API_BASE_URL}/tasks", timeout=100.0)
        response.raise_for_status()
        payload = response.json()
        print(f"Received tasks payload: {payload}")
        return payload if isinstance(payload, list) else []
    except Exception as exc:
        logger.warning("Unable to fetch tasks from backend: %s", exc)
        return []


def _send_task_message(user_message: str) -> str:
    try:
        response = httpx.post(f"{API_BASE_URL}/task-agent/chat", params={"user_message": user_message}, timeout=100.0)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            return str(payload.get("message") or payload.get("assistant_response") or payload)
        return str(payload)
    except Exception as exc:
        logger.warning("Unable to send task message to backend: %s", exc)
        return f"Backend unavailable: {exc}"


def render_task_page() -> None:
    st.title("📝 Task Agent")
    st.write("Manage tasks and chat with the task assistant from one screen.")
    left, right = st.columns([2, 1])

    with left:
        st.subheader("💬 AI Assistant")
        user_message = st.text_input("Type your message here:", key="task_user_message")
        if st.button("Send", key="task_send_button"):
            if user_message.strip():
                st.session_state.task_last_message = user_message
                st.write(f"User: {user_message}")
                assistant_response = _send_task_message(user_message)
                st.session_state.task_last_response = assistant_response
                st.write(assistant_response)
            else:
                st.warning("Please enter a message before sending.")

    with right:
        st.subheader("📋 My Tasks")
        tasks = _fetch_tasks()
        if tasks:
            for task in tasks:
                st.write(
                    f"📝 {task.get('title', 'Untitled')} - Status: {task.get('status', 'unknown')} - Priority: {task.get('priority', 'unknown')}"
                )
        else:
            st.write("No tasks available.")


if __name__ == "__main__":
    st.set_page_config(page_title="Task Agent", page_icon="📝", layout="wide")
    render_task_page()
    st.write("No tasks available.")

        

    
