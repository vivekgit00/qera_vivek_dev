# Generated by Django 5.2 on 2025-05-19 16:24

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qera_app', '0003_product_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('user', 'unique_code')},
        ),
    ]
