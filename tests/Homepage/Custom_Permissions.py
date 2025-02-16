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
