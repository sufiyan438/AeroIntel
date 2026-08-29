import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("AeroIntel AI")

        st.markdown("---")
        st.subheader("System Status")

        st.success("Backend Loaded")

        st.write("**Vector Store:** Dual FAISS")
        st.write("**Retrieval:** MMR")
        st.write("**Embedding:** all-MiniLM-L6-v2")
        st.write("**LLM:** Llama 3.3 70B (Groq)")

        st.markdown("---")

        st.subheader("Retrieval Settings")

        top_k = st.slider(
            "Top K Documents",
            1, #Minimum
            10, #Maximum
            5 #Default
        )

        search_scope = st.radio(
            "Search Scope",
            [
                "Aviation Database",
                "Uploaded Documents",
                "Both"
            ],
            index=0
        )

        st.markdown("---")

        st.subheader("Upload Investigation Report")

        uploaded_pdf = st.file_uploader(
            "Choose a PDF",
            type=["pdf"]
        )
        st.markdown("---")

        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")

        st.subheader("Project")

        st.write("**Name:** AeroIntel AI")
        st.write("**Version:** v1")
        st.write("**Database:** Dual FAISS")
        st.write("**Retrieval:** MMR Routing")

    return top_k, uploaded_pdf, search_scope