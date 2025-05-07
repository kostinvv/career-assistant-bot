from sqlalchemy import text

from ..schemas import SessionSchema
from ..database import SessionLocal

class SessionRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_session(self, session_id):
        quite = text("SELECT session_id, topic_id, current_q_id, created_at FROM llm.sessions WHERE session_id = :session_id")
        response = self.db.execute(quite, {"session_id": session_id}).fetchone()
        
        if response:
            return SessionSchema(
                session_id=str(response[0]),
                topic_id=response[1],
                current_q_id=response[2],
                created_at=str(response[3])
            )
        self.db.close()
        
        return None

    def create_session(self, session):
        query = text("INSERT INTO llm.sessions (session_id, topic_id, current_q_id, created_at) " \
                     "VALUES (:session_id, :topic_id, :current_q_id, :created_at)")
        
        self.db.execute(query, {
            "session_id": session.session_id,
            "topic_id": session.topic_id,
            "current_q_id": session.current_q_id,
            "created_at": session.created_at
        })
        self.db.commit()
        self.db.close()

        return session
    
    def create_interaction(self, interaction):
        query = text("INSERT INTO llm.interactions (session_id, question_id, answer, ai_response) " \
                     "VALUES (:session_id, :question_id, :answer, :ai_response)")
        
        self.db.execute(query, {
            "session_id": interaction.session_id,
            "question_id": interaction.question_id,
            "answer": interaction.answer,
            "ai_response": interaction.ai_response
        })
        self.db.commit()
        self.db.close()

        return interaction
    
    def update_session(self, session_id, question_id):
        query = text("UPDATE llm.sessions SET current_q_id = :question_id WHERE session_id = :session_id")
        
        self.db.execute(query, {
            "session_id": session_id,
            "question_id": question_id
        })
        self.db.commit()
        self.db.close()
    