import json
from uuid import uuid4

import caliber_bb
from caliber.framework.common.logger import LOGGER
from caliber.framework.utils.generic_utils import GenericUtilities
from caliber_bb.framework.blackbox_pg import (
    BOT_CODE,
    USER_ROLES,
    USER_SEEDS,
    UUID,
    PARENT_UUID,
    SCIM_GROUP_ADMIN_ID,
    SCIM_GROUP_READ_ONLY_ID,
)
from caliber_bb.framework.testcase import BlackboxBaseTestCase
from psycopg2._psycopg import DatabaseError

from blackbox import configuration
from blackbox.utilities import db, security, user_utils


def setUpModule():
    if not caliber_bb.REMOTE_INSTALL:
        LOGGER.debug('Inside setUpModule')
        try:
            [caliber_bb.POSTGRES_SERVER.create_customer_user(user) for user in USER_SEEDS]
        except DatabaseError:
            # ignoring already existing error
            pass


class UserManagementTestCase(BlackboxBaseTestCase):
    user = None

    @classmethod
    def setUpClass(cls):
        try:
            [caliber_bb.POSTGRES_SERVER.create_customer_user(user) for user in USER_SEEDS]
        except DatabaseError:
            # ignoring already existing error
            pass

    def setUp(self, repo_path=None):
        super(UserManagementTestCase, self).setUp()
        self.rest_driver = self.blackbox_server.rest_driver['users']
        self.rest_driver_customers = self.blackbox_server.rest_driver['customers']
        self.user = '{}_{}'.format(self.test_case_name, GenericUtilities.get_unique_id())

    def test_assume_child(self):
        '''
        This test is used to ensure that a parent can retrieve a child user's data by utilizing
        the users/assume_child functionality.
        TODO: When we have endpoints to update a customer or user's permissions, increase testing
        coverage to verify that the child is assumed in read-only mode when these permisisons
        are changed to read-only, and the child cannot be assumed when these permissions are
        removed.
        '''
        # Create user of parent customer with account delegation admin
        parent_first_name = self.user + '-Parent'
        rv = self.blackbox_server.CreateUser(
            data={
                'email': '{}_parent@test1.com'.format(self.user),
                'customer_id': PARENT_UUID,
                'password': 'whysosassy',
                'role': 'admin',
                'first_name': parent_first_name,
                'last_name': 'sassy',
            }
        )
        assert rv.status_code == 200
        parent_user = json.loads(rv.text)['data']
        assert parent_user['customer_id'] == PARENT_UUID
        assert parent_user['first_name'] == parent_first_name
        assert parent_user['last_name'] == 'sassy'
        assert parent_user['role'] == 'admin'
        assert parent_user['user_permissions'] == []
        assert parent_user['customer_permissions'] == ["parent admin"]
        assert parent_user['role'] == 'admin'
        assert parent_user['is_parent'] == True
        rv = self.rest_driver.Post(
            '/users/{}/permission'.format(parent_user['user_id']),
            data=json.dumps({'permission': 'child admin'}),
        )

        # Now test assume_child
        rv = self.rest_driver.Get(
            '/users/{}/assume_child/{}/{}'.format(
                parent_user['user_id'], UUID, parent_user['user_id']
            )
        )
        assumed_child_user = json.loads(rv.text)['data']
        assert assumed_child_user['parent_user_id'] == parent_user['user_id']
        assert assumed_child_user['email'] == parent_user['email']
        assert assumed_child_user['customer_permissions'] == ["parent admin"]
        assert assumed_child_user['user_permissions'] == ["child admin"]
        assert assumed_child_user['first_name'] == parent_user['first_name']
        assert assumed_child_user['is_parent'] == False
        assert assumed_child_user['role'] == 'admin'

    @caliber_bb.local_only
    def test_get_user_by_id(self):
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test22.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200
        user_id = json.loads(rv.text)['data']['user_id']

        rv = self.rest_driver.Get('/users/{}/'.format(user_id))
        assert rv.status_code == 200
        self.assertAPIResponse(
            rv,
            ignorefields=[
                'first_name',
                'email',
                'customer_created_at',
                'password_last_modified',
                'created_at',
                'last_modified',
                'user_id',
                'customer_permissions',
                'user_permissions',
                'customer_created_at',
                'bot_code',
            ],
        )

    @caliber_bb.local_only
    def test_get_inactive_user(self):
        # Create test user
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test22.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200
        user_id = json.loads(rv.text)['data']['user_id']

        # DELETE the user
        rv = self.rest_driver_customers.Delete('/customers/{}/users/{}'.format(UUID, user_id))
        assert rv.status_code == 200

        # Get inactive user
        rv = self.rest_driver.Get('/users/{}/inactive'.format(user_id))
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['customer_id'] == UUID

    @caliber_bb.local_only
    def test_scim_groups_join(self):
        # Create test user
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test22.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200
        user_id = json.loads(rv.text)['data']['user_id']

        # Join user to READ ONLY SCIM Group
        rv = self.rest_driver.Post(
            '/users/{}/scim_groups/{}'.format(user_id, SCIM_GROUP_READ_ONLY_ID),
            data=json.dumps({}),
        )
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['role'] == 'read only'

        # Join user to ADMIN SCIM Group and be sure the read only role is selected
        rv = self.rest_driver.Post(
            '/users/{}/scim_groups/{}'.format(user_id, SCIM_GROUP_ADMIN_ID), data=json.dumps({}),
        )
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['role'] == 'read only'

        # Delete join to READ ONLY SCIM Group
        rv = self.rest_driver.Delete(
            '/users/{}/scim_groups/{}'.format(user_id, SCIM_GROUP_READ_ONLY_ID)
        )
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['role'] == 'admin'

    def test_create_users(self):
        rv = self.blackbox_server.CreateUser(
            data={
                'email': '{}@test1.com'.format(self.user),
                'customer_id': UUID,
                'password': 'whysosassy',
                'role': 'admin',
                'first_name': self.user,
                'last_name': 'sassy',
            }
        )
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['customer_id'] == UUID
        assert data['first_name'] == self.user
        assert data['last_name'] == 'sassy'
        assert data['role'] == 'admin'
        assert data['bot_code'] == BOT_CODE

    def test_user_permissions_crud(self):
        """
        Verifies that update, delete, create functionality of user permissions CRUD is working
        Checks for errors when sending a permission value that doesn't exist
        """
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test1.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200
        user = json.loads(rv.text)['data']
        user_id = user['user_id']
        user_permissions = user['user_permissions']
        assert user_permissions == []

        # Create permission
        rv = self.rest_driver.Post(
            '/users/{}/permission'.format(user_id), data=json.dumps({'permission': 'child admin'}),
        )
        assert rv.status_code == 200
        user = json.loads(rv.text)['data']
        user_permissions = user['user_permissions']
        assert user_permissions == ["child admin"]

        # Update permission
        rv = self.rest_driver.Put(
            '/users/{}/permission'.format(user_id),
            data=json.dumps({'old_permission': 'child admin', 'new_permission': 'child read only'}),
        )
        assert rv.status_code == 200
        user = json.loads(rv.text)['data']
        user_permissions = user['user_permissions']
        assert user_permissions == ["child read only"]

        # Delete permission
        rv = self.rest_driver.Delete('/users/{}/permission/{}'.format(user_id, 'child read only'))
        assert rv.status_code == 200
        user = json.loads(rv.text)['data']
        user_permissions = user['user_permissions']
        assert user_permissions == []

        # Create permission failure
        rv = self.rest_driver.Post(
            '/users/{}/permission'.format(user_id),
            data=json.dumps({'permission': 'invalid permission'}),
        )
        assert rv.status_code == 500

    def test_duplicate_user_creation(self):
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test1.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test1.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 400

    def test_user_uniqueness_constraint(self):
        # CREATE a user
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test1.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        user_id = data['user_id']

        # DELETE the user
        rv = self.rest_driver_customers.Delete('/customers/{}/users/{}'.format(UUID, user_id))
        assert rv.status_code == 200

        # CREATE a user with the same email as the deleted user
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test1.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['user_id'] != user_id

    def test_get_qr_code(self):

        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test1.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )

        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['email'] == '{}@test1.com'.format(self.user)

        rv = self.rest_driver.Get('/users/{}/codes'.format(data['user_id']))
        rv_no_such_user = self.rest_driver.Get('/users/DOESNOTEXIST/codes')

        if not configuration.ENABLE_TFA:
            assert rv.status_code == 404
            assert rv_no_such_user.status_code == 404
        else:
            data = json.loads(rv.text)['data']
            LOGGER.debug('data: {}'.format(data))
            assert rv.status_code == 200
            assert 'otp_secret' in data
            assert 'qrcode' in data

            # check that qrcode was generated correctly
            otp_secret = data['otp_secret']
            qrcode = data['qrcode']
            email = data['email']
            assert security.generate_otp_qrcode(email, otp_secret), qrcode

            success = json.loads(rv_no_such_user.text)['success']
            assert success is False

    def test_get_and_modify_user(self):
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test1.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['email'] == '{}@test1.com'.format(self.user)
        user_id = data['user_id']

        rv = self.rest_driver.Get('/users/{}'.format(user_id))
        data = json.loads(rv.text)['data']
        assert data['email'] == '{}@test1.com'.format(self.user)
        assert data['show_onboarding'] is True

        rv = self.rest_driver.Post(
            '/users/{}'.format(user_id),
            data=json.dumps({'first_name': 'whatis', 'last_name': 'mylastname'}),
        )
        data = json.loads(rv.text)['data']
        assert rv.status_code == 200
        assert data['first_name'] == 'whatis'
        assert data['last_name'] == 'mylastname'
        assert data['role'] == 'admin'
        assert data['show_onboarding'] is True

        rv = self.rest_driver.Get('/users/{}'.format(user_id))
        data = json.loads(rv.text)['data']

        assert rv.status_code == 200
        assert data['first_name'] == 'whatis'
        assert data['last_name'] == 'mylastname'
        assert data['role'] == 'admin'
        assert data['show_onboarding'] is True

        rv_no_such_user = self.rest_driver.Get('/users/DOESNOTEXIST')
        assert rv_no_such_user.status_code == 400, 'Failed to Get user by id'

    def test_get_user_codes(self):
        for i, role in enumerate(USER_ROLES):
            rv = self.rest_driver.Get('/users/{}/codes/'.format(i + 1))

            if not configuration.ENABLE_TFA:
                assert rv.status_code == 404

            else:
                assert rv.status_code == 200
                data = json.loads(rv.text)['data']

                assert data['customer_id'] == UUID
                assert data['otp_secret'] == 'xxx'
                assert data['qrcode'] == security.generate_otp_qrcode(
                    data['email'], data['otp_secret']
                )

    def test_request_reset(self):
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test1.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200
        rv = self.rest_driver.Post(
            '/users/request/reset/',
            data=json.dumps(dict(email='{}@test1.com'.format(self.user), portal_version='bikini')),
        )
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['email'] == '{}@test1.com'.format(self.user)

        for i in range(configuration.MAX_RESET_REQUESTS - 1):
            rv = self.rest_driver.Post(
                '/users/request/reset/',
                data=json.dumps(
                    dict(email='{}@test1.com'.format(self.user), portal_version='bikini')
                ),
            )
        assert json.loads(rv.text)['error'] == 'This user cannot request any more password resets.'
        assert rv.status_code == 403

    def test_one_time_url(self):
        rv = self.rest_driver.Get('/users/once/{}'.format(str(uuid4())))
        assert rv.status_code == 410
        data = json.loads(rv.text)
        assert data['success'] is False

        rv = self.rest_driver.Post(
            '/users/once/{uuid}'.format(uuid=str(uuid4())), data=json.dumps({})
        )
        assert rv.status_code == 400

    def test_privileged_authenticate_password_expired(self):
        email = user_utils.PRIVILEGED_USERS[0]
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': user_utils.PRIVILEGED_USERS[0],
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200

        caliber_bb.POSTGRES_SERVER.SqlCmd(
            "UPDATE password_history SET created_at = created_at - interval '95 days';"
        )

        if configuration.ENABLE_TFA:
            rv = self.rest_driver.Post(
                '/users/authenticate/',
                data=json.dumps({'email': email, 'password': 'whysosassy', 'token': '123456',}),
            )
            data = json.loads(rv.text)
            LOGGER.info(f'Password expired login data: {data}')
            assert data['success'] == 'success'
            assert data['data']['email'] == email

    def test_authenticate_password_expired(self):
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test1.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200

        caliber_bb.POSTGRES_SERVER.SqlCmd(
            "UPDATE password_history SET created_at = created_at - interval '95 days';"
        )

        if configuration.ENABLE_TFA:
            rv = self.rest_driver.Post(
                '/users/authenticate/',
                data=json.dumps(
                    {
                        'email': '{}@test1.com'.format(self.user),
                        'password': 'whysosassy',
                        'token': '123456',
                    }
                ),
            )
            data = json.loads(rv.text)
            LOGGER.info(f'Password expired login data: {data}')
            assert rv.status_code == 403  # Password expired
        else:
            rv = self.rest_driver.Post(
                '/users/authenticate/',
                data=json.dumps(
                    {
                        'email': '{}@test1.com'.format(self.user),
                        'password': 'whysosassy',
                        'token': '123456',
                    }
                ),
            )

            data = json.loads(rv.text)
            LOGGER.info(f'Password expired login data: {data}')
            assert rv.status_code == 403
            assert data['success'] is False
            for _ in range(configuration.MAX_FAILURE_COUNT - 1):
                rv = self.rest_driver.Post(
                    '/users/authenticate/',
                    data=json.dumps(
                        {
                            'email': '{}@test1.com'.format(self.user),
                            'password': 'whysowrong',
                            'token': '123456',
                        }
                    ),
                )
            assert rv.status_code == 403

    def test_change_customer_user_password(self):
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test22.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200
        user_id = json.loads(rv.text)['data']['user_id']

        rv = self.rest_driver_customers.Put(
            '/customers/{}/users/{}/password'.format(UUID, user_id),
            data=json.dumps({'password': 'whysosassy'}),  # Same as before
        )
        assert rv.status_code == 403

        rv = self.rest_driver_customers.Put(
            '/customers/{}/users/{}/password'.format(UUID, user_id),
            data=json.dumps({'password': 'whysosassy2'}),  # New Password
        )
        assert rv.status_code == 200

    def test_authenticate(self):
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test1.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200

        if configuration.ENABLE_TFA:
            rv = self.rest_driver.Post(
                '/users/authenticate/',
                data=json.dumps(
                    {
                        'email': '{}@test1.com'.format(self.user),
                        'password': 'whysosassy',
                        'token': '123456',
                    }
                ),
            )
            data = json.loads(rv.text)
            assert data['success'] == 'success'
            assert data['data']['email'] == '{}@test1.com'.format(self.user)
        else:
            rv = self.rest_driver.Post(
                '/users/authenticate/',
                data=json.dumps(
                    {
                        'email': '{}@test1.com'.format(self.user),
                        'password': 'whysowrong',
                        'token': '123456',
                    }
                ),
            )

            assert rv.status_code == 403
            data = json.loads(rv.text)
            assert data['success'] is False
            for i in range(configuration.MAX_FAILURE_COUNT - 1):
                rv = self.rest_driver.Post(
                    '/users/authenticate/',
                    data=json.dumps(
                        {
                            'email': '{}@test1.com'.format(self.user),
                            'password': 'whysowrong',
                            'token': '123456',
                        }
                    ),
                )
            assert rv.status_code == 403

    @caliber_bb.local_only
    def test_manage_features(self):

        caliber_bb.POSTGRES_SERVER.create_feature({'name': 'test', 'description': 'test'})
        caliber_bb.POSTGRES_SERVER.create_feature(
            {'name': 'test_false', 'description': 'test false'}
        )
        caliber_bb.POSTGRES_SERVER.create_feature({'name': 'test_real', 'description': 'test real'})

        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test1.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )

        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['email'] == '{}@test1.com'.format(self.user)
        user_id = data['user_id']

        rv = self.rest_driver.Get('/users/1/features')
        data = json.loads(rv.text)
        assert rv.status_code == 200
        assert data['data'] == {}

        rv = self.rest_driver.Post(
            '/users/{}/features'.format(user_id),
            data=json.dumps({'features': {'test': True, 'test_false': False, 'test_real': True}}),
        )
        data = json.loads(rv.text)
        assert data['context']['data']['features'] == {
            'test': True,
            'test_false': False,
            'test_real': True,
        }

    def test_reset_2fa(self):
        """
        test to ensure the reset_2fa endpoint is working
        """
        caliber_bb.POSTGRES_SERVER.cursor.execute("SELECT email, otp_secret, id FROM users;")
        before_list = caliber_bb.POSTGRES_SERVER.cursor.fetchall()
        before_otps = [user[1] for user in before_list]
        before_unique_otp_secrets = len(set(before_otps))

        db.reset_2fa(user_id=1, otp_secret='AAAAAAAAAAAAAAAA')

        caliber_bb.POSTGRES_SERVER.cursor.execute("SELECT email, otp_secret, id FROM users;")
        after_list = caliber_bb.POSTGRES_SERVER.cursor.fetchall()
        after_otps = [user[1] for user in after_list]
        # get the number of unique otp_tokens
        after_unique_otp_secrets = len(set(after_otps))

        # compare the number of unique before vs after the query gets run
        assert before_unique_otp_secrets == after_unique_otp_secrets

    # User notifications create and read ---------------------------------------
    def test_user_notifications_crud(self):
        '''
        Test "fetch notifications"
        '''
        LOGGER.info('Test "fetch notifications"')
        rv = self.rest_driver.Post(
            '/users/create/',
            data=json.dumps(
                {
                    'email': '{}@test1.com'.format(self.user),
                    'customer_id': UUID,
                    'password': 'whysosassy',
                    'role': 'admin',
                    'first_name': self.user,
                    'last_name': 'sassy',
                }
            ),
        )
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        user_id = data['user_id']

        '''
        Test "create notification"
        '''
        LOGGER.info('Test "create notification"')
        rv = self.rest_driver.Post(
            '/users/{}/notifications'.format(user_id),
            data=json.dumps(
                {
                    "payload": "{\"url\":\"https://horizon.area1security.com/downloads/21\"}",
                    "type": "download",
                    "user_id": user_id,
                }
            ),
        )
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['payload'] == ["{\"url\":\"https://horizon.area1security.com/downloads/21\"}"]
        assert data['type'] == 'download'
        assert data['user_id'] == user_id

        '''
        Test "fetch all notifications"
        '''
        LOGGER.info('Test "fetch all notifications"')
        rv = self.rest_driver.Get(f'/users/{user_id}/notifications')
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert len(data) == 1
        assert data[0]['payload'] == [
            "{\"url\":\"https://horizon.area1security.com/downloads/21\"}"
        ]
        assert data[0]['type'] == 'download'
        assert data[0]['user_id'] == user_id

        user_notification_id = data[0]['id']

        '''
        Test "get notification by ID"
        '''
        LOGGER.info('Test "fetch notification by ID"')
        rv = self.rest_driver.Get(f'/users/{user_id}/notifications/{user_notification_id}')
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['id'] == user_notification_id
        assert data['user_id'] == user_id

        '''
        Test "mark notification as read"
        '''
        LOGGER.info('Test "mark notification as read"')
        rv = self.rest_driver.Post(
            f'/users/{user_id}/notifications/{user_notification_id}/read', data=json.dumps({}),
        )
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['read_at'] != 'Thu, 01 Jan 1970 00:00:00 GMT'

        '''
        Test "mark notification as dismissed"
        '''
        LOGGER.info('Test "mark notification as dismissed"')
        rv = self.rest_driver.Post(
            f'/users/{user_id}/notifications/{user_notification_id}/dismiss', data=json.dumps({}),
        )
        assert rv.status_code == 200
        data = json.loads(rv.text)['data']
        assert data['dismissed_at'] != 'Thu, 01 Jan 1970 00:00:00 GMT'
