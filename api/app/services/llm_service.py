from data.repositories.question_repository import QuestionRepository
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

class LLMService:
    def __init__(self):
        self.repo = QuestionRepository()
        self.llm = ChatOpenAI(
            model_name="deepseek-chat",
            base_url='https://api.proxyapi.ru/deepseek',
            api_key=os.getenv("PROXYAPI_KEY"),
            temperature=0.7
        )
    
    def llm_process(self, question, user_message, answer):
        prompt_template = PromptTemplate(
            input_variables=['question', 'user_message', 'answer'],
            template= ''' Ты эксперт в области backend, который специализируется на проведении собеседований с backend разработчиками. 
            Твоя задача оценивать ответ кандидата на поставленный вопрос о backend разработке, или на другую связанную тематику. 
            Также тебе будет дан ответ на данный вопрос из базы вопросов, этот ответ считается правильным и оценивается на 5 баллов.
            Твоя задача оценить ответ кандидата по 5-бальной шкале, сравнив его с эталонным ответом из базы. Учти, что ответ ответ кандидата может быть лучше,
            чем ответ из базы, но для получения максимального балла, он точно должен быть не хуже эталлонного ответа
            **Вопрос**
            {question}
            **Эталонный ответ на этот вопрос из базы вопросов**
            {answer} 
            **Ответ кандидата**
            {user_message}
            Ты должен отвечать в следующем формате: 
            Оценка: (оценка, которую ты поставил кандидату)
            Ниже должно идти обоснование поставленной тобой оценки, ты должен указать насколько кандадат в целом справился с ответом на вопрос, 
            указать на сильные и слабые стороны в его ответе (если таковы есть), если кандидат плохо ответил на вопрос, ты должен поррекомендовать темы,
            которые соотносятся вопросу кандидата, чтобы в следующий раз, он смог ответить на вопрос лучше
            Обоснование должно быть в следующем формате: общаешься с кандидатом на "ты" (твой ответ не плохой, но есть нюансы...), или (блестящий ответ, вижу, ты отлично разобрался в этой теме...)
            Используй markdown разметку в своем ответе, чтобы выделить ключевые моменты, которые ты хочешь донести до кандидата
            markdown разметка должна быть в формате telegram, то есть ты можешь использовать *жирный* и _курсивный_ текст, а также `inline code` для выделения ключевых моментов'''   
        )

        prompt = prompt_template.format(question=question, answer=answer, user_message=user_message)
        
        response = self.llm.invoke(prompt)
        
        return response
    
    def analyze_logs(self, logs):
        prompt_template = PromptTemplate(
            input_variables=['logs'],
            template='''Ты эксперт в области backend разработки. Твоя задача - анализировать логи приложений и выявлять возможные ошибки или проблемы. 
            Вот логи, которые нужно проанализировать:
            {logs}
            Ты должен ответить в следующем формате:
            1. Описание проблемы (если есть).
            2. Возможная причина проблемы.
            3. Рекомендации по исправлению.'''
        )

        prompt = prompt_template.format(logs=logs)
        
        response = self.llm.invoke(prompt)
        
        return response
