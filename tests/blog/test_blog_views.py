import pytest
from django.urls import reverse
from django_mock_queries.query import MockSet, MockModel
from unittest.mock import patch
from blog.models import Post, Comment
from blog.forms import PostForm, CommentForm
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.blog.test_blog_factory import PostFactory, CommentFactory
from faker import Faker
import logging
from django.utils.text import slugify
from django.contrib import messages

fake = Faker()
# Disable Faker DEBUG logging
faker_logger = logging.getLogger("faker")
faker_logger.setLevel(logging.WARNING)


@pytest.fixture()
def admin_user():
    return CustomUserOnlyFactory(user_type="ADMINISTRATOR")


@pytest.mark.django_db
def test_post_list_view(mocker, client, admin_user):
    user = admin_user

    client.force_login(user)

    # Create a mock queryset
    mock_post1 = MockModel(id=1, title="Post 1", status=1)
    mock_post2 = MockModel(id=2, title="Post 2", status=1)
    mock_qs = MockSet(mock_post1, mock_post2, model=Post)

    # Patch the Post.objects.filter() to return our mock queryset
    mocker.patch("blog.models.Post.objects.filter", return_value=mock_qs)

    response = client.get(reverse("blog:post_list"))

    assert response.status_code == 200
    assert "blog_posts" in response.context
    assert len(response.context["blog_posts"]) == 2
    assert response.context["blog_posts"][0].title == "Post 1"
    assert response.context["blog_posts"][1].title == "Post 2"
    assert "blog_home.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_my_posts_list_view_admin(mocker, client, admin_user):

    client.force_login(admin_user)

    # Create a mock queryset
    mock_post1 = MockModel(
        id=1, title="Post 1", status=1, post_admin=admin_user, created_on="2023-06-01"
    )
    mock_post2 = MockModel(
        id=2, title="Post 2", status=1, post_admin=admin_user, created_on="2023-06-02"
    )
    mock_qs = MockSet(mock_post1, mock_post2, model=Post)

    # Patch the Post.objects.filter() to return our mock queryset
    mocker.patch("blog.models.Post.objects.filter", return_value=mock_qs)

    response = client.get(
        reverse("blog:my_posts_list")
    )  # Assuming 'my_posts_list' is the URL name for the view

    assert response.status_code == 200
    assert "posts" in response.context
    assert len(response.context["posts"]) == 2
    assert response.context["posts"][1].title == "Post 1"
    assert response.context["posts"][0].title == "Post 2"
    assert "myposts.html" in [t.name for t in response.templates]


user_type_args_value = [
    ("SELLER", "SELLER"),
    ("CUSTOMER", "CUSTOMER"),
    ("MANAGER", "MANAGER"),
    ("CUSTOMER REPRESENTATIVE", "CUSTOMER REPRESENTATIVE"),
]


@pytest.mark.parametrize(
    "user_type", user_type_args_value, ids=[arg[1] for arg in user_type_args_value]
)
@pytest.mark.django_db
def test_my_posts_list_view_non_admin(client, user_type):
    non_admin_user = CustomUserOnlyFactory(user_type=user_type)

    client.force_login(non_admin_user)

    response = client.get(
        reverse("blog:my_posts_list")
    )  # Assuming 'my_posts_list' is the URL name for the view

    assert response.status_code == 200
    assert "user_email" in response.context
    assert response.context["user_email"] == non_admin_user.email
    assert "user_permission" in response.context
    assert "permission_denied.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_delete_post_view(mocker, admin_user, client):

    client.force_login(admin_user)

    # Create a post
    mock_post = PostFactory(post_admin=admin_user)

    # Patch the get_object_or_404 to return our mock post
    mocker.patch("blog.views.get_object_or_404", return_value=mock_post)

    # Patch the delete method
    with patch.object(Post, "delete") as mock_delete:
        response = client.post(
            reverse("blog:blog_post_delete", kwargs={"slug": mock_post.slug})
        )

        # Verify the delete method was called
        mock_delete.assert_called_once()

        # Check for redirection
        assert response.status_code == 302
        assert response.url == reverse("blog:my_posts_list")


