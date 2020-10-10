import json
from random import randint
from unittest import TestCase

import requests
from parameterized import parameterized

from src.utils.logger import LOGGER

new_note_id = 0


class TestDbOps(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = requests.Session()
        self.base_url = f'http://0.0.0.0:8000/notes'
        id_list = self.id().split('.')
        LOGGER.info(f'Running test "{id_list.pop()}"')
        # print(f'==== New Id of note: {new_note_id}')

    def test_create_note(self):
        random_id = randint(1, 5000)
        test_request_payload = {"title": "something", "description": f"something else {random_id}"}
        test_response_payload = {"title": "something", "description": f"something else {random_id}"}
        response = self.client.post(f"{self.base_url}/", data=json.dumps(test_request_payload))
        assert response.status_code == 201
        data = response.json()
        # print(f'Response: {data}')
        global new_note_id
        new_note_id = data.pop('id')
        assert data.get('description') == test_response_payload['description']

    def test_create_note_invalid_json(self):
        """create without required fields"""
        response = self.client.post(f"{self.base_url}/", data=json.dumps({"title": "something"}))
        assert response.status_code == 422

    def test_read_note(self):
        response = self.client.get(f"{self.base_url}/{new_note_id}/")
        assert response.status_code == 200
        assert response.json().get('id') == new_note_id

    def test_read_note_incorrect_id(self):
        response = self.client.get(f"{self.base_url}/999/")
        assert response.status_code == 404
        assert response.json()["detail"] == "Note not found"

    def test_read_all_notes(self):
        response = self.client.get(f"{self.base_url}/")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_update_note(self):
        test_response_payload = {
            "title": "something",
            "description": f"something else {randint(1, 5000)}",
        }
        response = self.client.post(f"{self.base_url}/", data=json.dumps(test_response_payload))
        global new_note_id
        new_note_id = response.json()['id']
        test_update_data = {
            "title": "someone",
            "description": "newWWW someone else",
            "id": new_note_id,
        }
        response = self.client.put(
            f"{self.base_url}/{new_note_id}/", data=json.dumps(test_update_data)
        )
        assert response.status_code == 200
        assert response.json() == test_update_data

    @parameterized.expand(
        [
            (1, {}, 422),
            (1, {"description": "bar"}, 422),
            (999, {"title": "foo", "description": "bar"}, 404),
        ]
    )
    def test_update_note_invalid(self, _id, payload, status_code):
        response = self.client.put(f"{self.base_url}/{_id}/", data=json.dumps(payload))
        assert response.status_code == status_code

    def test_remove_note(self):
        test_data = {"id": new_note_id}
        response = self.client.delete(f"{self.base_url}/{new_note_id}/")
        assert response.status_code == 200
        assert response.json()['id'] == test_data['id']

    def test_remove_note_incorrect_id(self):
        response = self.client.delete(f"{self.base_url}/999/")
        assert response.status_code == 404
        assert response.json()["detail"] == "Note not found"
