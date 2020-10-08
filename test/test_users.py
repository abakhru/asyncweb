import json
import uuid
from random import randint
from unittest import TestCase

import requests
from parameterized import parameterized

from src.api.logger import LOGGER

new_user_id = 0


class TestUserOps(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.client = requests.Session()
        self.base_url = f'http://0.0.0.0:8000/users'
        id_list = self.id().split('.')
        LOGGER.info(f'Running test "{id_list.pop()}"')
        LOGGER.info(f'==== New Id of note: {new_user_id}')

    def test_create_user(self):
        random_id = uuid.uuid4()
        test_request_payload = {"email": f"test.{random_id}@amit.com",
                                "password": f"password123",
                                "first_name": 'test',
                                "last_name": f'{random_id}',
                                }
        response = self.client.post(f"{self.base_url}/create",
                                    data=json.dumps(test_request_payload))
        assert response.status_code == 201
        data = response.json()
        LOGGER.debug(f'Response: {data}')
        global new_user_id
        new_user_id = data.pop('id')
        # assert data.get('description') == test_response_payload['description']

    # def test_create_user_invalid_json(self):
    #     """create without required fields"""
    #     response = self.client.post(f"{self.base_url}/",
    #                                 data=json.dumps({"title": "something"}))
    #     assert response.status_code == 422
    # 
    # def test_read_user(self):
    #     response = self.client.get(f"{self.base_url}/{new_user_id}/")
    #     assert response.status_code == 200
    #     assert response.json().get('id') == new_user_id
    # 
    # def test_read_user_incorrect_id(self):
    #     response = self.client.get(f"{self.base_url}/999/")
    #     assert response.status_code == 404
    #     assert response.json()["detail"] == "Note not found"
    # 
    # def test_read_all_users(self):
    #     response = self.client.get(f"{self.base_url}/")
    #     assert response.status_code == 200
    #     assert len(response.json()) > 1
    # 
    # def test_update_user(self):
    #     test_response_payload = {"title": "something",
    #                              "description": f"something else {randint(1, 5000)}"}
    #     response = self.client.post(f"{self.base_url}/",
    #                                 data=json.dumps(test_response_payload))
    #     global new_user_id
    #     new_user_id = response.json()['id']
    #     test_update_data = {"title": "someone",
    #                         "description": "newWWW someone else",
    #                         "id": new_user_id}
    #     response = self.client.put(f"{self.base_url}/{new_user_id}/",
    #                                data=json.dumps(test_update_data))
    #     assert response.status_code == 200
    #     assert response.json() == test_update_data
    # 
    # @parameterized.expand([
    #     (1, {}, 422),
    #     (1, {"description": "bar"}, 422),
    #     (999, {"title": "foo", "description": "bar"}, 404),
    #     ])
    # def test_update_user_invalid(self, _id, payload, status_code):
    #     response = self.client.put(f"{self.base_url}/{_id}/", data=json.dumps(payload))
    #     assert response.status_code == status_code
    # 
    # def test_remove_user(self):
    #     test_data = {"id": new_user_id}
    #     response = self.client.delete(f"{self.base_url}/{new_user_id}/")
    #     assert response.status_code == 200
    #     assert response.json()['id'] == test_data['id']
    # 
    # def test_remove_user_incorrect_id(self):
    #     response = self.client.delete(f"{self.base_url}/999/")
    #     assert response.status_code == 404
    #     assert response.json()["detail"] == "Note not found"
