import json

with open("syllabus.json", "r", encoding="utf-8") as f:
    SYLLABUS = json.load(f)

def validate(program, subject, unit):
    return (
        program in SYLLABUS and
        subject in SYLLABUS[program] and
        unit in SYLLABUS[program][subject]["units"]
    )

def get_units_for_subject(subject):
    units = []
    for program in SYLLABUS:
        if subject in SYLLABUS[program]:
            for unit in SYLLABUS[program][subject]["units"]:
                units.append((program, unit))
    return units
