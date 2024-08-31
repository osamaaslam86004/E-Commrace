import factory
from faker import Faker
from blog.models import Post, Comment
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory

fake = Faker()


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Sequence(lambda n: f"Unique Post {n}")  # Unique Post title
    slug = factory.Sequence(lambda n: f"unique-post-{n}")
    meta_description = factory.LazyAttribute(lambda _: fake.sentence(nb_words=150))
    post_admin = factory.SubFactory(CustomUserOnlyFactory)
    content = factory.Faker("text")
    status = factory.Iterator([0, 1])


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    comments_user = factory.SubFactory(CustomUserOnlyFactory)
    body = factory.Faker("sentence")
