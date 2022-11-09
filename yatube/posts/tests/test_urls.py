from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.user = User.objects.create_user(username='author')
        cls.user_2 = User.objects.create_user(username='Not_author')
        cls.post = Post.objects.create(author=cls.user, text='Тестовый пост')
        cls.main = '/'
        cls.group = '/group/test/'
        cls.profile = '/profile/author/'
        cls.detail = '/posts/1/'
        cls.create = '/create/'
        cls.unexiting_page = '/unexiting_page/'
        cls.edit = '/posts/1/edit/'

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_2)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test/': 'posts/group_list.html',
            '/profile/author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexiting_page_for_guest_client(self):
        response = self.guest_client.get(self.unexiting_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_page_create_for_authorized_client(self):
        response = self.authorized_client.get(self.create)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_edit_post_for_authorized_client(self):
        response = self.authorized_client.get(self.edit)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/create_post.html')
        response = self.authorized_client_not_author.get(self.edit)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_response_for_guest_client(self):
        url_names = {
            self.main: HTTPStatus.OK,
            self.group: HTTPStatus.OK,
            self.profile: HTTPStatus.OK,
            self.detail: HTTPStatus.OK,
            self.create: HTTPStatus.FOUND,
            self.unexiting_page: HTTPStatus.NOT_FOUND,
            self.edit: HTTPStatus.FOUND,
        }
        for adress, status in url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, status)

    def test_get_response_for_authorized_client(self):
        url_names = {
            self.main: HTTPStatus.OK,
            self.group: HTTPStatus.OK,
            self.profile: HTTPStatus.OK,
            self.detail: HTTPStatus.OK,
            self.create: HTTPStatus.OK,
            self.unexiting_page: HTTPStatus.NOT_FOUND,
            self.edit: HTTPStatus.OK,
        }
        for adress, status in url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, status)

    def test_get_response_for_authorized_client_not_author(self):
        url_names = {
            self.main: HTTPStatus.OK,
            self.group: HTTPStatus.OK,
            self.profile: HTTPStatus.OK,
            self.detail: HTTPStatus.OK,
            self.create: HTTPStatus.OK,
            self.unexiting_page: HTTPStatus.NOT_FOUND,
            self.edit: HTTPStatus.FOUND,
        }
        for adress, status in url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client_not_author.get(adress)
                self.assertEqual(response.status_code, status)
