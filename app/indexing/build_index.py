from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader

from app.retrieval.chunker import DocumentChunker
from app.retrieval.vector_store import VectorStore

class IndexBuilder:
    def __init__(self):
        self.vectorstore = VectorStore()
        self.chunker = DocumentChunker()

    def build(self, data_folder="data/raw"):
        documents = []
        pdf_files = list(Path(data_folder).rglob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF(s).")

        for pdf in pdf_files:
            loader = PyMuPDFLoader(str(pdf))
            docs = loader.load()
            documents.extend(docs)

        print(f"Loaded {len(documents)} documents pages.")

        chunks = self.chunker.split(documents)
        print(f"Created {len(chunks)} chunks.")

        vector_db = self.vectorstore.create(chunks)
        self.vectorstore.save(vector_db)
        print("FAISS index created successfully!")