from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        help_texts = {
            'group': 'Выберите группу',
            'text': 'Введите сообщение',
        }
        fields = ('text', 'group', 'image')


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        help_texts = {
            'text': 'введите текст комментария',
        }
        fields = ('text',)
