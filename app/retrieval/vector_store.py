import shutil

from pathlib import Path
from langchain_community.vectorstores import FAISS
from app.retrieval.embeddings import EmbeddingModel

class VectorStore:
    def __init__(self):
        self.embedding = EmbeddingModel().get_model()
        self.aviation_path = "data/vector_store/aviation_index"
        self.upload_path = "data/vector_store/uploaded_index"

    def create(self, documents):
        return FAISS.from_documents(documents, self.embedding)

    def save(self, vectorstore, path=None):
        if path is None:
            path = self.aviation_path

        Path(path).mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(path)

    def load(self, path=None):
        if path is None:
            path = self.aviation_path

        return FAISS.load_local(path, self.embedding, allow_dangerous_deserialization=True)

    def load_aviation(self):
        return self.load(self.aviation_path)

    def load_uploaded(self):
        index_file = Path(self.upload_path) / "index.faiss"
        pkl_file = Path(self.upload_path) / "index.pkl"

        if not index_file.exists() or not pkl_file.exists():
            print("Creating uploaded FAISS store")
            dummy = FAISS.from_texts(["Temporary document"], self.embedding)
            dummy.save_local(self.upload_path)

        return self.load(self.upload_path)

    def rebuild(self, documents, path=None):
        if path is None:
            path = self.aviation_path

        path = Path(path)

        if path.exists():
            shutil.rmtree(path)

        vectorstore = FAISS.from_documents(documents, self.embedding)
        vectorstore.save_local(path)
        return vectorstore