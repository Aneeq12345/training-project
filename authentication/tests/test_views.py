from .test_setup import PositiveTestSetUp, NegativeTestSetUp

from django.contrib.auth.models import User


class PostiveTestViews(PositiveTestSetUp):
    def test_user_register(self):
        res = self.client.post(
            self.register_url, self.user_data, format="json")
        self.assertEqual(res.data['payload']['email'], self.user_data['email'])
        self.assertEqual(res.data['success'], True)
        self.assertEqual(res.status_code, 201)

    def test_user_login(self):
        response = self.client.post(
            self.register_url, self.user_data, format="json")
        email = response.data['payload']['email']
        user = User.objects.get(email=email)
        user.save()
        res = self.client.post(self.login_url, self.user_data, format="json")
        self.assertEqual(res.status_code, 200)


class NegativeTestViews(NegativeTestSetUp):
    def test_user_cannot_register_with_no_data(self):
        res = self.client.post(self.register_url)
        self.assertEqual(res.status_code, 400)

    def test_user_register_email_invalid(self):
        res = self.client.post(
            self.register_url, self.user_data_email_invalid, format="json")
        self.assertEqual(res.data['success'], False)
        self.assertEqual(res.status_code, 400)

    def test_user_register_password_invalid(self):
        res = self.client.post(
            self.register_url, self.user_data_password_invalid,
            format="json")
        self.assertEqual(res.data['success'], False)
        self.assertEqual(res.status_code, 400)

    def test_user_login_email_invalid(self):
        response = self.client.post(
            self.register_url, self.user_data, format="json")
        email = response.data['payload']['email']
        user = User.objects.get(email=email)
        user.save()
        res = self.client.post(self.login_url, self.user_data_email_invalid,
                               format="json")
        self.assertEqual(res.status_code, 400)
