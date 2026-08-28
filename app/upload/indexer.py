from pathlib import Path

from langchain_community.vectorstores import FAISS

from app.retrieval.embeddings import EmbeddingModel

class IndexUpdater:
    def __init__(self):
        self.embedding = EmbeddingModel().get_model()
        self.index_path = "data/vector_store/uploaded_index"

    def update(self, documents):
        index_dir = Path(self.index_path)

        #If this is first upload, then create new uploaded index
        if not index_dir.exists():
            db = FAISS.from_documents(documents, self.embedding)
            db.save_local(self.index_path)
            print(f"Created uploaded index with {len(documents)} chunks.")
            return len(documents)

        #if existing index
        db = FAISS.load_local(
            self.index_path, self.embedding, allow_dangerous_deserialization=True
        )

        print("Before:", db.index.ntotal)

        db.add_documents(documents)
        print("After :", db.index.ntotal)

        db.save_local(self.index_path)

        return len(documents)