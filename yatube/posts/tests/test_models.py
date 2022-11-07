from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='1' * 20,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_object_name = self.post.text[:15]
        self.assertEqual(expected_object_name, str(self.post))
        expected_object_name = f'<Сообщество: {self.group.title}>'
        self.assertEqual(expected_object_name, str(self.group))

    def test_post_verbose_name_and_help_text(self):
        verbose_names = {
            'text': 'Текст публикации',
            'group': 'Сообщество',
            'pub_date': 'Дата публикации',
            'author': 'Автор публикации',
            'group': 'Сообщество',
        }
        for value, expected in verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected)
        help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for value, expected in help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text, expected)

    def test_group_verbose_names(self):
        verbose_names = {
            'title': 'имя сообщества',
            'slug': 'ссылка',
            'description': 'Описание сообщества',
        }
        for value, expected in verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.group._meta.get_field(value).verbose_name, expected)
