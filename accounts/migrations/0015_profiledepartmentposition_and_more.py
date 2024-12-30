# Generated by Django 5.0.4 on 2024-12-30 15:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_alter_departmentposition_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileDepartmentPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveConstraint(
            model_name='departmentposition',
            name='unique_department_position',
        ),
        migrations.RemoveField(
            model_name='department',
            name='positions',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='department',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='position',
        ),
        migrations.AlterField(
            model_name='profile',
            name='rank',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rank', to='accounts.rank'),
        ),
        migrations.AlterUniqueTogether(
            name='departmentposition',
            unique_together={('department', 'position')},
        ),
        migrations.AddField(
            model_name='profiledepartmentposition',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.department'),
        ),
        migrations.AddField(
            model_name='profiledepartmentposition',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.position'),
        ),
        migrations.AddField(
            model_name='profiledepartmentposition',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.profile'),
        ),
        migrations.AddField(
            model_name='profile',
            name='departments',
            field=models.ManyToManyField(related_name='profiles', through='accounts.ProfileDepartmentPosition', to='accounts.department'),
        ),
        migrations.AddField(
            model_name='profile',
            name='positions',
            field=models.ManyToManyField(related_name='profiles', through='accounts.ProfileDepartmentPosition', to='accounts.position'),
        ),
        migrations.AlterUniqueTogether(
            name='profiledepartmentposition',
            unique_together={('profile', 'department', 'position')},
        ),
    ]
