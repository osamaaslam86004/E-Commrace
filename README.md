
# django-E-Cmmrace

## Authorizations and Authentications:

1. used signed cookie based session (httponly cookie, named as sessionid)
2. Custom Permissions for different user-types
3. django-axes to limit the unauthorized attempts
4. Multiple methods for log-in:
   1. Google account login
   2. SMS login
   3. Database / website account login
5. Multiple methods for Password reset
   1. E-mail send using sendgrid
   2. OTP send using twilio


## User Profiles:

### User-Types: Customer, Seller/Merchant, Customer Service Representative, Manager, Admin

### Permissions And Groups

1. CUSTOMER:
    4. customer view blog
    5. cusyomer delete comment
    6. customer add comment
    7. customer delete profile
    8. customer create profile
    9. customer edit comment
    10. customer edit profile
    11. customer view order status


2. SELLER:
    1. seller delete product
    2. seller update product
    3. seller add product
    4. seller view blog
    5. seller delete comment
    6. seller add comment
    7. seller delete profile
    8. seller create profile
    9. seller edit comment
    10. seller edit profile
    11. seller view order status


3. CUSTOMER SERVICE REPRESENTATIVE:
    4. csr view blog
    5. csr delete comment
    6. csr add comment
    7. csr delete profile
    8. csr create profile
    9. csr edit comment
    10. csr edit profile
    11. csr view order status



4. MANAGER:
    1. manager delete product
    2. manager update product
    3. manager add product
    4. manager view blog
    5. manager delete comment
    6. manager add comment
    7. manager delete profile
    8. manager create profile
    9. manager edit comment
    10. manager edit profile
    11. manager view order status 
    12. manager create blog
    13. manager update blog
    14. manager delete blog



5. ADMINISTRATOR:
    1. admin delete product
    2. admin update product
    3. admin add product
    4. admin view blog
    5. admin delete comment
    6. admin add comment
    7. admin delete profile
    8. admin create profile
    9. admin edit comment
    10. admin edit profile
    11. admin view order status 
    12. admin create blog
    13. admin update blog
    14. admin delete blog
    15. admin edit customer profile
    16. admin delete customer profile
    17. admin edit seller profile", 
    18. admin delete seller profile
    19. admin edit csr profile 
    20. admin delete csr profile
    21. admin edit manager profile
    22. admin delete manager profile



## Image Handling:
1. cloudinary storages is used to store images
   
   1. Users can upload profile image
   2. Seller can upload maximum of 3 images for their product


## Ckeditor:
Admin can only published a text-type blog using ckeditor.


## Product Categories:
1. Books:
         Restriction: Seller can add only one book of each format-type
2. Monitor:
           Seller can add any number of Monitor type product




## User Browsing History:
1. httponly cookie based sessions is used to display user browsing history. Only 5 to 7 products 
will be displayed.

### Cart:
1. The items in the cart are stored in both database and cookie. Cart items are retrieve from the cookie,
if cookie is present in the browser. Otherwise, cart items are retrieved from database

#### Restriction: 
1. User can add any number of items in cart, unless cookie size is less than 4Kb
2. Many cart are linked to one user




## Payment Handling:
1. Stripe API is used to handle the payment.
2. User can get a Partial or Full refund for a product
3. User can view the Refund status in their profiles


# Integration With Resume API

1. One User can Create, Update, Delete and Read many Resume / CV
Reference : [GitHub Repo](https://github.com/osamaaslam86004/reumse_api-5-24-2024.git)

# How to run this web app:

python version : 3.11

 1. python -m pip install -r requirements.txt
 2. python manage.py flush
 3. python manage.py reset_db
 4. python manage.py clean_pyc
 5. python manage.py makemigrations
 6. python manage.py migrate 
 7. python manage.py product_category 
 8. python manage.py computersubcategory 
 9. python manage.py Special_Features 
