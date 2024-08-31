from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps


def initialize_groups_permissions(sender, **kwargs):
    custom_user_content_type = ContentType.objects.get_for_model(
        apps.get_model("Homepage", "CustomUser")
    )

    CUSTOMER_CUSTOM_PERMISSIONS = [
        ("customer_add_comment", "Can add comment on product or blogpost"),
        ("customer_delete_comment", "Can delete comment"),
        ("customer_edit_comment", "Can edit comment"),
        ("customer_edit_profile", "Can edit customer profile"),
        ("customer_delete_profile", "Can delete customer profile"),
        ("customer_create_profile", "Can edit customer profile"),
        ("customer_view_blog", "Can view blog"),
        ("customer_view_order_status", "Can check order status"),
    ]

    # Create permissions for CUSTOMER type users
    customer_permissions = {}
    for codename, description in CUSTOMER_CUSTOM_PERMISSIONS:
        customer_permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=custom_user_content_type,
            defaults={"name": description},
        )
        customer_permissions[codename] = customer_permission

        # if created:
        #     print(f"Permission created for {description}")
        # else:
        #     print(f"Permission '{description}' already exists")

    customer_group, created = Group.objects.get_or_create(name="CUSTOMER")
    if created:
        for codename, permission in customer_permissions.items():
            try:
                # permission = Permission.objects.get(codename=codename)
                customer_group.permissions.add(permission)
            except Permission.MultipleObjectsReturned:
                print(f"Multiple objects returned for codename: {codename}")
        customer_group.save()

    SELLER_CUSTOM_PERMISSIONS = [
        ("seller_add_comment", "Can add comment on product or blogpost"),
        ("seller_delete_comment", "Can delete comment"),
        ("seller_edit_comment", "Can edit comment"),
        ("seller_add_product", "Can add product"),
        ("seller_delete_product", "Can delete product"),
        ("seller_update_product", "Can update product"),
        ("seller_edit_profile", "Can edit customer profile"),
        ("seller_delete_profile", "Can delete customer profile"),
        ("seller_create_profile", "Can edit customer profile"),
        ("seller_view_blog", "Can view blog"),
        ("seller_view_order_status", "Can check order status"),
        (
            "seller_create_discounts_and_promotions",
            "Can approve discounts and promotions",
        ),
        (
            "seller_update_discounts_and_promotions",
            "Can approve discounts and promotions",
        ),
        (
            "seller_delete_discounts_and_promotions",
            "Can approve discounts and promotions",
        ),
        (
            "seller_view_discounts_and_promotions",
            "Can approve discounts and promotions",
        ),
    ]

    # Create permissions for SELLER type users
    seller_permissions = {}
    for codename, description in SELLER_CUSTOM_PERMISSIONS:
        seller_permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=custom_user_content_type,
            defaults={"name": description},
        )
        seller_permissions[codename] = seller_permission

        # if created:
        #     print(f"Permission created for {description}")
        # else:
        #     print(f"Permission '{description}' already exists")

    seller_group, created = Group.objects.get_or_create(name="SELLER")
    if created:
        for codename, permission in seller_permissions.items():
            try:
                # permission = Permission.objects.get(codename=codename)
                seller_group.permissions.add(permission)
            except Permission.MultipleObjectsReturned:
                print(f"Multiple objects returned for codename: {codename}")
        seller_group.save()

    CSR_CUSTOM_PERMISSIONS = [
        ("csr_add_comment", "Can add comment on product or blogpost"),
        ("csr_delete_comment", "Can delete comment"),
        ("csr_edit_comment", "Can edit comment"),
        ("csr_edit_profile", "Can edit customer profile"),
        ("csr_delete_profile", "Can delete customer profile"),
        ("csr_create_profile", "Can edit customer profile"),
        ("csr_view_blog", "Can view blog"),
        ("csr_view_order_status", "Can check order status"),
        (
            "csr_handle_customer_enquires",
            "Can respond to customer enquires",
        ),  # comming soon
    ]

    # Create permissions for CSR type users
    csr_permissions = {}
    for codename, description in CSR_CUSTOM_PERMISSIONS:
        csr_permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=custom_user_content_type,
            defaults={"name": description},
        )
        csr_permissions[codename] = csr_permission

        # if created:
        #     print(f"Permission created for {description}")
        # else:
        #     print(f"Permission '{description}' already exists")

    csr_group, created = Group.objects.get_or_create(name="CUSTOMER REPRESENTATIVE")
    if created:
        for codename, permission in csr_permissions.items():
            try:
                # permission = Permission.objects.get(codename=codename)
                csr_group.permissions.add(permission)
            except Permission.MultipleObjectsReturned:
                print(f"Multiple objects returned for codename: {codename}")
        csr_group.save()

    MANAGER_CUSTOM_PERMISSIONS = [
        ("manager_add_comment", "Can add comment on product or blogpost"),
        ("manager_delete_comment", "Can delete comment"),
        ("manager_edit_comment", "Can edit comment"),
        ("manager_add_product", "Can add product"),
        ("manager_delete_product", "Can delete product"),
        ("manager_update_product", "Can update product"),
        ("manager_edit_profile", "Can edit manager profile"),
        ("manager_delete_profile", "Can delete manager profile"),
        ("manager_create_profile", "Can delete manager profile"),
        ("manager_view_blog", "Can view blog"),
        ("manager_create_blog", "Can create blog"),
        ("manager_update_blog", "Can update blog"),
        ("manager_delete_blog", "Can delete blog"),
        ("manager_view_order_status", "Can check order status"),
        ("manager_update_order_status", "Can update order status"),
        ("manager_create_order_status", "Can check order status"),
        ("manager_delete_order_status", "Can update order status"),
        ("admin_approve_orders", "Can approve orders"),
        ("admin_delete_orders", "Can approve orders"),
        ("admin_view_orders", "Can approve orders"),
    ]

    # Create permissions for MANAGER type users
    manager_permissions = {}
    for codename, description in MANAGER_CUSTOM_PERMISSIONS:
        manager_permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=custom_user_content_type,
            defaults={"name": description},
        )
        manager_permissions[codename] = manager_permission

        # if created:
        #     print(f"Permission created for {description}")
        # else:
        #     print(f"Permission '{description}' already exists")

    manager_group, created = Group.objects.get_or_create(name="MANAGER")
    if created:
        for codename, permission in manager_permissions.items():
            try:
                # permission = Permission.objects.get(codename=codename)
                manager_group.permissions.add(permission)
            except Permission.MultipleObjectsReturned:
                print(f"Multiple objects returned for codename: {codename}")
        manager_group.save()

    ADMIN_CUSTOM_PERMISSIONS = [
        ("admin_add_product", "Can add product"),
        ("admin_delete_product", "Can delete product"),
        ("admin_update_product", "Can update product"),
        ("admin_edit_customer_profile", "Can edit customer profile"),
        ("admin_delete_customer_profile", "Can delete customer profile"),
        ("admin_edit_seller_profile", "Can edit seller profile"),
        ("admin_delete_seller_profile", "Can delete seller profile"),
        ("admin_edit_csr_profile", "Can edit CSR profile"),
        ("admin_delete_csr_profile", "Can delete CSR profile"),
        ("admin_edit_manager_profile", "Can edit manager profile"),
        ("admin_delete_manager_profile", "Can delete manager profile"),
        ("admin_view_blog", "Can view blog"),
        ("admin_create_blog", "Can create blog"),
        ("admin_update_blog", "Can update blog"),
        ("admin_delete_blog", "Can delete blog"),
        ("admin_view_order_status", "Can check order status"),
        ("admin_update_order_status", "Can update order status"),
        ("admin_create_order_status", "Can check order status"),
        ("admin_delete_order_status", "Can update order status"),
        ("admin_access_user_data", "Can access user data"),
        ("admin_handle_customer_enquires", "Can respond to customer enquires"),
        ("admin_view_order_detail", "Can view order detail"),
        ("admin_approve_orders", "Can approve orders"),  # comming soon
        ("admin_delete_orders", "Can approve orders"),  # comming soon
        ("admin_update_orders", "Can approve orders"),  # comming soon
        ("admin_view_orders", "Can approve orders"),  # comming soon
        (
            "admin_create_discounts_and_promotions",
            "Can approve discounts and promotions",
        ),
        (
            "admin_update_discounts_and_promotions",
            "Can approve discounts and promotions",
        ),
        (
            "admin_delete_discounts_and_promotions",
            "Can approve discounts and promotions",
        ),
        ("admin_view_discounts_and_promotions", "Can approve discounts and promotions"),
    ]

    admin_permissions = {}
    for codename, description in ADMIN_CUSTOM_PERMISSIONS:
        admin_permission, created = Permission.objects.get_or_create(
            codename=codename,
            content_type=custom_user_content_type,
            defaults={"name": description},
        )
        admin_permissions[codename] = admin_permission
        # if created:
        #     print(f"Permission created for {description}")
        # else:
        #     print(f"Permission '{description}' already exists")

    admin_group, created = Group.objects.get_or_create(name="ADMINISTRATOR")
    for codename, permission in admin_permissions.items():
        try:
            # permission = Permission.objects.get(codename=codename)
            admin_group.permissions.add(permission)
        except Permission.MultipleObjectsReturned:
            print(f"Multiple objects returned for codename: {codename}")
    admin_group.save()


if __name__ == "__main__":
    initialize_groups_permissions()
