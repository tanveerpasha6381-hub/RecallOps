import os

import streamlit as st
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

st.set_page_config(
    page_title="RecallOps | Incident Memory",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 RecallOps")
st.subheader("Incident response that remembers what worked.")
st.caption(
    "Hackathon prototype • Synthetic demo data • "
    "Recommendations only—no production actions are executed."
)

api_url = os.getenv("HINDSIGHT_API_URL", "").strip()
api_key = os.getenv("HINDSIGHT_API_KEY", "").strip()
bank_id = os.getenv("HINDSIGHT_BANK_ID", "").strip()

if not all([api_url, api_key, bank_id]):
    st.error("Missing configuration. Check your .env file.")
    st.stop()

with st.sidebar:
    st.header("RecallOps Workspace")
    st.caption("Memory provider")
    st.write("Hindsight")
    st.caption("Configured memory bank")
    st.code(bank_id, language="text")
    st.info(
        "Search past incidents to inspect failed actions, "
        "successful resolutions, and their context."
    )

st.markdown("### Search incident memory")

with st.form("memory_search"):
    query = st.text_area(
        "What would you like to investigate?",
        value=(
            "What failed and what worked when the checkout "
            "service had database connection timeouts?"
        ),
        height=110,
    )
    submitted = st.form_submit_button(
        "Search Hindsight memory",
        type="primary",
    )

if submitted:
    if not query.strip():
        st.warning("Enter a question first.")
    else:
        st.session_state.pop("memory_results", None)

        try:
            with st.spinner("Retrieving incident evidence from Hindsight..."):
                with Hindsight(
                    base_url=api_url,
                    api_key=api_key,
                    timeout=120.0,
                ) as client:
                    response = client.recall(
                        bank_id=bank_id,
                        query=query.strip(),
                        max_tokens=2048,
                    )

                st.session_state["memory_results"] = [
                    memory.text for memory in response.results
                ]

        except Exception as error:
            st.error(
                f"Memory search failed: {type(error).__name__}. "
                "Check your connection and Hindsight configuration."
            )

if "memory_results" in st.session_state:
    results = st.session_state["memory_results"]

    st.markdown("### Retrieved evidence")
    st.caption(
        "These are retrieved memory entries, not confirmed diagnoses "
        "for a new incident."
    )

    if results:
        st.success(f"Retrieved {len(results)} memory entries.")

        for index, text in enumerate(results, start=1):
            with st.container(border=True):
                st.markdown(f"**Evidence {index}**")
                st.write(text)
    else:
        st.warning(
            "No relevant memory was returned. "
            "Try a more specific question about the saved incident."
        )