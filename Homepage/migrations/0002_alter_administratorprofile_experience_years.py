# Generated by Django 4.2.8 on 2024-08-27 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Homepage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administratorprofile',
            name='experience_years',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
