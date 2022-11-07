import tempfile

from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class TaskPagesTestsContext(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.user = User.objects.create_user(username='author')
        cls.user_2 = User.objects.create_user(username='Not_author')

        for i in range(12):
            Post.objects.create(
                author=cls.user,
                text=str(i),
            )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user,
            image=SimpleUploadedFile(
                name='small.gif',
                content=(
                    b'\x47\x49\x46\x38\x39\x61\x02\x00'
                    b'\x01\x00\x80\x00\x00\x00\x00\x00'
                    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                    b'\x0A\x00\x3B'
                ),
                content_type='image/gif',
            )
        )
        cls.follow = Follow.objects.get_or_create(
            user=cls.user_2,
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_2)

    def test_follow_page_without_following_for_autorized_client(self):
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_add_follow_for_autorized_client_not_author(self):
        response = self.authorized_client_not_author.get(reverse(
            'posts:follow_index'
        ))
        self.assertEqual(len(response.context['page_obj']), 10)
        self.assertIn(self.post, response.context['page_obj'])

    def test_chek_follow_for_autorized_client(self):
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_unfollow_for_autorized_client_not_author(self):
        Follow.objects.all().delete()
        response = self.authorized_client_not_author.get(reverse(
            'posts:follow_index'
        ))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_cache_created_for_guest_client(self):
        response_first = self.guest_client.get(reverse('posts:index'))
        Post.objects.all().delete
        response_cached = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response_first.content, response_cached.content)
        cache.clear()
        response_uncached = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(response_first.content, response_uncached.content)

    def test_image_in_context_post_detail(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(response.context['concrete_post'], self.post)

    def test_image_in_context_profile(self):
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'author'}
        ))
        total = ''
        for post in response.context['posts']:
            if post == self.post:
                total = post
        self.assertEqual(total, self.post)

    def test_image_in_context_for_authorized_client(self):
        terms = {'main': reverse('posts:index'),
                 'profile':
                 reverse('posts:profile', kwargs={'username': 'author'}),
                 'group':
                 reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
                 }
        for name, reverse_name in terms.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse_name)
                total = ''
                for post in response.context['posts']:
                    if post == self.post:
                        total = post
                self.assertEqual(total, self.post)

    def test_index_show_correct_context_for_guest_client(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(
            list(response.context['page_obj']), list(Post.objects.all()[:10])
        )

    def test_group_list_show_correct_context(self):
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        group = get_object_or_404(Group, slug=self.group.slug)
        group_posts = group.posts.all()[:10]
        self.assertEqual(list(response.context['page_obj']), list(group_posts))

    def test_profile_show_correct_context(self):
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        author = get_object_or_404(User, username=self.post.author)
        author_posts = author.posts.all()[:10]
        self.assertEqual(
            list(response.context['page_obj']), list(author_posts)
        )

    def test_concrete_post_exist_in_context(self):
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertTrue('concrete_post' in response.context)
        post_from_response = response.context['concrete_post']
        self.assertEqual(
            post_from_response.text, self.post.text
        )

    def test_post_detail_show_correct_context_for_guest_client(self):
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post_from_response = response.context['concrete_post']
        self.assertEqual(
            post_from_response.text, self.post.text
        )
        self.assertEqual(
            post_from_response.author, self.post.author
        )
        self.assertEqual(
            post_from_response.group, self.post.group
        )

    def test_create_edit_show_correct_context_for_authorized_client(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_show_correct_context_for_authorized_client(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_check_group_in_pages_for_authorized_client(self):
        form_fields = {
            reverse('posts:index'): Post.objects.get(group=self.post.group),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): Post.objects.get(group=self.post.group),
            reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ): Post.objects.get(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertIn(expected, form_field)

    def test_check_group_is_not_included_in_the_wrong_group(self):
        form_fields = {
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): Post.objects.exclude(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertNotIn(expected, form_field)


class TaskPagesTestsPaginator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.user = User.objects.create_user(username='author')
        cls.user_2 = User.objects.create_user(username='Not_author')
        for i in range(13):
            Post.objects.create(
                author=cls.user,
                text=str(i),
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_len_pages_for_guest_client(self):
        terms = {
            '1': 10,
            '2': 3,
        }
        for num, length in terms.items():
            with self.subTest(num=num):
                response = self.guest_client.get(
                    reverse('posts:index') + f'?page={num}')
                self.assertEqual(len(response.context['page_obj']), length)
                response = self.guest_client.get(
                    reverse('posts:group_list',
                            kwargs={'slug': self.group.slug}) + f'?page={num}'
                )
                self.assertEqual(len(response.context['page_obj']), length)
                response = self.guest_client.get(
                    reverse('posts:profile',
                            kwargs={'username': 'author'}) + f'?page={num}'
                )
                self.assertEqual(len(response.context['page_obj']), length)


class TaskPagesTestsTemplates(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.user = User.objects.create_user(username='author')
        cls.user_2 = User.objects.create_user(username='Not_author')
        for i in range(12):
            Post.objects.create(
                author=cls.user,
                text=str(i),
            )

        cls.post = Post.objects.create(
            author=cls.user, text='Тестовый пост', group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_2)
        self.templates_page_names_authorized_client = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test_slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'author'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }

    def test_pages_uses_correct_template_for_authorized_client(self):
        templates_dict = self.templates_page_names_authorized_client
        for reverse_name, template in templates_dict.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
