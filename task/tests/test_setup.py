from rest_framework.test import APITestCase
from django.urls import reverse

from faker import Faker
from ..models import Task


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

        self.task_data = {
            'title': "task1",
            'description': "task1 inserted",
            'due_date': "2021-04-20T10:41:37.322000Z",
        }
        return super().setUp()

    def tearDown(self):
        return super().tearDown()
