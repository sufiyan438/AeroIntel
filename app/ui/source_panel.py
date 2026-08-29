import streamlit as st
from pathlib import Path

def show_sources(results):

    with st.expander("Sources", expanded=True):

        shown = set()

        for doc, _ in results:

            source = Path(
                doc.metadata["source"]
            ).name

            page = doc.metadata["page"] + 1

            key = (source, page)

            if key in shown:
                continue

            shown.add(key)

            st.write(f"{source} (Page {page})")