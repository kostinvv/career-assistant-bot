import uvicorn
import json

from fastapi import FastAPI
from routes.api import router

app = FastAPI()

app.include_router(router, prefix="/api", tags=["api"])

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=80)