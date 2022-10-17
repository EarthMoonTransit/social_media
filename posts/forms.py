from django import forms
from .models import *


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].required = True

    class Meta:
        model = Post
        fields = ['group', 'text', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']