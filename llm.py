import ollama

OLLAMA_HOST = "http://3.7.91.177:11434"   # your Ubuntu Ollama server
MODEL = "llama3.2:3b"

client = ollama.Client(host=OLLAMA_HOST)

# -------- CONTENT (~5000 WORDS) --------
def generate_content(unit):
    try:
        response = client.generate(
            model=MODEL,
            prompt=f"""
You are a university professor.

TASK:
Write a DETAILED academic explanation.

RULES:
- University-level depth
- Headings, subheadings, paragraphs
- Around 5000 words
- STRICTLY limited to the topic
- No MCQs, no summary

TOPIC:
{unit}
""",
            stream=False
        )

        if not response or "response" not in response:
            return "ERROR: Empty LLM output"

        return response["response"]

    except Exception as e:
        return f"ERROR: {str(e)}"


# -------- MCQs (EXACTLY 25, NO ANSWERS) --------
def generate_mcqs(content):
    try:
        response = client.generate(
            model=MODEL,
            prompt=f"""
You are an expert examiner.

TASK:
Generate EXACTLY 25 multiple-choice questions (MCQs).

STRICT RULES:
- Total questions MUST be exactly 25
- Number questions from Q1 to Q25
- Each question must have EXACTLY 4 options: A, B, C, D
- DO NOT include correct answers
- DO NOT include explanations
- DO NOT include headings or extra text
- Output ONLY MCQs

FORMAT (STRICT):
Q1. Question text
A. Option
B. Option
C. Option
D. Option

CONTENT:
{content[:4000]}
""",
            stream=False
        )

        if not response or "response" not in response:
            return "ERROR: Empty MCQ output"

        return response["response"]

    except Exception as e:
        return f"ERROR: {str(e)}"