@pytest.mark.parametrize(
    "user_type", ["SELLER", "CUSTOMER", "MANAGER", "CUSTOMER REPRESENTATIVE"]
)
@pytest.mark.django_db
def test_delete_post_view_non_admin(mocker, admin_user, client, user_type):

    non_admin_user = CustomUserOnlyFactory(user_type=user_type)

    client.force_login(non_admin_user)

    # Create a post
    mock_post = PostFactory(post_admin=admin_user)

    # Patch the get_object_or_404 to return our mock post
    mocker.patch("blog.views.get_object_or_404", return_value=mock_post)

    # Patch the delete method
    mock_delete = mocker.patch.object(mock_post, "delete")

    response = client.post(
        reverse("blog:blog_post_delete", kwargs={"slug": mock_post.slug})
    )  # Assuming 'delete_post' is the URL name for the view

    # Verify the delete method was not called
    mock_delete.assert_not_called()

    # Check for redirection to a permission denied page
    assert response.status_code == 200
    assert "permission_denied.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_update_post_success(mocker, client, admin_user):
    admin_user = CustomUserOnlyFactory(user_type="ADMINISTRATOR")

    client.force_login(admin_user)

    # Create a post
    mock_post = PostFactory(post_admin=admin_user)

    # Patch the get_object_or_404 to return our mock post
    mocker.patch("blog.views.get_object_or_404", return_value=mock_post)

    form_data = {
        "title": fake.sentence(nb_words=4),
        "slug": slugify(fake.sentence(nb_words=4)),
        "meta_description": fake.sentence(nb_words=10),
        "content": fake.paragraph(nb_sentences=3),
        "status": 1,
    }

    response = client.post(
        reverse("blog:blog_post_update", args=[mock_post.slug]), data=form_data
    )

    # Assert the expected behavior
    assert response.status_code == 302
    assert response.url == reverse("blog:live_post", args=[mock_post.slug])


@pytest.mark.django_db
def test_update_post_form_invalid(mocker, client, admin_user):
    admin_user = CustomUserOnlyFactory(user_type="ADMINISTRATOR")

    client.force_login(admin_user)

    # Create a post
    mock_post = PostFactory(post_admin=admin_user)

    # Patch the get_object_or_404 to return our mock post
    mocker.patch("blog.views.get_object_or_404", return_value=mock_post)

    form_data = {
        "title": fake.sentence(nb_words=4),
        "slug": slugify(fake.sentence(nb_words=4)),
    }

    response = client.post(
        reverse("blog:blog_post_update", args=[mock_post.slug]), data=form_data
    )

    # Assert the expected behavior
    assert response.status_code == 200
    assert "update_post.html" in [template.name for template in response.templates]
    assert response.context["form"].errors


@pytest.mark.parametrize(
    "user_type", ["SELLER", "CUSTOMER", "MANAGER", "CUSTOMER REPRESENTATIVE"]
)
@pytest.mark.django_db
def test_update_post_unauthorized(mocker, client, admin_user, user_type):
    non_admin_user = CustomUserOnlyFactory(user_type=user_type)

    client.force_login(non_admin_user)

    # Create a post
    mock_post = PostFactory(post_admin=admin_user)

    response = client.post(reverse("blog:blog_post_update", args=[mock_post.slug]))

    assert response.status_code == 200  # Assuming it should return a 403 Forbidden
    assert "permission_denied.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_update_comment_view_get(mocker, client):
    regular_user = CustomUserOnlyFactory(user_type="SELLER")

    client.force_login(regular_user)

    # Create a mock post and comment
    mock_post = PostFactory(post_admin=regular_user)
    mock_comment = CommentFactory(comments_user=regular_user)

    # Patch the get_object_or_404 to return our mock post and comment
    mocker.patch("blog.views.get_object_or_404", side_effect=[mock_post, mock_comment])

    response = client.get(
        reverse(
            "blog:update_comment",
            kwargs={"slug": mock_post.slug, "comment_id": mock_comment.id},
        )
    )

    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], CommentForm)
    assert response.context["form"].instance == mock_comment
    assert "update_comment.html" in [templates.name for templates in response.templates]


