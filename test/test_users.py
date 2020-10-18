import json
import uuid
from unittest import TestCase

import requests

from src.utils.logger import LOGGER

new_user_id = 0
RANDOM_STRING = uuid.uuid4()
REQUEST_PAYLOAD = {
    "email": f"test.{RANDOM_STRING}@amit.com",
    "password": f"password123",
    "first_name": 'test',
    "last_name": f'{RANDOM_STRING}',
}


class TestUserOps(TestCase):
    """REST tests for users CRUD operations"""

    def setUp(self) -> None:
        super().setUp()
        self.test_case_name = self.id().split(".").pop()
        LOGGER.warning(f'Running test "{self.test_case_name}"')
        self.client = requests.Session()
        # self.base_url = f'http://0.0.0.0:8000/users'
        self.base_url = f'http://0.0.0.0:4000'
        self.random_id = RANDOM_STRING
        LOGGER.debug(f'new_user_id: {new_user_id}')
        self.json_response = dict()

    def tearDown(self) -> None:
        super().tearDown()
        # LOGGER.critical(f'Request: {self.json_response[""]}')
        LOGGER.info(f'[{self.test_case_name}] Response:'
                    f'\n{json.dumps(self.json_response, indent=4, sort_keys=True)}')

    def test_login(self):
        test_data = REQUEST_PAYLOAD.copy()
        test_data.pop('first_name')
        test_data.pop('last_name')
        response = self.client.post(f"{self.base_url}/login", data=json.dumps(test_data))
        assert response.status_code == 201
        self.json_response = response.json()
        assert REQUEST_PAYLOAD['email'] == self.json_response['email']

    def test_a_create_user(self):
        response = self.client.post(f"{self.base_url}/create", data=json.dumps(REQUEST_PAYLOAD))
        assert response.status_code == 201
        self.json_response = response.json()
        global new_user_id
        new_user_id = self.json_response.get('id')
        assert REQUEST_PAYLOAD['email'] == self.json_response['email']

    def test_create_duplicate_user(self):
        """create without password field"""
        response = self.client.post(f"{self.base_url}/create", data=json.dumps(REQUEST_PAYLOAD))
        assert response.status_code == 422
        self.json_response = response.json()

    def test_create_user_invalid_json(self):
        """create without password field"""
        test_request_payload = REQUEST_PAYLOAD.copy()
        test_request_payload['email'] = f'test.{uuid.uuid4()}@amit.com'
        test_request_payload.pop('password')
        response = self.client.post(
            f"{self.base_url}/create", data=json.dumps(test_request_payload)
        )
        assert response.status_code == 422
        self.json_response = response.json()

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
    def test_remove_user(self):
        test_data = {"id": new_user_id}
        response = self.client.delete(f"{self.base_url}/delete/{new_user_id}/")
        assert response.status_code == 200
        self.json_response = response.json()
        assert self.json_response['id'] == test_data['id']
    #
    # def test_remove_user_incorrect_id(self):
    #     response = self.client.delete(f"{self.base_url}/999/")
    #     assert response.status_code == 404
    #     assert response.json()["detail"] == "Note not found"
