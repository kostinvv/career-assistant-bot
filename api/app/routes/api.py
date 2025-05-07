import uuid

from datetime import datetime, timezone 

from fastapi import APIRouter, status, HTTPException

from data.repositories.session_repository import SessionRepository
from data.repositories.question_repository import QuestionRepository
from data.schemas import *

from services.llm_service import LLMService

router = APIRouter()

@router.get("/topics", response_model=list[TopicSchema])
def get_topics():
    question_repository = QuestionRepository()
    response = question_repository.get_topics()
    return response

@router.get("/topics/{topic_id}/questions", response_model=list[QuestionSchema])
def get_questions_by_topic(topic_id: int, limit: int = 5):
    question_repository = QuestionRepository()
    questions = question_repository.get_questions_by_topic(topic_id, limit)

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found."
        )
    
    return questions

@router.get("/questions/{question_id}", response_model=QuestionSchema)
def get_question_by_id(question_id: int):
    question_repository = QuestionRepository()
    question = question_repository.get_question(question_id)

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found."
        )
    
    return question

@router.post("/sessions", status_code=status.HTTP_201_CREATED, response_model=SessionOut)
def create_session(payload: SessionCreate):
    question_repository = QuestionRepository()
    session_repository = SessionRepository()
    
    topic = question_repository.get_topic(payload.topic_id)
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found."
        )
    
    first_question = question_repository.get_questions_by_topic(payload.topic_id, limit=1)[0]

    new_session = SessionSchema(
        session_id=str(uuid.uuid4()),
        topic_id=payload.topic_id,
        current_q_id=first_question.id,
        created_at=str(datetime.now(timezone.utc))
    )

    response = session_repository.create_session(new_session)

    return SessionOut(
        session_id=response.session_id,
        question_id=response.current_q_id,
        text=first_question.question_text)

@router.post("/sessions/{session_id}/interactions", response_model=InteractionOut)
def interact(session_id: str, payload: InteractionIn):
    session_repository = SessionRepository()
    question_repository = QuestionRepository()
    llm_service = LLMService()
    session = session_repository.get_session(session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    if payload.question_id != session.current_q_id:
        raise HTTPException(status_code=400, detail="Unexpected question_id.")
    
    question = question_repository.get_question(payload.question_id)

    if question is None:
        raise HTTPException(status_code=404, detail="Question not found.")
    
    ai_response = llm_service.llm_process(
        question=question.question_text, 
        user_message=payload.answer, 
        answer=question.answer_text)
    
    content = ai_response.content

    interaction = InteractionSchema(
        session_id=session_id,
        question_id=payload.question_id,
        answer=payload.answer,
        ai_response=content
    )
    
    session_repository.create_interaction(interaction)
    next_question = question_repository.get_questions_by_topic(session.topic_id, limit=1)[0]
    session_repository.update_session(session_id, next_question.id)

    return InteractionOut(
        session_id=session_id,
        question_id=payload.question_id,
        answer=payload.answer,
        ai_response=content,
        next_question=QuestionOut(
            id=next_question.id,
            text=next_question.question_text
        )
    )