@pytest.mark.django_db
def test_update_comment_view_post_valid(mocker, admin_user, client):

    client.force_login(admin_user)

    # Create a mock post and comment
    mock_post = PostFactory(post_admin=admin_user)
    assert mock_post is not None
    mock_comment = CommentFactory(comments_user=admin_user, post=mock_post)

    # Patch the get_object_or_404 to return our mock post and comment
    mocker.patch("blog.views.get_object_or_404", side_effect=[mock_post, mock_comment])

    response = client.post(
        reverse(
            "blog:update_comment",
            kwargs={"slug": mock_post.slug, "comment_id": mock_comment.id},
        ),
        data={"body": "updated comment"},
    )

    # Check for redirection and success message
    assert response.status_code == 302
    assert mock_comment.body == "updated comment"
    assert response.url == reverse("blog:live_post", kwargs={"slug": mock_post.slug})


@pytest.mark.django_db
def test_update_comment_view_post_empty(mocker, admin_user, client):
    regular_user = CustomUserOnlyFactory(user_type="SELLER")

    client.force_login(regular_user)

    # Create a mock post and comment
    mock_post = PostFactory(post_admin=admin_user)
    mock_comment = CommentFactory(comments_user=regular_user, post=mock_post)

    # Patch the get_object_or_404 to return our mock post and comment
    mocker.patch("blog.views.get_object_or_404", side_effect=[mock_post, mock_comment])

    response = client.post(
        reverse(
            "blog:update_comment",
            kwargs={"slug": mock_post.slug, "comment_id": mock_comment.id},
        ),
        data={"body": ""},
    )

    assert response.status_code == 302
    # assert "form" in response.context
    assert mock_comment.body == ""
    assert response.url == reverse("blog:live_post", args=[mock_post.slug])


@pytest.mark.parametrize(
    "user_type", ["SELLER", "CUSTOMER", "MANAGER", "CUSTOMER REPRESENTATIVE"]
)
@pytest.mark.django_db
def test_update_comment_view_no_permission(mocker, admin_user, client, user_type):
    regular_user = CustomUserOnlyFactory(user_type=user_type)

    client.force_login(regular_user)

    # Create a mock post and comment
    mock_post = PostFactory(post_admin=admin_user)
    mock_comment = CommentFactory(comments_user=admin_user, post=mock_post)

    # Patch the get_object_or_404 to return our mock post and comment
    mocker.patch("blog.views.get_object_or_404", side_effect=[mock_post, mock_comment])

    response = client.post(
        reverse(
            "blog:update_comment",
            kwargs={"slug": mock_post.slug, "comment_id": mock_comment.id},
        ),
        data={"text": "Updated Comment"},
    )

    # Check for redirection and error message
    assert response.status_code == 302
    assert response.url == reverse("blog:post_list")
    messages_list = list(messages.get_messages(response.wsgi_request))
    any(
        "You do not have permission to edit this comment." in str(message)
        for message in messages_list
    )


@pytest.mark.django_db
def test_delete_comment_view_author(mocker, client):
    regular_user = CustomUserOnlyFactory(user_type="SELLER")

    client.force_login(regular_user)

    # Create a mock comment
    mock_post = PostFactory()
    mock_comment = CommentFactory(comments_user=regular_user, post=mock_post)

    # Patch the get_object_or_404 to return our mock comment
    mocker.patch("blog.views.get_object_or_404", return_value=mock_comment)

    mock_delete = mocker.patch.object(mock_comment, "delete")

    response = client.post(
        reverse(
            "blog:delete_comment",
            kwargs={"slug": mock_post.slug, "comment_id": mock_comment.id},
        )
    )

    # Verify comment.delete() was called
    mock_delete.assert_called_once()

    # Check for redirection and success message
    assert response.status_code == 302
    assert response.url == reverse("blog:live_post", kwargs={"slug": mock_post.slug})
    messages_list = list(messages.get_messages(response.wsgi_request))
    any("Your comment has been deleted." in str(message) for message in messages_list)


