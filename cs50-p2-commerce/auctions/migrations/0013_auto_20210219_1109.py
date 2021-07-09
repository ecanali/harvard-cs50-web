# Generated by Django 3.1.6 on 2021-02-19 11:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_auto_20210219_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='winner_id',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, related_name='winner_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
