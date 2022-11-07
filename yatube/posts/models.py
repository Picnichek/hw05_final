from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='имя сообщества')
    slug = models.SlugField(unique=True, verbose_name='ссылка')
    description = models.TextField(verbose_name='Описание сообщества')

    class Meta:
        verbose_name = 'Группы'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return f'<Сообщество: {self.title}>'


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст публикации', help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Сообщество',
        help_text='Группа, к которой будет' ' относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return f'{self.text[:15]}'

    class Meta:
        verbose_name = 'Публикации'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст коментария', help_text='Введите текст коментария'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария',
    )

    class Meta:
        ordering = ['-created']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f'{self.text[:15]}'


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')

    def __str__(self):
        return f'{self.text[:15]}'
