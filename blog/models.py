from ckeditor.fields import RichTextField
from django.db import models
from django.urls import reverse

from Homepage.models import CustomUser

STATUS = ((0, "Draft"), (1, "Publish"))


class Post(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=500, unique=True, primary_key=True)
    meta_description = models.CharField(
        max_length=160, unique=False, default="meta description"
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        name="post_admin",
        related_name="blog_posts",
    )
    updated_on = models.DateTimeField(auto_now=True, editable=True)
    content = RichTextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True, null=True)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self) -> str:
        return self.title

    def admin_post_count(self, user) -> list[int]:
        publish = Post.objects.filter(post_admin=user, status="1").count()
        draft = Post.objects.filter(post_admin=user, status="0").count()
        total = publish + draft
        return [publish, draft, total]

    def get_absolute_url(self):
        return reverse("blog:live_post", kwargs={"slug": self.slug})


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user_comment = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, name="comments_user"
    )
    body = RichTextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return f'Comment "{self.body}" by {self.comments_user.username}'
