from pypdf import PdfReader
import re
import json
from pathlib import Path

# ---------------- CONFIG ----------------
BASE_DIR = Path(__file__).resolve().parent
PDF_FILE = BASE_DIR / "PFDFDC_Three-PGD.pdf"
JSON_OUT = BASE_DIR / "syllabus.json"
TEXT_OUT = BASE_DIR / "syllabus_readable.txt"


# ---------------- UTILITIES ----------------
def extract_pdf_content(file_path):
    """Extract full text from PDF"""
    reader = PdfReader(file_path)
    collected_text = []

    for page in reader.pages:
        content = page.extract_text()
        if content:
            collected_text.append(content)

    return "\n".join(collected_text)


def normalize_text(line):
    """Clean and normalize a line"""
    line = re.sub(r"[•●▪]", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def is_valid_topic(line):
    """Filter unwanted lines"""
    ignore_keywords = ("Teaching", "Credits", "Evaluation")
    return len(line) > 5 and not line.startswith(ignore_keywords)


# ---------------- PARSER CLASS ----------------
class SyllabusParser:

    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.data = {}
        self.current_program = None
        self.current_subject = None
        self.current_unit = None

    def parse(self):
        for raw_line in self.raw_text.splitlines():
            line = normalize_text(raw_line)

            if not line:
                continue

            if self._detect_program(line):
                continue

            if self._detect_subject(line):
                continue

            if self._detect_unit(line):
                continue

            self._add_topic(line)

        return self.data

    # ---------- DETECTORS ----------
    def _detect_program(self, line):
        if line.startswith("Postgraduate Diploma"):
            self.current_program = line
            self.data[self.current_program] = {}
            self.current_subject = None
            self.current_unit = None
            return True
        return False

    def _detect_subject(self, line):
        if line.startswith("Course Title") and self.current_program:
            subject_name = line.replace("Course Title", "").replace(":", "").strip()
            self.data[self.current_program][subject_name] = {}
            self.current_subject = subject_name
            self.current_unit = None
            return True
        return False

    def _detect_unit(self, line):
        pattern = r"(Unit\s+[IVX]+)\s*[–-]\s*(.*)"
        match = re.match(pattern, line)

        if match and self.current_program and self.current_subject:
            unit_title = f"{match.group(1)} – {match.group(2)}"
            self.data[self.current_program][self.current_subject][unit_title] = {
                "topics": [],
                "word_count": 0
            }
            self.current_unit = unit_title
            return True

        return False

    # ---------- ADD CONTENT ----------
    def _add_topic(self, line):
        if not (self.current_program and self.current_subject and self.current_unit):
            return

        if not is_valid_topic(line):
            return

        unit_data = self.data[self.current_program][self.current_subject][self.current_unit]

        if line not in unit_data["topics"]:
            unit_data["topics"].append(line)
            unit_data["word_count"] += len(line.split())


# ---------------- OUTPUT HANDLERS ----------------
def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_readable(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        for program, subjects in data.items():
            f.write(f"\n📘 {program}\n\n")

            for subject, units in subjects.items():
                f.write(f"  📗 {subject}\n")

                for unit, info in units.items():
                    f.write(f"    📙 {unit} (Words: {info['word_count']})\n")

                    for topic in info["topics"]:
                        f.write(f"      - {topic}\n")

                    f.write("\n")


# ---------------- MAIN EXECUTION ----------------
def run_pipeline():
    raw_text = extract_pdf_content(PDF_FILE)

    parser = SyllabusParser(raw_text)
    structured_data = parser.parse()

    save_json(structured_data, JSON_OUT)
    save_readable(structured_data, TEXT_OUT)

    print("✅ Files generated successfully:")
    print(f"   → {JSON_OUT.name}")
    print(f"   → {TEXT_OUT.name}")


if __name__ == "__main__":
    run_pipeline()