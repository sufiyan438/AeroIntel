import fitz

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import CHUNK_OVERLAP, CHUNK_SIZE

class PDFProcessor:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    def process(self, pdf_path):
        docs = []
        pdf = fitz.open(pdf_path)

        for page_no, page in enumerate(pdf):
            text = page.get_text()
            docs.append(Document(
                page_content=text,
                metadata={
                    "source": pdf_path,
                    "page": page_no
                }
            ))

        chunks = self.splitter.split_documents(docs)
        return chunks