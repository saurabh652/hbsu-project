from fastapi import FastAPI, HTTPException
from schemas import ContentRequest, QuizRequest
from validator import validate, get_units_for_subject
from db import get_content, save_content
from llm import generate_content, generate_mcqs

app = FastAPI(title="Syllabus Restricted AI Engine")

# -------- CONTENT API --------
@app.post("/api/v1/content/generate")
def generate_content_api(req: ContentRequest):

    if not validate(req.program, req.subject, req.unit):
        raise HTTPException(
            status_code=400,
            detail="Invalid Program / Subject / Unit"
        )

    cached = get_content(req.program, req.subject, req.unit)
    if cached:
        return {"source": "cache", "content": cached}

    content = generate_content(req.unit)

    if content.startswith("ERROR"):
        return {"source": "llm", "content": content}

    save_content(req.program, req.subject, req.unit, content)
    return {"source": "llm", "content": content}


# -------- QUIZ API --------
@app.post("/api/v1/quiz/generate")
def generate_quiz_api(req: QuizRequest):

    units = get_units_for_subject(req.subject)
    if not units:
        raise HTTPException(400, "Invalid subject")

    combined_content = ""
    for program, unit in units:
        content = get_content(program, req.subject, unit)
        if content:
            combined_content += content + "\n"

    if not combined_content.strip():
        raise HTTPException(400, "Generate content first")

    mcqs = generate_mcqs(combined_content)
    return {"mcqs": mcqs}
