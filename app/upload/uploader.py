# from pathlib import Path

# class PDFUploader:
#     def __init__(self):
#         self.upload_dir = Path("data/uploads")
#         self.upload_dir.mkdir(parents=True, exist_ok=True)

#     def save(self, uploaded_file):
#         destination = self.upload_dir / uploaded_file.name
        
#         with open(destination, "wb") as f:
#             f.write(uploaded_file.getbuffer())

#         return destination


from pathlib import Path
import hashlib
import json


class PDFUploader:

    def __init__(self):
        self.upload_dir = Path("data/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.registry_path = self.upload_dir / "indexed_files.json"

    def get_hash(self, uploaded_file):
        file_bytes = uploaded_file.getbuffer()

        return hashlib.sha256(file_bytes).hexdigest()

    def is_indexed(self, file_hash):
        registry = self._load_registry()

        return file_hash in registry.values()

    def save(self, uploaded_file):
        destination = self.upload_dir / uploaded_file.name

        with open(destination, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return destination

    def mark_indexed(self, filename, file_hash):
        registry = self._load_registry()

        registry[filename] = file_hash

        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

    def _load_registry(self):
        if not self.registry_path.exists():
            return {}

        with open(self.registry_path, "r", encoding="utf-8") as f:
            return json.load(f)