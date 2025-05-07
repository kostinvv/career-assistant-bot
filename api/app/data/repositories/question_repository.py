from sqlalchemy import text

from ..schemas import QuestionSchema, TopicSchema
from ..database import SessionLocal

class QuestionRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_topics(self):
        query = text("SELECT id, name FROM qa_dataset.topics WHERE id NOT IN (4, 6)")
        response = self.db.execute(query).fetchall()
        self.db.close()
        return [TopicSchema(id=row[0], name=row[1]) for row in response]
    
    def get_topic(self, topic_id):
        query = text("SELECT id, name FROM qa_dataset.topics WHERE id = :topic_id")
        response = self.db.execute(query, {"topic_id": topic_id}).fetchone()
        self.db.close()
        if response:
            return TopicSchema(id=response[0], name=response[1])
        return None
    
    def get_questions_by_topic(self, topic_id, limit=5):
        query = text("SELECT id, topic_id, question_text, answer_text FROM " \
            "qa_dataset.questions WHERE topic_id = :topic_id " \
            "ORDER BY RANDOM()" \
            "LIMIT :limit")
        
        response = self.db.execute(query, {"topic_id": topic_id, "limit": limit}).fetchall()
        self.db.close()
        return [QuestionSchema(id=row[0], topic_id=row[1], question_text=row[2], answer_text=row[3]) for row in response]
    
    def get_question(self, question_id):
        query = text("SELECT id, topic_id, question_text, answer_text FROM " \
            "qa_dataset.questions WHERE id = :question_id")
        
        response = self.db.execute(query, {"question_id": question_id}).fetchone()
        self.db.close()
        if response:
            return QuestionSchema(id=response[0], topic_id=response[1], question_text=response[2], answer_text=response[3])
        return None