import json

class MetadataService:

    def __init__(self):
        with open("data/metadata/reports.json", "r", encoding="utf-8") as f:
            self.reports = json.load(f)

    def find_reports(self, question):
        question = question.lower()
        matched = []

        for report in self.reports:
            text = (report["title"] + (report["airline"] or "") + " ".join(report["keywords"])).lower()

            if any(word in text for word in text.split()):
                matched.append(report)

        return matched

    def get_best_match(self, question):
        reports = self.find_reports(question)
        
        if reports:
            return reports[0]
        
        return None