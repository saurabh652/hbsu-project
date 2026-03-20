from pydantic import BaseModel

class ContentRequest(BaseModel):
    program: str
    subject: str
    unit: str

class QuizRequest(BaseModel):
    subject: str
