from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from Homepage.models import CustomUser, CustomSocialAccount
from random import randint


@receiver(post_save, sender=CustomUser)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        user_type = instance.user_type
        # group_name = user_type.replace(' ', '_')  # Make a group name from user-type
        try:
            group = Group.objects.get(name=user_type)
            instance.groups.add(group)
        except Group.DoesNotExist:
            # Handle the case where the group doesn't exist

            pass


@receiver(post_save, sender=CustomSocialAccount)
def link_social_account(sender, instance, created, **kwargs):
    if created and instance.user.user_google_id is None:
        # Generate a 7-digit positive integer code
        unique_code = randint(
            1000000, 9999999
        )  # Generate a random number between 1000000 and 9999999

        # Assign the generated code to the 'user_google_id' field in CustomUser
        instance.user.user_google_id = unique_code
        instance.user.save()
    else:
        pass
