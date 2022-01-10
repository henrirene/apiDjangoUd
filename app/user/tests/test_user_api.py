from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users APIU
    (public)"""
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is success"""
        payload = {
            'email': 'test@example.com',
            'password': 'password',
            'name': 'xxx'
        }

        # Make a post request to create a user
        response = self.client.post(CREATE_USER_URL, payload)

        # Checl that request is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))

        # Check that password is not returned in the response
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        '''Test creating a user that already exists fails'''
        payload = {
            'email': 'test@example.com',
            'password': 'password',
            'name': 'xxx',
        }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)

        # Check that the response is "Bad Request" as the user already exists
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        '''Test that the password is more than 5 characters'''
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test',
        }
        response = self.client.post(CREATE_USER_URL, payload)

        # Check the response is HTTP_400_BAD_REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check the user was never created
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        '''Test that the token has been created for the user'''
        payload = {
            'email': 'test@example.com',
            'password': 'testpass',
            'name': 'Test',
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that the token is not created if
        invalid credentials are provided"""

        create_user(email='test@london.uk', password='testpass')

        payload = {
            'email': 'test@london.uk',
            'password': 'wrong',
            'name': 'Test',
        }

        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that the token is not created if user dosen't exist"""

        payload = {
            'email': 'test@london.uk',
            'password': 'testpass',
            'name': 'Test',
        }

        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthenticate(self):
            """Test that authentication is required frr user"""
            res = self.client.get(ME_URL)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication """

    def setUp(self):
        self.user = create_user(
            email='test@london.uk',
            password='testpass',
            name='name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retreiving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.password, payload['password'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
