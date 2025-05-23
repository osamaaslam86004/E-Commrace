# Generated by Django 4.2.8 on 2025-03-11 03:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_refund_id', models.CharField(default=0, max_length=150, null=True)),
                ('refund_status', models.CharField(choices=[('REFUNDED', 'Refund'), ('NO_REFUND', 'No Refund')], default='NO_REFUND', max_length=25)),
                ('cart', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cart_refund', to='cart.cart')),
                ('cartitem', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cartitem_refund', to='cart.cartitem')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_charge_id', models.CharField(max_length=150)),
                ('stripe_customer_id', models.CharField(max_length=150)),
                ('payment_status', models.CharField(choices=[('SUCCESSFUL', 'Successful'), ('PENDING', 'Pending')], default='PENDING', max_length=25)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('cart', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cart_payment', to='cart.cart')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_payment', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
