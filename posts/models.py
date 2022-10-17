from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    class Meta:
        ordering = ['-pub_date']

    text = models.TextField( verbose_name='Текст')
    pub_date = models.DateTimeField('date published',
                                    auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(User,
                               null=True,
                               on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              blank=True, null=True,
                              verbose_name='Группа',
                              help_text='Выберите группу')
    image = models.ImageField(upload_to='posts/',
                              blank=True, null=True,
                              verbose_name='Картинка',)

    def __str__(self):
       return self.text


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             null=True,
                             related_name='comments')
    author = models.ForeignKey(User,
                               null=True,
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(blank=True)
    created = models.DateTimeField('date published', auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             null=True,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User,
                               null=True,
                               on_delete=models.CASCADE,
                               related_name='following')
