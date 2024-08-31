import pytest
from django.utils.text import slugify
from blog.models import Post, Comment
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory, fake
from tests.blog.test_blog_factory import PostFactory, CommentFactory
from blog.forms import PostForm, CommentForm


@pytest.fixture
def create_user():
    return CustomUserOnlyFactory.create()


@pytest.fixture
def create_post(create_user):
    return PostFactory.create(post_admin=create_user)


@pytest.fixture
def create_comment(create_post, create_user):
    return CommentFactory.create(post=create_post, comments_user=create_user)


@pytest.mark.django_db
class Test_PostForm:

    def test_post_form_valid(self, create_user):
        form_data = {
            "title": fake.sentence(nb_words=4),
            "slug": slugify(fake.sentence(nb_words=4)),
            "meta_description": fake.sentence(nb_words=10),
            "content": fake.paragraph(nb_sentences=3),
            "status": 1,
        }
        form = PostForm(data=form_data)
        assert form.is_valid()

    def test_post_form_save(self, create_user):
        form_data = {
            "title": fake.sentence(nb_words=4),
            "slug": slugify(fake.sentence(nb_words=4)),
            "meta_description": fake.sentence(nb_words=10),
            "content": fake.paragraph(nb_sentences=3),
            "status": 1,
        }
        form = PostForm(data=form_data)
        assert form.is_valid()
        post = form.save(commit=False)
        post.post_admin = create_user
        post.save()
        assert Post.objects.filter(title=form_data["title"]).exists()

    def test_post_form_slug_unique(self, create_user, create_post):
        form_data = {
            "title": fake.sentence(nb_words=4),
            "slug": create_post.slug,  # Duplicate slug
            "meta_description": fake.sentence(nb_words=10),
            "content": fake.paragraph(nb_sentences=3),
            "status": 1,
        }
        form = PostForm(data=form_data)
        assert not form.is_valid()
        assert "slug" in form.errors

    def test_post_form_title_max_length(self):
        form_data = {
            "title": "a" * 101,  # Exceeds max length
            "slug": slugify(fake.sentence(nb_words=4)),
            "meta_description": fake.sentence(nb_words=10),
            "content": fake.paragraph(nb_sentences=3),
            "status": 1,
        }
        form = PostForm(data=form_data)
        assert not form.is_valid()
        assert "title" in form.errors

    def test_post_form_meta_description_max_length(self):
        form_data = {
            "title": fake.sentence(nb_words=4),
            "slug": slugify(fake.sentence(nb_words=4)),
            "meta_description": "a" * 161,  # Exceeds max length
            "content": fake.paragraph(nb_sentences=3),
            "status": 1,
        }
        form = PostForm(data=form_data)
        assert not form.is_valid()
        assert "meta_description" in form.errors


@pytest.mark.django_db
class Test_CommentForm:

    def test_comment_form_valid(self, create_comment):
        form_data = {
            "body": fake.paragraph(nb_sentences=2),
        }
        form = CommentForm(data=form_data)
        assert form.is_valid()

    def test_comment_form_save(self, create_user, create_post):
        form_data = {
            "body": fake.paragraph(nb_sentences=2),
        }
        form = CommentForm(data=form_data)
        assert form.is_valid()

        comment = form.save(commit=False)

        comment.post = create_post
        comment.comments_user = create_user
        comment.save()
        assert Comment.objects.filter(body=form_data["body"]).exists()
