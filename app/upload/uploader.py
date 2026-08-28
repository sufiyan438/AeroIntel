from pathlib import Path

class PDFUploader:
    def __init__(self):
        self.upload_dir = Path("data/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save(self, uploaded_file):
        destination = self.upload_dir / uploaded_file.name
        
        with open(destination, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return destination