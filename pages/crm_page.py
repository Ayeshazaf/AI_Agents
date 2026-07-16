from __future__ import annotations

import os
from typing import Any

import httpx
import streamlit as st

from shared.logging_config import logger

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _fetch_customers() -> list[dict[str, Any]]:
    try:
        response = httpx.get(f"{API_BASE_URL}/customers", timeout=100.0)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, list) else []
    except Exception as exc:
        logger.warning("Unable to fetch customers from backend: %s", exc)
        return []


def _fetch_complaints() -> list[dict[str, Any]]:
    try:
        response = httpx.get(f"{API_BASE_URL}/complaints", timeout=100.0)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, list) else []
    except Exception as exc:
        logger.warning("Unable to fetch complaints from backend: %s", exc)
        return []


def _send_crm_message(session_id: str, customer_id: int, user_message: str) -> str:
    try:
        response = httpx.post(
            f"{API_BASE_URL}/crm/chat/",
            params={"session_id": session_id, "customer_id": customer_id, "user_message": user_message},
            timeout=100.0,
        )
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            return str(payload.get("assistant_response") or payload.get("message") or payload)
        return str(payload)
    except Exception as exc:
        logger.warning("Unable to send CRM message to backend: %s", exc)
        return f"Backend unavailable: {exc}"


def render_crm_page() -> None:
    st.title("📣 CRM Agent")
    st.write("Handle customer conversations, complaints, and CRM operations from one screen.")

    left, right = st.columns([2, 1])

    with left:
        st.subheader("💬 CRM Assistant")
        session_id = st.text_input("Session ID", value=st.session_state.get("crm_session_id", "crm-demo-session"), key="crm_session_id")
        customer_id = st.number_input("Customer ID", min_value=1, value=int(st.session_state.get("crm_customer_id", 1)), step=1, key="crm_customer_id")
        user_message = st.text_area("Type your CRM message here:", key="crm_user_message", height=120)
        if st.button("Send", key="crm_send_button"):
            if user_message.strip():
                st.session_state.crm_last_message = user_message
                st.write(f"User: {user_message}")
                assistant_response = _send_crm_message(session_id, int(customer_id), user_message)
                st.session_state.crm_last_response = assistant_response
                st.write(assistant_response)
            else:
                st.warning("Please enter a message before sending.")

    with right:
        st.subheader("👥 Customers")
        customers = _fetch_customers()
        if customers:
            for customer in customers:
                st.write(f"👤 {customer.get('name', 'Unknown')} - Account {customer.get('account_id', '-')}")
        else:
            st.write("No customers available.")

        st.subheader("🧾 Complaints")
        complaints = _fetch_complaints()
        if complaints:
            for complaint in complaints:
                st.write(
                    f"⚠️ #{complaint.get('id', '-')}: {complaint.get('description', 'No description')} - {complaint.get('status', 'unknown')}"
                )
        else:
            st.write("No complaints available.")


if __name__ == "__main__":
    st.set_page_config(page_title="CRM Agent", page_icon="📣", layout="wide")
    render_crm_page()