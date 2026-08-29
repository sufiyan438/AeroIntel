import sys

from pathlib import Path

# ---------------------------------------------------------
# Add Project Root
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------

import streamlit as st

from app.rag.rag_engine import RAGEngine
from app.ui.sidebar import render_sidebar
from app.upload.uploader import PDFUploader


from app.upload.processor import PDFProcessor

from app.upload.indexer import IndexUpdater


# ---------------------------------------------------------
# Page Config
# ---------------------------------------------------------

st.set_page_config(
    page_title="AeroIntel AI",
    page_icon="✈️",
    layout="wide"
)

# ---------------------------------------------------------
# Load RAG Engine Once
# ---------------------------------------------------------

if "rag" not in st.session_state:

    with st.spinner("Loading AeroIntel AI..."):

        st.session_state.rag = RAGEngine()

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_uploaded" not in st.session_state:
    st.session_state.last_uploaded = None


# =============================
# CALL SIDEBAR HERE
# =============================

top_k, uploaded_pdf, search_scope = render_sidebar()

if (uploaded_pdf is not None
    and uploaded_pdf.name != st.session_state.last_uploaded):

    progress = st.sidebar.progress(
        0,
        text="Uploading PDF..."
    )

    # -----------------------------
    # Save PDF
    # -----------------------------

    uploader = PDFUploader()

    file_path = uploader.save(uploaded_pdf)

    progress.progress(
        25,
        text="PDF uploaded."
    )

    # -----------------------------
    # Process PDF
    # -----------------------------

    processor = PDFProcessor()

    chunks = processor.process(str(file_path))

    progress.progress(
        50,
        text=f"{len(chunks)} chunks created."
    )

    # -----------------------------
    # Update FAISS
    # -----------------------------

    indexer = IndexUpdater()

    added = indexer.update(chunks)

    progress.progress(
        75,
        text=f"{added} chunks indexed."
    )

    # -----------------------------
    # Reload RAG Engine
    # -----------------------------

    st.session_state.rag = RAGEngine()

    progress.progress(
        100,
        text="Knowledge Base Updated!"
    )

    st.sidebar.success(
        "🎉 PDF is ready for querying."
    )

    st.session_state.last_uploaded = uploaded_pdf.name

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("✈️ AeroIntel AI")

st.caption(
    "AI-powered Aviation Investigation Report Assistant"
)

st.divider()

# ---------------------------------------------------------
# Display Previous Messages
# ---------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            if "sources" in message:

                with st.expander("Sources"):

                    shown = set()

                    for doc, score in message["sources"][:top_k]:

                        source = Path(
                            doc.metadata.get(
                                "source",
                                "Unknown"
                            )
                        ).name

                        page = doc.metadata.get(
                            "page",
                            0
                        ) + 1

                        key = (source, page)

                        if key in shown:
                            continue

                        shown.add(key)

                        st.write(
                            f"{source} (Page {page})"
                        )

# ---------------------------------------------------------
# Chat Input
# ---------------------------------------------------------

question = st.chat_input(
    "Ask AeroIntel AI..."
)

# ---------------------------------------------------------
# Ask Question
# ---------------------------------------------------------

if question:

    # -------------------------
    # Show User Message
    # -------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    # -------------------------
    # Generate Response
    # -------------------------

    with st.chat_message("assistant"):

        with st.spinner("Searching aviation reports..."):

            answer, results = st.session_state.rag.ask(
                question=question,
                scope=search_scope
            )

        st.markdown(answer)

        with st.expander("Sources", expanded=False):

            shown = set()

            for doc, score in results[:top_k]:

                source = Path(
                    doc.metadata.get(
                        "source",
                        "Unknown"
                    )
                ).name

                page = doc.metadata.get(
                    "page",
                    0
                ) + 1

                key = (source, page)

                if key in shown:
                    continue

                shown.add(key)

                st.write(
                    f"{source} (Page {page})"
                )

    # -------------------------
    # Save Assistant Response
    # -------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": results
        }
    )

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "© AeroIntel AI | Built with LangChain • FAISS • Groq • Streamlit"
)