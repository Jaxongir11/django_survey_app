# Generated by Django 5.0.4 on 2025-01-03 09:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_profiledepartmentposition_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='departments',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='positions',
        ),
        migrations.AddField(
            model_name='profile',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.department'),
        ),
        migrations.AddField(
            model_name='profile',
            name='position',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.position'),
        ),
        migrations.DeleteModel(
            name='DepartmentPosition',
        ),
    ]
