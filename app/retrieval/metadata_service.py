import json

class MetadataService:

    def __init__(self):
        with open("data/metadata/reports.json", "r", encoding="utf-8") as f:
            self.reports = json.load(f)

    # def find_reports(self, question):
    #     question = question.lower()
    #     matched = []

    #     for report in self.reports:
    #         text = (report["title"] + (report["airline"] or "") + " ".join(report["keywords"])).lower()

    #         if any(word in text for word in text.split()):
    #             matched.append(report)

    #     return matched


    # def find_reports(self, question):
    #     question = question.lower()

    #     matched = []

    #     for report in self.reports:

    #         # Report ID
    #         report_id = report["report_id"].lower()

    #         if report_id in question:
    #             matched.append(report)
    #             continue

    #         # Airline
    #         airline = report.get("airline")

    #         if airline and airline.lower() in question:
    #             matched.append(report)
    #             continue

    #         # Aircraft
    #         aircraft = report.get("aircraft")

    #         if isinstance(aircraft, list):
    #             if any(item.lower() in question for item in aircraft):
    #                 matched.append(report)
    #                 continue

    #         elif aircraft and aircraft.lower() in question:
    #             matched.append(report)
    #             continue

    #         # Keywords
    #         keywords = report.get("keywords", [])

    #         if any(keyword.lower() in question for keyword in keywords):
    #             matched.append(report)
    #             continue

    #     return matched

    # def get_best_match(self, question):
    #     reports = self.find_reports(question)
        
    #     if reports:
    #         return reports[0]
        
    #     return None

def find_reports(self, question):
    question = question.lower()

    scored_reports = []

    for report in self.reports:
        score = 0

        # Report ID → strongest match
        report_id = report["report_id"].lower()

        if report_id in question:
            score += 10

        # Airline
        airline = report.get("airline")

        if airline and airline.lower() in question:
            score += 5

        # Aircraft
        aircraft = report.get("aircraft")

        if isinstance(aircraft, list):
            for item in aircraft:
                if item.lower() in question:
                    score += 5

        elif aircraft and aircraft.lower() in question:
            score += 5

        # Keywords
        keywords = report.get("keywords", [])

        for keyword in keywords:
            if keyword.lower() in question:
                score += 3

        # Only keep actual matches
        if score > 0:
            scored_reports.append((report, score))

    # Highest score first
    scored_reports.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return scored_reports


def get_best_match(self, question):
    reports = self.find_reports(question)

    if reports:
        return reports[0][0]

    return None