@pytest.mark.parametrize(
    "user_type", ["SELLER", "CUSTOMER", "MANAGER", "CUSTOMER REPRESENTATIVE"]
)
@pytest.mark.django_db
def test_delete_comment_view_not_author(mocker, admin_user, client, user_type):
    regular_user = CustomUserOnlyFactory(user_type=user_type)

    client.force_login(regular_user)

    # Create a mock comment
    mock_post = PostFactory()
    mock_comment = CommentFactory(comments_user=admin_user, post=mock_post)

    mock_delete = mocker.patch.object(mock_comment, "delete")

    # Patch the get_object_or_404 to return our mock comment
    mocker.patch("blog.views.get_object_or_404", return_value=mock_comment)

    response = client.post(
        reverse(
            "blog:delete_comment",
            kwargs={"slug": mock_post.slug, "comment_id": mock_comment.id},
        )
    )

    # Verify comment.delete() was not called
    mock_delete.assert_not_called()

    # Check for redirection and error message
    assert response.status_code == 302
    assert response.url == reverse("blog:live_post", kwargs={"slug": mock_post.slug})
    messages_list = list(messages.get_messages(response.wsgi_request))
    any(
        "You do not have permission to delete this comment." in str(message)
        for message in messages_list
    )


@pytest.mark.django_db
def test_search_view(mocker, client):

    # Create a mock set of posts
    mock_posts = MockSet(
        MockModel(id=1, title="Post 1"),
        MockModel(id=2, title="Post 2"),
    )

    # Patch the Post.objects.all() method to return our mock set
    mocker.patch("blog.models.Post.objects.all", return_value=mock_posts)

    # Simulate a GET request to the search_view
    response = client.get(reverse("blog:search_view"))

    # Verify the response context
    assert response.status_code == 200
    assert response.context["count"] == mock_posts.count()
    assert "blog_base.html" in [template.name for template in response.templates]


@pytest.mark.django_db
def test_search_results_view_no_query(mocker, client):
    # Create a mock set of posts
    mock_posts = MockSet(
        MockModel(id=1, title="Post 1"),
        MockModel(id=2, title="Post 2"),
    )

    # Patch the Post.objects.all() method to return our mock set
    mocker.patch("blog.models.Post.objects.all", return_value=mock_posts)

    # Simulate a GET request to the search_results_view without a search query
    response = client.get(reverse("blog:search_results_view"))

    # Verify the response context
    assert response.status_code == 200
    assert response.context["post"].count() == 0
    assert response.context["query"] is None

    # Verify the correct template is used
    assert "search_results.html" in [template.name for template in response.templates]


@pytest.mark.django_db
def test_search_results_view_with_query(mocker, client):
    # Create a mock set of posts
    mock_posts = MockSet(
        MockModel(id=1, title="Post 1", status=True),
        MockModel(id=2, title="Another Post", status=True),
        MockModel(id=3, title="Non-matching Post", status=False),
    )

    # Patch the Post.objects.all() method to return our mock set
    mocker.patch("blog.models.Post.objects.all", return_value=mock_posts)

    # Simulate a GET request to the search_results_view with a search query
    response = client.get(reverse("blog:search_results_view"), {"search": "Post"})

    # Filter posts in mock set manually to verify the result
    filtered_posts = [
        post for post in mock_posts if "Post" in post.title and post.status
    ]

    # Verify the response context
    assert response.status_code == 200
    assert response.context["post"].count() == len(filtered_posts)
    assert response.context["query"] == "Post"

    # Verify the correct template is used
    assert "search_results.html" in [template.name for template in response.templates]


@pytest.mark.django_db
def test_search_results_view_with_no_matching_query(mocker, client):
    # Create a mock set of posts
    mock_posts = MockSet(
        MockModel(id=1, title="Post 1", status=True),
        MockModel(id=2, title="Another Post", status=True),
    )

    # Patch the Post.objects.all() method to return our mock set
    mocker.patch("blog.models.Post.objects.all", return_value=mock_posts)

    # Simulate a GET request to the search_results_view with a non-matching search query
    response = client.get(reverse("blog:search_results_view"), {"search": "NoMatch"})

    # Verify the response context
    assert response.status_code == 200
    assert response.context["post"].count() == 0
    assert response.context["query"] == "NoMatch"

    # Verify the correct template is used
    assert "search_results.html" in [template.name for template in response.templates]


