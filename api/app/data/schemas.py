from pydantic import BaseModel

class TopicSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class QuestionSchema(BaseModel):
    id: int
    topic_id: int
    question_text: str
    answer_text: str

    class Config:
        from_attributes = True

class SessionSchema(BaseModel):
    session_id: str
    topic_id: int
    current_q_id: int
    created_at: str

    class Config:
        from_attributes = True

class InteractionSchema(BaseModel):
    session_id: str
    question_id: int
    answer: str
    ai_response: str

    class Config:
        from_attributes = True

class SessionCreate(BaseModel):
    topic_id: int

class SessionOut(BaseModel):
    session_id: str
    question_id: int
    text: str

class InteractionIn(BaseModel):
    question_id: int
    answer: str

class QuestionOut(BaseModel):
    id: int
    text: str

class InteractionOut(BaseModel):
    session_id: str
    question_id: int
    answer: str
    ai_response: str
    next_question: QuestionOut | None

class AnalyzeLogsRequest(BaseModel):
    log_message: str