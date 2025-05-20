import logging
import traceback

from logging.config import dictConfig

import uuid

from datetime import datetime, timezone 

from fastapi import APIRouter, status, HTTPException

from data.repositories.session_repository import SessionRepository
from data.repositories.question_repository import QuestionRepository
from data.schemas import *

from services.llm_service import LLMService
from fastapi import Form

router = APIRouter()

dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "default",
            "level": "INFO",
        },
    },
    "loggers": {
        "watchfiles.main": {
            "level": "WARNING",
            "handlers": ["console", "file"],
            "propagate": False
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    },
})

logger = logging.getLogger(__name__)

@router.get("/topics", response_model=list[TopicSchema])
def get_topics():
    try:
        logger.info("Получение списка топиков")
        question_repository = QuestionRepository()
        response = question_repository.get_topics()
        return response
    except Exception:
        logger.error(f"Ошибка при получении топиков:\n" + traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/topics/{topic_id}/questions", response_model=list[QuestionSchema])
def get_questions_by_topic(topic_id: int, limit: int = 5):
    try:
        logger.info(f"Получение вопросов по топику {topic_id} с лимитом {limit}")
        if limit < 1:
            logger.warning(f"Некорректный лимит: {limit}. Лимит должен быть больше 0.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be greater than 0."
            )
        
        question_repository = QuestionRepository()
        questions = question_repository.get_questions_by_topic(topic_id, limit)

        if not questions:
            logger.warning(f"Вопросы по топику {topic_id} не найдены.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found."
            )
        return questions
    except HTTPException as e:
        logger.warning(f"Ошибка при получении вопросов по топику {topic_id}: {e.detail}")
        raise e
    except Exception:
        logger.error(f"Ошибка при получении вопросов по топику {topic_id}:\n" + traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/questions/{question_id}", response_model=QuestionSchema)
def get_question_by_id(question_id: int):
    try:
        logger.info(f"Получение вопроса с ID {question_id}")
        question_repository = QuestionRepository()
        question = question_repository.get_question(question_id)

        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found."
            )
        
        return question
    except Exception as e:
        logger.warning(f"Ошибка при получении вопроса {question_id}: {e.detail}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/sessions", status_code=status.HTTP_201_CREATED, response_model=SessionOut)
def create_session(payload: SessionCreate):
    try:
        logger.info(f"Создание сессии с топиком {payload.topic_id}")
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
    except Exception:
        logger.error(f"Ошибка при создании сессии:\n" + traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/sessions/{session_id}/interactions", response_model=InteractionOut)
def interact(session_id: str, payload: InteractionIn):
    try:
        logger.info(f"Взаимодействие с сессией {session_id} и вопросом {payload.question_id}")
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
    except HTTPException as e:
        logger.warning(f"Ошибка при взаимодействии с сессией {session_id}: {e.detail}")
        raise e
    except Exception:
        logger.error(f"Ошибка при взаимодействии с сессией {session_id}:\n" + traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.post("/analyze_logs_text")
def analyze_logs_text(log_message: str = Form(...)):
    try:
        logger.info(f"Запрос на анализ логов: {log_message}")
        llm_service = LLMService()
        response = llm_service.analyze_logs(log_message)
        return response
    except Exception:
        logger.error(f"Ошибка при анализе логов:\n" + traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health", status_code=status.HTTP_200_OK) 
def health():
    return {"status": "ok"}