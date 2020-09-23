import json
from unittest import TestCase

import pytest
import requests

from src.api.logger import LOGGER


class TestDbOps(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.client = requests.Session()
        self.base_url = f'http://0.0.0.0:8000'
        id_list = self.id().split('.')
        LOGGER.info(f'Running test "{id_list.pop()}"')

    def test_create_note(self):
        test_request_payload = {"title": "something", "description": "something else"}
        test_response_payload = {"id": 1,
                                 "title": "something",
                                 "description": "something else"}
        response = self.client.post(f"{self.base_url}/notes/",
                                    data=json.dumps(test_request_payload))
        assert response.status_code == 201
        data = response.json()
        LOGGER.info(f'Response: {data}')
        assert response.json() == test_response_payload

    def test_create_note_invalid_json(self):
        response = self.client.post(f"{self.base_url}/notes/",
                                    data=json.dumps({"title": "something"}))
        assert response.status_code == 422

    def test_read_note(self):
        test_data = {"id": 1, "title": "something", "description": "something else"}
        response = self.client.get(f"{self.base_url}/notes/1")
        assert response.status_code == 200
        assert response.json() == test_data

    def test_read_note_incorrect_id(self):
        response = self.client.get(f"{self.base_url}/notes/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Note not found"

    def test_read_all_notes(self):
        test_data = [
            {"title": "something", "description": "something else", "id": 1},
            {"title": "someone", "description": "someone else", "id": 2},
            ]
        response = self.client.get(f"{self.base_url}/notes/")
        assert response.status_code == 200
        assert response.json() == test_data

    def test_update_note(self):
        test_update_data = {"title": "someone", "description": "someone else", "id": 1}
        response = self.client.put(f"{self.base_url}/notes/1/", data=json.dumps(test_update_data))
        assert response.status_code == 200
        assert response.json() == test_update_data

    @pytest.mark.parametrize(
        "id, payload, status_code",
        [
            [1, {}, 422],
            [1, {"description": "bar"}, 422],
            [999, {"title": "foo", "description": "bar"}, 404],
            ],
        )
    def test_update_note_invalid(self, _id, payload, status_code):
        response = self.client.put(f"{self.base_url}/notes/{_id}/", data=json.dumps(payload))
        assert response.status_code == status_code

    def test_remove_note(self):
        test_data = {"title": "something", "description": "something else", "id": 1}
        response = self.client.delete(f"{self.base_url}/notes/1/")
        assert response.status_code == 200
        assert response.json() == test_data

    def test_remove_note_incorrect_id(self):
        response = self.client.delete(f"{self.base_url}/notes/999/")
        assert response.status_code == 404
        assert response.json()["detail"] == "Note not found"
