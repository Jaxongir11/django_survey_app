# Generated by Django 5.0.1 on 2024-01-22 09:33

import birthday.fields
import datetime
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='birthday',
            field=birthday.fields.BirthdayField(default=datetime.date.today, null=True),
        ),
    ]
