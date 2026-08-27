import re
import os
import fitz

class MetadataExtractor:
    """
    Extract metadata from a PDF document.
    """

    def extract(self, pdf: fitz.Document, file_path: str):
        filename = os.path.basename(file_path)
        metadata = pdf.metadata
        title = metadata.get("title")

        if not title:
            title = filename

        source = self.detect_source(filename)
        category = self.detect_category(source)
        year = self.detect_year(filename)

        return {
            "filename": filename,
            "title": title,
            "source": source,
            "category": category,
            "year": year,
            "pages": pdf.page_count
        }

    def detect_category(self, source):
        mapping = {
            "NTSB": "Accident Report",
            "FAA": "Advisory Circular",
            "NASA": "Safety Report"
        }
        return mapping.get(source, "Unknown")

    def detect_source(self, filename):
        name = filename.upper()

        if name.startswith("AIR"):
            return "NTSB"
        if name.startswith("AC"):
            return "FAA"
        if "ASRS" in name:
            return "NASA"
        
        return "Unknown"

    def detect_year(self, filename):
        match = re.search(r"(19|20\d{2})", filename)
        if match:
            return (int) (match.group())
        
        return None