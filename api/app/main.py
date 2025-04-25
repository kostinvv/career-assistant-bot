from fastapi import FastAPI
import uvicorn
from services.llm_service import LLMService

app = FastAPI()

@app.get("/")
def get_data():
    llm_service = LLMService()
    response = llm_service.process_dataset()

    return response

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=80)