@pytest.mark.django_db
def test_search_results_for_admin_my_post_view_no_filter(mocker, admin_user, client):
    client.force_login(admin_user)

    # Create a mock set of posts
    posts = PostFactory.create_batch(5, post_admin=admin_user)

    response = client.get(reverse("blog:admin_search_results_view"))

    # Verify the response context
    assert response.status_code == 200
    assert response.context["posts"].count() == len(posts)

    # Verify the correct template is used
    assert "admin_search_results_my_posts.html" in [
        template.name for template in response.templates
    ]


@pytest.mark.django_db
def test_search_results_for_admin_my_post_view_with_search(admin_user, client):
    client.force_login(admin_user)

    # Create a mock set of posts
    posts = PostFactory.create_batch(5, post_admin=admin_user)

    # get the post title
    post = Post.objects.first()
    assert post is not None

    response = client.get(reverse("blog:admin_search_results_view"))

    # Simulate a GET request to the Search_Results_For_Admin_My_Post view with a search query
    response = client.get(
        reverse("blog:admin_search_results_view"), {"search": post.title}
    )

    # Verify the response context
    assert response.status_code == 200
    assert response.context["posts"].count() == 1

    # Verify the correct template is used
    assert "admin_search_results_my_posts.html" in [
        template.name for template in response.templates
    ]


@pytest.mark.django_db
def test_search_results_for_admin_my_post_view_with_status(admin_user, client):
    client.force_login(admin_user)

    # Create a mock set of posts
    posts = PostFactory.create_batch(5, post_admin=admin_user)

    response = client.get(reverse("blog:admin_search_results_view"), {"value": 1})

    # Filter posts in mock set manually to verify the result
    filtered_posts = [post for post in posts if post.status]

    # Verify the response context
    assert response.status_code == 200
    assert "posts" in response.context
    assert response.context["posts"].count() == len(filtered_posts)

    # Verify the correct template is used
    assert "admin_search_results_my_posts.html" in [
        template.name for template in response.templates
    ]


@pytest.mark.django_db
def test_search_results_for_admin_my_post_view_context_data(admin_user, client):
    client.force_login(admin_user)

    # Create a mock set of posts
    posts = PostFactory.create_batch(4, post_admin=admin_user)

    # get the post title
    get_post = Post.objects.first()
    assert get_post is not None

    # Simulate a GET request to the Search_Results_For_Admin_My_Post view with both filters
    response = client.get(
        reverse("blog:admin_search_results_view"),
        {"search": get_post.title, "value": 1},
    )

    # Filter posts in mock set manually to verify the result
    filtered_posts = [
        post for post in posts if get_post.title in post.title and post.status
    ]
    publish = len([post for post in posts if post.status == 1])
    draft = len([post for post in posts if post.status == 0])

    # Verify the response context
    assert response.status_code == 200
    assert "posts" in response.context
    assert response.context["posts"].count() == len(filtered_posts)
    assert response.context["search"] == get_post.title
    assert response.context["draft"] == draft
    assert response.context["publish"] == publish


@pytest.mark.django_db
def test_live_post_view_get_request(mocker, admin_user, client):
    client.force_login(admin_user)

    # Create a mock post
    mock_post = MockModel(id=1, slug="test-post", status=1)

    # Create a mock set of comments
    mock_comments = MockSet(
        MockModel(id=1, post=mock_post, active=True),
        MockModel(id=2, post=mock_post, active=True),
    )

    # Patch the get_object_or_404 and Comment.objects.filter methods
    mocker.patch("blog.views.get_object_or_404", return_value=mock_post)
    mocker.patch("blog.views.Comment.objects.filter", return_value=mock_comments)

    # Simulate a GET request to the live_post view
    response = client.get(reverse("blog:live_post", kwargs={"slug": mock_post.slug}))

    # Verify the response context
    assert response.status_code == 200
    assert "blog_post" in response.context
    assert "comments" in response.context
    assert "comment_form" in response.context
    assert response.context["blog_post"] == mock_post
    assert response.context["comments"].count() == len(mock_comments)

    # Verify the correct template is used
    assert "live_post.html" in [template.name for template in response.templates]


