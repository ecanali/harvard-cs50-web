# Generated by Django 3.1.6 on 2021-04-05 17:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('capstone', '0002_file_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='capstone.recipe'),
        ),
    ]
