# Generated by Django 4.2.8 on 2025-03-11 03:17

import ckeditor.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('i', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookAuthorName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_name', models.CharField(max_length=255)),
                ('author_name', models.CharField(max_length=50)),
                ('about_author', models.TextField(default='default', max_length=500)),
                ('language', models.CharField(default='English', max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='BookFormat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('format', models.CharField(choices=[('AUDIO_CD', 'Audio CD'), ('SPIRAL_BOUND', 'spiral bound'), ('PAPER_BACK', 'paper back'), ('HARDCOVER', 'Hardcover')], max_length=20)),
                ('is_new_available', models.PositiveIntegerField()),
                ('is_used_available', models.PositiveIntegerField()),
                ('publisher_name', models.CharField(max_length=100, null=True)),
                ('publishing_date', models.DateField(blank=True, null=True)),
                ('edition', models.CharField(blank=True, max_length=50, null=True)),
                ('length', models.PositiveIntegerField(null=True)),
                ('narrator', models.CharField(blank=True, max_length=20, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(limit_value=1, message='Price must be greater than or equal to 1.'), django.core.validators.MaxValueValidator(limit_value=999999.99, message='Price cannot exceed 999999.99.')])),
                ('is_active', models.BooleanField(default=True, null=True)),
                ('restock_threshold', models.PositiveIntegerField(default=9)),
                ('image_1', models.ImageField(default='https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico', null=True, upload_to='images/')),
                ('image_2', models.ImageField(default='https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico', null=True, upload_to='images/')),
                ('image_3', models.ImageField(default='https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico', null=True, upload_to='images/')),
                ('book_author_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='format_name', to='book_.bookauthorname')),
                ('product_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_product_category', to='i.productcategory')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_format_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100)),
                ('content', ckeditor.fields.RichTextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('status', models.BooleanField(default=True, null=True)),
                ('image_1', models.ImageField(default='https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico', null=True, upload_to='images/')),
                ('image_2', models.ImageField(default='https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico', null=True, upload_to='images/')),
                ('book_format', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_review_format', to='book_.bookformat')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_user_review', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.DecimalField(decimal_places=1, max_digits=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('book_format', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating_format', to='book_.bookformat', verbose_name='book_format_rating')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_user_rating', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
