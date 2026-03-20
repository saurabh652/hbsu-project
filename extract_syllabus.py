from pypdf import PdfReader
import re
import json
import os

PDF_PATH = os.path.join(os.path.dirname(__file__), "PFDFDC_Three-PGD.pdf")
OUTPUT = "syllabus.json"

reader = PdfReader(PDF_PATH)

text = ""
for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

syllabus = {}
program = None
subject = None
unit = None

for line in text.split("\n"):
    line = line.strip()

    # ---------------- PROGRAM ----------------
    if line.startswith("Postgraduate Diploma"):
        program = line
        if program not in syllabus:
            syllabus[program] = {}
        subject = None
        unit = None
        continue

    # ---------------- SUBJECT ----------------
    if line.startswith("Course Title"):
        if program is None:
            continue  # safety check

        subject = line.replace("Course Title", "").replace(":", "").strip()
        syllabus[program][subject] = {}
        unit = None
        continue

    # ---------------- UNIT ----------------
    match = re.match(r"(Unit\s+[IVX]+)\s*[–-]\s*(.*)", line)
    if match and program and subject:
        unit = f"{match.group(1)} – {match.group(2)}"
        syllabus[program][subject][unit] = []
        continue

    # ---------------- UNIT CONTENT ----------------
    if program and subject and unit:
        if len(line) > 5 and not line.startswith(("Teaching", "Credits", "Evaluation")):
            syllabus[program][subject][unit].append(line)

# Save output
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(syllabus, f, indent=2, ensure_ascii=False)

print("✅ syllabus.json generated successfully")
