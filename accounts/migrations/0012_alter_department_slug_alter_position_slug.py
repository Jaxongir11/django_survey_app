# Generated by Django 5.0.4 on 2024-12-24 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_profileposition_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
