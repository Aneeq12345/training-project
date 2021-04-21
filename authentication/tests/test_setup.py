from django.contrib.auth.models import User
from django.urls import reverse
from faker import Faker
from rest_framework.test import APITestCase


class PositiveTestSetUp(APITestCase):

    def setUp(self):
        self.register_url = reverse('auth_register')
        self.login_url = reverse('auth_login')
        self.fake = Faker()

        self.user_data = {
            'email': self.fake.email(),
            'username': self.fake.email().split('@')[0],
            'password': self.fake.email(),
        }
        self.user_data['password2'] = self.user_data['password']
        return super().setUp()

    def tearDown(self):
        return super().tearDown()


class NegativeTestSetUp(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth_register')
        self.login_url = reverse('auth_login')
        self.fake = Faker()

        self.user_data = {
            'email': self.fake.email(),
            'username': self.fake.email().split('@')[0],
            'password': self.fake.email(),
        }
        self.user_data['password2'] = self.user_data['password']
        self.user_data_email_invalid = {
            'email': "abcgmail.com",
            'password': 'pass@123'
        }
        self.user_data_password_invalid = {
            'email':  self.fake.email(),
            'password': 'pass',
            'password2': 'pass'
        }
        self.user_data_login = {
            'email':  self.fake.email(),
            'password': 'pass',
            'password2': 'pass'
        }

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
