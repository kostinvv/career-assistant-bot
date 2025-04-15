from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def get_data():
    return { "message": "Hello, World!" }

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=80)   