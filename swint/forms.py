from django import forms
from .models import CommentSwint

# Django提供了两个可以创建表单的基本类：
# Form: 允许你创建一个标准表单。
# ModelForm: 允许你创建一个可用于创建或者更新model实例的表单。


class EmailArticleForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentSwint
        fields = ('name', 'email', 'content')
