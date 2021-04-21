from .test_setup import PositiveTestSetUp
from django.urls import reverse
from django.contrib.auth.models import User


class PostiveTestViews(PositiveTestSetUp):
    def test_task_creation(self):
        response = self.client.post(
            self.register_url, self.user_data, format="json")
        email = response.data['payload']['email']
        user = User.objects.get(email=email)
        user.save()
        res_login = self.client.post(self.login_url, self.user_data,
                                     format="json")
        bearer = {'HTTP_AUTHORIZATION': 'Bearer {}'.format(
                res_login.data['payload']['token']['access'])}
        res = self.client.post(
            reverse('TaskList', kwargs={'uid': user.id}), self.task_data,
            **bearer, format="json")
        self.assertEqual(res.data['payload']['title'], self.task_data['title'])
        self.assertEqual(res.data['success'], True)
        self.assertEqual(res.status_code, 201)
    
    def test_get_user_tasks(self):
        response = self.client.post(
            self.register_url, self.user_data, format="json")
        email = response.data['payload']['email']
        user = User.objects.get(email=email)
        user.save()
        res_login = self.client.post(self.login_url, self.user_data,
                                     format="json")
        bearer = {'HTTP_AUTHORIZATION': 'Bearer {}'.format(
                res_login.data['payload']['token']['access'])}
        res = self.client.post(
            reverse('TaskList', kwargs={'uid': user.id}), self.task_data,
            **bearer, format="json")
        res_get = self.client.get(
            reverse('TaskList', kwargs={'uid': user.id}),
            **bearer, format="json")
        self.assertEqual(res_get.data['success'], True)
        self.assertEqual(res_get.status_code, 200)
