from sqlalchemy import text

from ..schemas import QuestionSchema
from ..database import SessionLocal

class QuestionRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_all_questions(self):
        query = text("SELECT * FROM qa_dataset.questions")
        response = self.db.execute(query).fetchall()
        self.db.close()
        return [QuestionSchema(id=row[0], topic_id=row[1], question_text=row[2], answer_text=row[3]) for row in response]
    
    def get_questions_by_topics(self, topic_ids):
        query = text("SELECT * FROM qa_dataset.questions WHERE topic_id IN :topic_ids")
        response = self.db.execute(query, {"topic_ids": tuple(topic_ids)}).fetchall()
        self.db.close()
        return [QuestionSchema(id=row[0], topic_id=row[1], question_text=row[2], answer_text=row[3]) for row in response]