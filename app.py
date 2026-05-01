import streamlit as st

from agent.classifier import classify
from agent.retriever import CorpusRetriever, load_corpus
from agent.response_generator import generate_response

# Load backend
corpus = load_corpus("data")
retriever = CorpusRetriever(corpus)

st.set_page_config(page_title="AI Triage Agent", layout="wide")

# -------- HERO --------
st.markdown("""
<h1 style='text-align:center;'>AI Support Triage Agent</h1>
<p style='text-align:center; color:gray;'>Classification • Retrieval • Response</p>
""", unsafe_allow_html=True)

# -------- FEATURES --------
col1, col2, col3 = st.columns(3)
col1.write("⚡ Fast Classification")
col2.write("📊 Smart Retrieval")
col3.write("🤖 AI Response")

st.markdown("---")

# -------- INPUT --------
st.subheader("Enter Support Ticket")

issue = st.text_area("Issue", placeholder="Describe the issue...")
subject = st.text_input("Subject", placeholder="Short summary")
company = st.text_input("Company (optional)", placeholder="HackerRank / Visa / Claude")

# -------- BUTTON --------
if st.button("Analyze"):

    if not issue.strip():
        st.warning("Please enter an issue")
    else:
        # PROCESS
        result = classify(issue, subject, company)
        docs = retriever.retrieve(issue, result.company)

        should_escalate = len(docs) == 0
        escalation_reason = "No docs found" if should_escalate else ""

        status, response, justification = generate_response(
            issue=issue,
            company=result.company,
            request_type=result.request_type,
            product_area=result.product_area,
            should_escalate=should_escalate,
            escalation_reason=escalation_reason,
            retrieval_results=docs
        )

        # -------- OUTPUT --------
        st.markdown("## 📊 Analysis Overview")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Company", result.company)
        col2.metric("Type", result.request_type)
        col3.metric("Area", result.product_area)
        col4.metric("Status", status)

        st.markdown("---")

        left, right = st.columns([2,1])

        with left:
            st.markdown("### 💬 Response")
            st.success(response)

        with right:
            st.markdown("### 📈 Confidence")
            score = docs[0]["score"] if docs else 0
            st.progress(min(score, 1.0))
            st.caption(f"{score:.3f}")

        st.markdown("---")

        with st.expander("📚 Evidence"):
            for i, d in enumerate(docs, 1):
                st.markdown(f"**{i}. Score: {d['score']}**")
                st.write(d["chunk"][:200] + "...")

        st.markdown("### 🧠 Justification")
        st.info(justification)

# -------- FOOTER --------
st.markdown(
    "<div style='text-align:center; color:gray;'>Built by Divya Shree 🚀</div>",
    unsafe_allow_html=True
)