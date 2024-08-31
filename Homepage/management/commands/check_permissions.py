# user_permissions_list = list(
#     Permission.objects.filter(
#         Q(user=request.user) | Q(group__user=request.user)
#     ).values_list("codename", flat=True)
# )

# Permission.objects.filter(Q(group__in=user.groups.all()) | Q(user=user)).distinct()


from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.contrib.auth import get_user_model
from Homepage.models import AdministratorProfile, SellerProfile, UserProfile
from django.db.models import Q

CustomUser = get_user_model()


class Command(BaseCommand):
    help = "Initialize groups and permissions for CustomUser"

    def handle(self, *args, **kwargs):

        try:
            admin_user = CustomUser.objects.create(
                user_type="ADMINISTRATOR",
                email="newadmin23@gmail.com",
                password="23newadmin23!",
                username="newadmin_user23",
            )
        except:
            admin_users_selected = CustomUser.objects.select_related(
                "customuser_type_5"
            )
            admin_user = admin_users_selected.filter(
                email="newadmin23@gmail.com",
            ).first()

        userprofile_for_admin = UserProfile.objects.filter(user=admin_user).first()
        admin_profile_instance = AdministratorProfile.objects.get_or_create(
            user=admin_user, admin_profile=userprofile_for_admin, experience_years=25
        )

        # Get the content type for the AdministratorProfile model
        content_type = ContentType.objects.get_for_model(AdministratorProfile)

        # Get the permissions for the AdministratorProfile model
        permissions = Permission.objects.filter(content_type=content_type)

        # Assign the permissions to the admin user
        admin_user.user_permissions.add(*permissions)

        # Save the admin user
        admin_user.save()

        # Return user direct permissions / object-level / Model-Level Permissions codename as strings / set()
        print(f"admin direct permissions----:{admin_user.get_user_permissions()}")
        for index, value in enumerate(admin_user.get_user_permissions()):
            print(f"permission name----:{value}")

        # return all permissions codename as a strings / set()
        print(f"admin user all permissions----:{admin_user.get_all_permissions()}")

        # return a list of all permission codename
        user_permissions_list = list(
            Permission.objects.filter(
                Q(user=admin_user) | Q(group__user=admin_user)
            ).values_list("codename", flat=True)
        )

        print(f"Names of user all permission : {user_permissions_list}")

        # return a set of all permission name
        user_permissions_list = set(
            Permission.objects.filter(
                Q(user=admin_user) | Q(group__user=admin_user)
            ).values_list("name", flat=True)
        )

        print(f"Names of user all permission : {user_permissions_list}")

        # return a zip of user all permissions codename list and permission name list
        user_permissions_codename_list = list(
            Permission.objects.filter(
                Q(user=admin_user) | Q(group__user=admin_user)
            ).values_list("codename", flat=True)
        )

        user_permissions_name_list = list(
            Permission.objects.filter(
                Q(user=admin_user) | Q(group__user=admin_user)
            ).values_list("name", flat=True)
        )

        user_permissions_zip = zip(
            user_permissions_codename_list, user_permissions_name_list
        )
        print(
            f"zip permission : {zip(user_permissions_codename_list, user_permissions_name_list)}"
        )

        # Iterate over the zip object and extract the data
        for codename, name in user_permissions_zip:
            print(f"Codename: {codename}, Name: {name}")
