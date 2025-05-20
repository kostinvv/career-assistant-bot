import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from ..routes import api

app = FastAPI()
app.include_router(api.router)
client = TestClient(app)

# ---------- /topics ----------
def test_get_topics_success():
    fake_topics = [
        api.TopicSchema(id=1, name="SQL"),
        api.TopicSchema(id=2, name="DevOps"),
    ]

    with patch.object(api.QuestionRepository, "get_topics", return_value=fake_topics):
        r = client.get("/topics")
    assert r.status_code == status.HTTP_200_OK
    assert r.json() == [t.model_dump() for t in fake_topics]

