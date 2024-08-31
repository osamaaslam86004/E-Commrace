from django.db.models.signals import pre_save
from django.dispatch import receiver
from slugify import slugify  # Importing slugify from the python-slugify library
from blog.models import Post

@receiver(pre_save, sender=Post)
def create_post_slug(sender, instance, *args, **kwargs):
    if not instance.slug:  # Only create slug if it doesn't exist already
        base_slug = slugify(instance.title)
        instance_slug = base_slug[:80]  # Adjust the length of the base slug as needed
        similar_slugs = Post.objects.filter(slug__startswith=instance_slug).count()

        if similar_slugs > 0:
            half_meta_description = instance.meta_description[:len(instance.meta_description) // 2]
            half_meta_description_slug = slugify(half_meta_description)
            instance_slug += f"-{half_meta_description_slug}"
            instance.slug = instance_slug[:80]  # Limit slug length if necessary
        else:
            instance.slug = instance_slug