@pytest.mark.django_db
def test_live_post_view_post_request_valid_data(mocker, admin_user, client):
    client.force_login(admin_user)

    # Create a mock post
    real_post = PostFactory(slug="test-post", status=1, post_admin=admin_user)

    # Create a mock set of comments
    mock_comments = CommentFactory(post=real_post, body="comment body")
    # Create a mock set of comments
    mock_comments = CommentFactory.create_batch(
        2,
        post=real_post,
        comments_user=admin_user,
    )

    # Patch the get_object_or_404 and Comment.objects.filter methods
    mocker.patch("blog.views.get_object_or_404", return_value=real_post)
    mock_filter = mocker.patch(
        "blog.views.Comment.objects.filter", return_value=mock_comments
    )

    # Simulate a POST request with valid data
    comment_data = {"body": "Test comment content"}
    response = client.post(
        reverse("blog:live_post", kwargs={"slug": real_post.slug}), data=comment_data
    )

    # Verify the response context
    assert response.status_code == 302
    assert response.url == reverse("blog:live_post", kwargs={"slug": real_post.slug})

    # Verify that a new comment was created and saved
    new_comment = Comment.objects.last()
    assert new_comment.body == "Test comment content"
    assert new_comment.comments_user == admin_user
    # Assert the mock filter was called once
    mock_filter.assert_called_once_with(post=real_post, active=True)


@pytest.mark.django_db
def test_create_post_view_get_request_admin_user(admin_user, client):
    client.force_login(admin_user)

    # Simulate a GET request to the create post view
    response = client.get(reverse("blog:blog_post_create"))

    # Verify the response context
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], PostForm)

    # Verify the correct template is used
    assert "blog_post.html" in [template.name for template in response.templates]


@pytest.mark.django_db
def test_create_post_view_post_request_valid_data_admin_user(admin_user, client):
    client.force_login(admin_user)

    post = PostFactory.build(post_admin=admin_user, status=1)

    # Create a mock set of posts
    post_data = {
        "title": post.title,
        "status": post.status,
        "slug": post.slug,
        "meta_description": post.meta_description[:150],
        "content": post.content,
    }

    form = PostForm(data=post_data)
    assert form.is_valid()

    # Simulate a POST request to the create post view
    response = client.post(reverse("blog:blog_post_create"), data=post_data)

    # Verify the response status code
    assert response.status_code == 302

    get_post = Post.objects.get(slug=post.slug)

    # Verify the redirect URL
    assert response.url == reverse("blog:live_post", kwargs={"slug": get_post.slug})


@pytest.mark.django_db
def test_create_post_view_post_request_invalid_data_admin_user(admin_user, client):
    client.force_login(admin_user)

    # Simulate a POST request with invalid data (missing required fields)
    post_data = {"title": "", "content": "", "status": ""}
    response = client.post(reverse("blog:blog_post_create"), data=post_data)

    # Verify the response context
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], PostForm)
    assert response.context["form"].errors

    # Verify the correct template is used
    assert "blog_post.html" in [template.name for template in response.templates]


@pytest.mark.django_db
def test_create_post_view_get_request_non_admin_user(client):

    # create a regular user
    regular_user = CustomUserOnlyFactory(user_type="CUSTOMER")
    client.force_login(regular_user)

    # Simulate a GET request to the create post view
    response = client.get(reverse("blog:blog_post_create"))

    # Verify the response context
    assert response.status_code == 200
    assert "user_email" in response.context
    assert "user_permission" in response.context

    # Verify the correct template is used
    assert "permission_denied.html" in [
        template.name for template in response.templates
    ]
