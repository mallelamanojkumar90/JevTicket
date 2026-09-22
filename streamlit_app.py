from __future__ import annotations

import pandas as pd
import streamlit as st

from jev_client import JevClient, JevConfigurationError, JevRequestError
from models import CategoryDecision
from router import RouteResult, route_ticket


DEFAULT_TICKET = "Payment was deducted twice from my account. Please fix this urgently."


def main() -> None:
    st.set_page_config(
        page_title="JevTicket",
        page_icon="J",
        layout="wide",
    )

    st.title("JevTicket")

    ticket_message = st.text_area(
        "Support ticket",
        value=DEFAULT_TICKET,
        height=140,
        max_chars=2000,
    )

    analyze_clicked = st.button("Analyze ticket", type="primary")

    if analyze_clicked:
        if not ticket_message.strip():
            st.warning("Enter a support ticket before analyzing.")
            return

        with st.spinner("Asking Jev..."):
            try:
                decision = JevClient.from_env().analyze_ticket(ticket_message.strip())
            except JevConfigurationError as exc:
                st.error(str(exc))
                st.info("Create a .env file with TYPESAFE_API_KEY=your_key_here, then restart Streamlit.")
                return
            except JevRequestError as exc:
                st.error(f"Jev request failed: {exc}")
                return

        route = route_ticket(decision)
        render_results(decision, route)
    else:
        st.caption("Enter a customer message and run the analysis.")


def render_results(decision: CategoryDecision, route: RouteResult) -> None:
    st.subheader("Ticket Analysis")

    category_col, urgent_col, severity_col, escalation_col = st.columns(4)
    category_col.metric("Category", decision.category.value)
    urgent_col.metric("Urgent", "YES" if decision.is_urgent else "NO")
    severity_col.metric("Severity", f"{decision.severity_display} / 5")
    escalation_col.metric("Escalate", "YES" if route.escalate else "NO")

    route_col, model_col = st.columns(2)
    with route_col:
        st.subheader("Routing Decision")
        st.write(f"**Team:** {route.team}")
        st.write(f"**Queue:** `{route.queue_name}`")
        st.write(route.message)
        if route.escalation_reason:
            st.warning(route.escalation_reason)

    with model_col:
        st.subheader("Jev Response")
        st.write(f"**Model:** `{decision.model}`")
        st.write(f"**Urgency probability:** `{decision.urgent_probability:.4f}`")
        if decision.confidence is not None:
            st.write(f"**Category confidence:** `{decision.confidence:.4f}`")
        if decision.severity_confidence is not None:
            st.write(f"**Severity confidence:** `{decision.severity_confidence:.4f}`")
        if decision.usage_input_tokens is not None:
            st.write(f"**Input tokens:** `{decision.usage_input_tokens}`")
        if decision.usage_output_tokens is not None:
            st.write(f"**Output tokens:** `{decision.usage_output_tokens}`")

    chart_col, severity_chart_col = st.columns(2)
    with chart_col:
        st.subheader("Category Probabilities")
        if decision.probabilities:
            st.bar_chart(
                pd.DataFrame(
                    {
                        "category": [category.value for category in decision.probabilities],
                        "probability": list(decision.probabilities.values()),
                    }
                ).set_index("category")
            )
        else:
            st.caption("No category probabilities returned.")

    with severity_chart_col:
        st.subheader("Severity Probabilities")
        if decision.severity_probabilities:
            st.bar_chart(
                pd.DataFrame(
                    {
                        "severity": [str(level) for level in decision.severity_probabilities],
                        "probability": list(decision.severity_probabilities.values()),
                    }
                ).set_index("severity")
            )
        else:
            st.caption("No severity probabilities returned.")


if __name__ == "__main__":
    main()
