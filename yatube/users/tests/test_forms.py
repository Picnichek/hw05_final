from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_signup(self):
        form_data = {
            'first_name': 'Ivan',
            'last_name': 'Ivanov',
            'username': 'Ivanich',
            'email': 'Ivan@ivanich.com',
            'password1': 'StrongPass123@',
            'password2': 'StrongPass123@',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )
        self.assertTrue(User.objects.filter(username='Ivanich').exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)
