# Generated by Django 4.2.8 on 2024-11-30 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Homepage', '0003_alter_administratorprofile_experience_years'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customsocialaccount',
            name='refresh_token',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
