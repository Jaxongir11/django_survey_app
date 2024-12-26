# Generated by Django 5.0.4 on 2024-11-01 05:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djf_surveys', '0015_alter_answer_options_remove_answer_question_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ['-created_at'], 'verbose_name': 'answer', 'verbose_name_plural': 'Javoblar'},
        ),
        migrations.AlterModelOptions(
            name='direction',
            options={'ordering': ['name'], 'verbose_name': 'direction', 'verbose_name_plural': "O'quv kurslari"},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['ordering'], 'verbose_name': 'question', 'verbose_name_plural': 'Savollar'},
        ),
        migrations.AlterModelOptions(
            name='question2',
            options={'ordering': ['ordering'], 'verbose_name': 'question', 'verbose_name_plural': 'Savollar'},
        ),
        migrations.AlterModelOptions(
            name='survey',
            options={'ordering': ['created_at'], 'verbose_name': 'survey', 'verbose_name_plural': "So'rovnomalar"},
        ),
        migrations.AlterModelOptions(
            name='useranswer',
            options={'ordering': ['-updated_at'], 'verbose_name': 'user answer', 'verbose_name_plural': 'Foydalanuvchi javoblari'},
        ),
        migrations.RemoveField(
            model_name='answer',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='answer',
            name='object_id',
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='djf_surveys.question', verbose_name='question'),
        ),
        migrations.AlterField(
            model_name='question2',
            name='choices',
            field=models.TextField(blank=True, help_text='Agar maydon turi radio, tanlanadigan yoki ko‘p tanlovli bo‘lsa, ajratilgan variantlarni to‘ldiringvergullar bilan. Masalan: Erkak, Ayol.', null=True, verbose_name='choices'),
        ),
        migrations.AlterField(
            model_name='question2',
            name='key',
            field=models.CharField(blank=True, help_text='Bu savol uchun noyob kalit, avtomatik yaratishda foydalanishni istasangiz, bo‘sh joyni to‘ldiring.', max_length=225, null=True, unique=True, verbose_name='key'),
        ),
        migrations.AlterField(
            model_name='question2',
            name='label',
            field=models.CharField(help_text='Savolingizni shu yerga kiriting.', max_length=500, verbose_name='label'),
        ),
        migrations.AlterField(
            model_name='question2',
            name='ordering',
            field=models.PositiveIntegerField(default=0, help_text='So‘rovnomalar doirasida savollar tartibini belgilaydi.', verbose_name='choices'),
        ),
        migrations.AlterField(
            model_name='question2',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions2', to='djf_surveys.survey', verbose_name='survey'),
        ),
        migrations.CreateModel(
            name='UserAnswer2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('direction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='djf_surveys.direction')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djf_surveys.survey', verbose_name='survey')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rating_user', to=settings.AUTH_USER_MODEL, verbose_name='rating user')),
            ],
            options={
                'verbose_name': 'user answer for Question2',
                'verbose_name_plural': 'Foydalanuvchi javoblari (Question2)',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='UserRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rated_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='rated user')),
                ('user_answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djf_surveys.useranswer2', verbose_name='user answer2')),
            ],
            options={
                'verbose_name': 'user rating',
                'verbose_name_plural': "O'qituvchilar reytingi",
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='useranswer2',
            name='rated_users',
            field=models.ManyToManyField(related_name='rated_users', through='djf_surveys.UserRating', to=settings.AUTH_USER_MODEL, verbose_name='rated users'),
        ),
        migrations.CreateModel(
            name='Answer2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('value', models.TextField(help_text='Foydalanuvchi tomonidan berilgan javobning qiymati.', verbose_name='value')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers2', to='djf_surveys.question2', verbose_name='question2')),
                ('user_rating', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djf_surveys.userrating', verbose_name='user rating')),
            ],
            options={
                'verbose_name': 'answer for Question2',
                'verbose_name_plural': 'Javoblar (Question2)',
                'ordering': ['-created_at'],
            },
        ),
    ]