import pytest
from tests.blog.test_blog_factory import PostFactory, CommentFactory
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from blog.models import Post, Comment
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

CustomUser = get_user_model()


@pytest.fixture
def create_admin_user():
    return CustomUserOnlyFactory(user_type="ADMINISTRATOR")


@pytest.fixture
def create_post_batch(create_admin_user):
    def _create_post_batch():
        admin = create_admin_user
        post_batch = PostFactory.create_batch(5, post_admin=admin)
        return admin, post_batch

    return _create_post_batch


@pytest.fixture
def build_setup_for_comment(create_admin_user):
    def _build_setup_for_comment():
        admin = create_admin_user
        post = PostFactory(post_admin=admin)
        return admin, post

    return _build_setup_for_comment


@pytest.mark.django_db
class Test_PostModel:
    def test_post_creation(self, create_admin_user):
        admin = create_admin_user
        post = PostFactory(post_admin=admin)
        assert post.title
        assert post.slug
        assert post.meta_description
        assert post.post_admin
        assert post.content

    def test_post_status(self, create_admin_user):
        admin = create_admin_user
        post = PostFactory(post_admin=admin)
        assert post.status == 1

    def test_post_admin_post_count(self, create_post_batch):
        admin, post_batch = create_post_batch()

        get_all_post = Post.objects.select_related("post_admin").filter(
            post_admin=admin
        )

        draft = get_all_post.filter(status=0).count()
        publish = get_all_post.filter(status=1).count()

        for instance in get_all_post:
            assert instance.admin_post_count(admin) == [
                publish,
                draft,
                publish + draft,
            ]

    def test_post_on_cascade(self, create_admin_user):
        admin = create_admin_user
        post = PostFactory(post_admin=admin)
        admin.delete()
        assert not CustomUser.objects.filter(id=admin.id).exists()
        assert not Post.objects.filter(post_admin=admin).exists()


@pytest.mark.django_db
class Test_CommentModel:
    def test_comment_creation(self, build_setup_for_comment):
        # getting the data
        admin, post = build_setup_for_comment()

        # create a comment for the Post
        comment = CommentFactory(post=post, comments_user=admin)

        # Assertions
        assert comment in post.comments.all()
        assert comment.comments_user.username == admin.username
        assert len(comment.body) > 0

    def test_comment_str(self, build_setup_for_comment):
        # getting the data
        admin, post = build_setup_for_comment()

        # create a comment for the Post
        comment = CommentFactory(post=post, comments_user=admin)

        # create a comment for the Post
        comment = CommentFactory(post=post, comments_user=admin)
        assert (
            str(comment)
            == f'Comment "{comment.body}" by {comment.comments_user.username}'
        )

    def test_comment_on_cascade_with_customuser(self, build_setup_for_comment):
        # getting the data
        admin, post = build_setup_for_comment()

        # create a comment for the Post
        comment = CommentFactory(post=post, comments_user=admin)

        # delete the user to trigger 'on_cascade'
        admin.delete()

        # Assertions
        assert comment not in post.comments.all()
        assert not Comment.objects.filter(comments_user=admin).exists()

    def test_comment_on_cascade_with_Post(self, build_setup_for_comment):
        # getting the data
        admin, post = build_setup_for_comment()

        # create a comment for the Post
        comment = CommentFactory(post=post, comments_user=admin)

        # delete the user to trigger 'on_cascade'
        post.delete()

        # Assertions
        assert not Comment.objects.filter(post=post).exists()
