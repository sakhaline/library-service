from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken


class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "password": "testpassword",
        }

    def test_create_user(self):
        user = get_user_model().objects.create_user(**self.user_data)

        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))

    def test_create_superuser(self):
        superuser = get_user_model().objects.create_superuser(**self.user_data)

        self.assertEqual(superuser.email, self.user_data["email"])
        self.assertTrue(superuser.check_password(self.user_data["password"]))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('user:create')
        self.token_url = reverse('user:token_obtain_pair')
        self.refresh_token_url = reverse('user:token_refresh')
        self.verify_token_url = reverse('user:token_verify')
        self.me_url = reverse('user:manage')

        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpassword',
        }

        self.user = get_user_model().objects.create_user(**self.user_data)

    def test_token_obtain(self):
        response = self.client.post(self.token_url, {'email': self.user_data['email'], 'password': self.user_data['password']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):
        refresh_token = RefreshToken.for_user(self.user)
        response = self.client.post(self.refresh_token_url, {'refresh': str(refresh_token)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_verify(self):
        refresh_token = RefreshToken.for_user(self.user)
        access_token = refresh_token.access_token
        response = self.client.post(self.verify_token_url, {'token': str(access_token)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manage_user(self):
        refresh_token = RefreshToken.for_user(self.user)
        access_token = refresh_token.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])
