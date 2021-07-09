# Generated by Django 3.1.6 on 2021-02-21 16:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_auto_20210219_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='owner_user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
    ]