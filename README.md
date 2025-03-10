
# django-E-Cmmrace

## Authorizations and Authentications:

1. used signed cookie based session (httponly cookie)
2. Custom Permissions for different user-types
3. django-axes to limit the unauthorized attempts
4. Multiple methods for log-in:
   1. Google account login / OAuth Authentication
   2. SMS login / Two-Factor Authentication
   3. Basic Authentication / Password Based Autehnication / Single-Facctor Authentication
5. Multiple methods for Password reset
   1. E-mail send using sendgrid
   2. OTP send using twilio


## User Profiles:

### User-Types: Customer, Seller/Merchant, Customer Service Representative, Manager, Admin

### Permissions And Groups


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


## Security and Performance Enhancements:

1. Content Security Policy (CSP): Implemented using django_csp

2. Compression Headers: Enabled Gzip/Brotli compression using django-compression-middleware

3. SEO Enhancements: Added robots.txt and sitemap.xml for the Monitors model

4. ETag Header: Available only for the homepage


# Integration With Resume API

1. One User can Create, Update, Delete and Read many Resume / CV
Reference : [GitHub Repo](https://github.com/osamaaslam86004/Resume-API-Backend.git)

# How to run this web app:

python version : 3.11

 1. python -m pip install -r requirements.txt
 
## Reset the database:
 1. python manage.py flush
 2. python manage.py reset_db
 3. python manage.py clean_pyc

 ## Delete migration files if present:
 1. python delete_migrations.py
 
## Apply migrations:
 1. python manage.py makemigrations
 2. python manage.py migrate 

 ## Populate initial data for creating product categories (mandaotory):
 1. python manage.py product_category 
 2. python manage.py computersubcategory 
 3. python manage.py Special_Features 
