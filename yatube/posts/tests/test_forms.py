import shutil
import tempfile

from django.conf import settings
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post, User

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            text='тестовый текст',
            author=cls.user,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_comment_for_autorized_user(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'комментарий',
        }
        response = self.authorized_client.post(reverse(
            'posts:add_comment', kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.first()
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(comment.text, 'комментарий')

    def test_create_comment_for_guest_client(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'комментарий',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={"post_id": self.post.id}),
            data=form_data, follow=True)
        comment = Comment.objects.first()
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertIsNone(comment)

    def test_create_post_with_picture(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'пост с картинкой',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': self.user})
        )
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(uploaded, form_data['image'])
        self.assertEqual(post.image.name, 'posts/' + form_data['image'].name)

    def test_create_post_for_authorized_client(self):
        posts_count = Post.objects.count()
        form_data = {'text': 'второй тест текст', 'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post = Post.objects.all().latest('id')
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_with_group_for_authorized_client(self):
        posts_count = Post.objects.count()
        form_data = {"text": "Изменяем текст", "group": self.group.id}
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=self.post.id)
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id}),
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_without_group_for_authorized_client(self):
        posts_count = Post.objects.count()
        form_data = {"text": "Изменяем текст"}
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=self.post.id)
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id}),
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post.text, form_data['text'])
        self.assertIsNone(post.group)
        self.assertEqual(post.author, self.user)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_is_not_for_guest_client(self):
        posts_count = Post.objects.count()
        form_data = {"text": "Изменяем текст", "group": self.group.id}
        response = self.guest_client.post(
            reverse("posts:post_edit", args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=self.post.id)
        login_url = reverse('users:login')
        edit_url = reverse('posts:post_edit', args=({self.post.id}))
        redirect_url = f'{login_url}?next={edit_url}'
        self.assertRedirects(
            response, redirect_url
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post.text, self.post.text)
        self.assertIsNone(post.group)
        self.assertEqual(post.author, self.user)
        self.assertEqual(response.status_code, HTTPStatus.OK)
