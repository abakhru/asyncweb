from starlette.testclient import TestClient

from src.api.logger import LOGGER
from src.main import app

client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    data = response.json()
    LOGGER.debug(f'Response: {data}')
    assert data == {"ping": "pong!"}
