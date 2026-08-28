from pathlib import Path

from app.upload.processor import PDFProcessor
from app.retrieval.vector_store import VectorStore


class KnowledgeBaseBuilder:
    def __init__(self):
        self.processor = PDFProcessor()
        self.vector_store = VectorStore()
        self.raw_folder = Path("data/raw")


    def rebuild(self):
        all_chunks = []
        total_pdfs = 0

        for pdf in self.raw_folder.rglob("*.pdf"):
            print(f"Processing {pdf.name}")
            chunks = self.processor.process(str(pdf))
            all_chunks.extend(chunks) #Appending new chunks to list
            total_pdfs += 1


        self.vector_store.rebuild(all_chunks)

        return total_pdfs, len(all_chunks)