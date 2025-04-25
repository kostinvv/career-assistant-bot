from data.repositories.question_repository import QuestionRepository

class LLMService:
    def __init__(self):
        self.repo = QuestionRepository()

    def process_dataset(self):
        questions = self.repo.get_questions_by_topics([1, 4, 6])
        return questions
