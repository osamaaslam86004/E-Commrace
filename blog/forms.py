from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget
from django import forms

from blog.models import Comment, Post


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Post
        fields = [
            "title",
            "slug",
            "status",
            "meta_description",
            "content",
        ]

    labels = {
        "title": "Title",
        "slug": "Slug",
        "status": "Status",
        "content": "Content",
        "meta_description": "Meta-Description",
    }

    placeholders = {
        "title": "Enter the title",
        "slug": "Enter the slug",
        "status": "Select the status",
        "content": "Write Your content Here......",
        "meta_description": "Write 160 Characters Seo-Optimized Meta-Description",
    }

    widgets = {
        "title": forms.TextInput(attrs={"class": "form-control"}),
        "slug": forms.TextInput(attrs={"class": "form-control"}),
        "meta_description": forms.TextInput(attrs={"class": "form-control"}),
        # "content": forms.Textarea(attrs={"class": "form-control"}),
        "status": forms.Select(attrs={"class": "form-control"}),
    }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            "body",
        ]
        exclude = ["created_on", "active", "user_comment", "post"]

    labels = {
        "body": "Comment Body",
    }

    placeholders = {
        "body": "Enter your comment",
    }

    widgets = {
        "body": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    }


class CommentFormAdmin(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            "active",
            "comments_user",
            "post",
            "body",
        ]
