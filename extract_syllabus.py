from pypdf import PdfReader
import re
import json
import os

PDF_PATH = os.path.join(os.path.dirname(__file__), "PFDFDC_Three-PGD.pdf")
OUTPUT_JSON = "syllabus.json"
OUTPUT_TXT = "syllabus_readable.txt"

reader = PdfReader(PDF_PATH)

# ---------------- EXTRACT TEXT ----------------
text = ""
for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

# ---------------- CLEAN FUNCTION ----------------
def clean_line(line):
    line = re.sub(r"\s+", " ", line)  # remove extra spaces
    line = re.sub(r"[•●▪]", "", line)  # remove bullets
    return line.strip()

# ---------------- MAIN LOGIC ----------------
syllabus = {}
program = None
subject = None
unit = None

for line in text.split("\n"):
    line = clean_line(line)

    if not line:
        continue

    # -------- PROGRAM --------
    if line.startswith("Postgraduate Diploma"):
        program = line
        syllabus[program] = {}
        subject = None
        unit = None
        continue

    # -------- SUBJECT --------
    if line.startswith("Course Title"):
        if program is None:
            continue

        subject = line.replace("Course Title", "").replace(":", "").strip()
        syllabus[program][subject] = {}
        unit = None
        continue

    # -------- UNIT --------
    match = re.match(r"(Unit\s+[IVX]+)\s*[–-]\s*(.*)", line)
    if match and program and subject:
        unit_name = f"{match.group(1)} – {match.group(2)}"
        syllabus[program][subject][unit_name] = {
            "topics": [],
            "word_count": 0
        }
        unit = unit_name
        continue

    # -------- CONTENT --------
    if program and subject and unit:
        if len(line) > 5 and not line.startswith(("Teaching", "Credits", "Evaluation")):
            
            # Avoid duplicates
            if line not in syllabus[program][subject][unit]["topics"]:
                syllabus[program][subject][unit]["topics"].append(line)
                
                # Word count
                syllabus[program][subject][unit]["word_count"] += len(line.split())

# ---------------- SAVE JSON ----------------
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(syllabus, f, indent=2, ensure_ascii=False)

# ---------------- SAVE READABLE TEXT ----------------
with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
    for prog, subjects in syllabus.items():
        f.write(f"\n📘 {prog}\n\n")
        for subj, units in subjects.items():
            f.write(f"  📗 {subj}\n")
            for unit, data in units.items():
                f.write(f"    📙 {unit} (Words: {data['word_count']})\n")
                for topic in data["topics"]:
                    f.write(f"      - {topic}\n")
                f.write("\n")

print("✅ syllabus.json + syllabus_readable.txt generated successfully")