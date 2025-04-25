from pydantic import BaseModel

class QuestionSchema(BaseModel):
    id: int
    topic_id: int
    question_text: str
    answer_text: str

    class Config:
        orm_mode = True