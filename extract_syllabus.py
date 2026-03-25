from pypdf import PdfReader
import re
import json
from pathlib import Path
from collections import defaultdict

# ---------------- PATH SETUP ----------------
ROOT = Path(__file__).parent
PDF_PATH = ROOT / "PFDFDC_Three-PGD.pdf"
JSON_PATH = ROOT / "syllabus.json"
TXT_PATH = ROOT / "syllabus_readable.txt"


# ---------------- STEP 1: LOAD PDF ----------------
def load_pdf_lines(path):
    reader = PdfReader(path)
    lines = []

    for pg in reader.pages:
        txt = pg.extract_text()
        if txt:
            lines.extend(txt.split("\n"))

    return lines


# ---------------- STEP 2: CLEAN ----------------
def preprocess(lines):
    cleaned = []
    for l in lines:
        l = re.sub(r"[•●▪]", "", l)
        l = re.sub(r"\s+", " ", l).strip()
        if l:
            cleaned.append(l)
    return cleaned


# ---------------- STEP 3: PARSE ----------------
def build_structure(lines):
    data = defaultdict(lambda: defaultdict(dict))

    prog, subj, unit = None, None, None

    for line in lines:

        # PROGRAM
        if "Postgraduate Diploma" in line:
            prog = line
            subj, unit = None, None
            continue

        # SUBJECT
        if "Course Title" in line and prog:
            subj = re.sub(r"Course Title\s*:?", "", line).strip()
            data[prog][subj] = {}
            unit = None
            continue

        # UNIT
        unit_match = re.search(r"(Unit\s+[IVX]+)\s*[–-]\s*(.*)", line)
        if unit_match and prog and subj:
            unit = f"{unit_match.group(1)} – {unit_match.group(2)}"
            data[prog][subj][unit] = {"topics": [], "word_count": 0}
            continue

        # TOPICS
        if prog and subj and unit:
            if is_topic(line):
                insert_topic(data, prog, subj, unit, line)

    return dict(data)


# ---------------- HELPERS ----------------
def is_topic(text):
    blocked = ["Teaching", "Credits", "Evaluation"]
    return len(text) > 5 and not any(text.startswith(b) for b in blocked)


def insert_topic(store, prog, subj, unit, text):
    topics = store[prog][subj][unit]["topics"]

    if text not in topics:
        topics.append(text)
        store[prog][subj][unit]["word_count"] += len(text.split())


# ---------------- STEP 4: SAVE ----------------
def export_json(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_text(data):
    with open(TXT_PATH, "w", encoding="utf-8") as f:
        for prog in data:
            f.write(f"\n📘 {prog}\n")

            for subj in data[prog]:
                f.write(f"\n  📗 {subj}\n")

                for unit in data[prog][subj]:
                    meta = data[prog][subj][unit]
                    f.write(f"    📙 {unit} ({meta['word_count']} words)\n")

                    for t in meta["topics"]:
                        f.write(f"      • {t}\n")


# ---------------- MAIN PIPELINE ----------------
def main():
    raw_lines = load_pdf_lines(PDF_PATH)
    cleaned_lines = preprocess(raw_lines)
    structured = build_structure(cleaned_lines)

    export_json(structured)
    export_text(structured)

    print("✅ Done! Outputs created.")


if __name__ == "__main__":
    main()