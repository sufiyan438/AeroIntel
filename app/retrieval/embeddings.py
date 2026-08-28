from langchain_huggingface import HuggingFaceEmbeddings
from app.config.settings import EMBEDDING_MODEL

class EmbeddingModel:
    def __init__(self):
        self.model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    def get_model(self):
        return self.model