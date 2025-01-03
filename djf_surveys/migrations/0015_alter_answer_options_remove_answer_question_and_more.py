# Generated by Django 5.0.4 on 2024-10-31 04:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('djf_surveys', '0014_direction_alter_survey_options_useranswer_direction'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ['-created_at'], 'verbose_name': 'answer', 'verbose_name_plural': 'answers'},
        ),
        migrations.RemoveField(
            model_name='answer',
            name='question',
        ),
        migrations.AddField(
            model_name='answer',
            name='content_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='answer',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='answer',
            name='value',
            field=models.TextField(help_text='Foydalanuvchi tomonidan berilgan javobning qiymati.', verbose_name='value'),
        ),
        migrations.AlterField(
            model_name='question',
            name='choices',
            field=models.TextField(blank=True, help_text='Agar maydon turi radio, tanlanadigan yoki ko‘p tanlovli bo‘lsa, ajratilgan variantlarni to‘ldiringvergullar bilan. Masalan: Erkak, Ayol.', null=True, verbose_name='choices'),
        ),
        migrations.AlterField(
            model_name='question',
            name='help_text',
            field=models.CharField(blank=True, help_text='Bu yerda yordam matnini kiritishingiz mumkin.', max_length=200, null=True, verbose_name='help text'),
        ),
        migrations.AlterField(
            model_name='question',
            name='key',
            field=models.CharField(blank=True, help_text='Bu savol uchun noyob kalit, avtomatik yaratishda foydalanishni istasangiz, bo‘sh joyni to‘ldiring.', max_length=225, null=True, unique=True, verbose_name='key'),
        ),
        migrations.AlterField(
            model_name='question',
            name='label',
            field=models.CharField(help_text='Savolingizni shu yerga kiriting.', max_length=500, verbose_name='label'),
        ),
        migrations.AlterField(
            model_name='question',
            name='ordering',
            field=models.PositiveIntegerField(default=0, help_text='So‘rovnomalar doirasida savollar tartibini belgilaydi.', verbose_name='choices'),
        ),
        migrations.AlterField(
            model_name='question',
            name='required',
            field=models.BooleanField(default=True, help_text='Agar True bo‘lsa, foydalanuvchi ushbu savolga javob berishi kerak.', verbose_name='required'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='can_anonymous_user',
            field=models.BooleanField(default=False, help_text='Agar True bo‘lsa, autentifikatsiyasiz foydalanuvchi yuboradi.', verbose_name='anonymous submission'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='deletable',
            field=models.BooleanField(default=True, help_text="Agar false (yolg‘on) bo‘lsa, foydalanuvchi yozuvni o'chira olmaydi.", verbose_name='deletable'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='duplicate_entry',
            field=models.BooleanField(default=False, help_text='Agar rost (true) bo‘lsa, foydalanuvchi qayta topshirishi mumkin.', verbose_name='mutiple submissions'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='editable',
            field=models.BooleanField(default=True, help_text='Agar false (yolg‘on) bo‘lsa, foydalanuvchi yozuvni tahrirlay olmaydi.', verbose_name='editable'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='notification_to',
            field=models.TextField(blank=True, help_text='Xabardor qilish uchun elektron pochta manzilingizni kiriting', null=True, verbose_name='Notification To'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='private_response',
            field=models.BooleanField(default=False, help_text='Agar rost bo‘lsa, faqat administrator va egasi kira oladi.', verbose_name='private response'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='success_page_content',
            field=models.TextField(blank=True, help_text='Muvaffaqiyatli sahifasi shu yerda o‘zgartirishingiz mumkin. HTML sintaksisi qo‘llab-quvvatlanadi', null=True, verbose_name='Success Page Content'),
        ),
        migrations.CreateModel(
            name='Question2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type_field', models.PositiveSmallIntegerField(choices=[(0, 'Text'), (1, 'Number'), (2, 'Radio'), (3, 'Select'), (4, 'Multi Select'), (5, 'Text Area'), (6, 'URL'), (7, 'Email'), (8, 'Date'), (9, 'Rating')], verbose_name='type of input field')),
                ('key', models.CharField(blank=True, help_text='Unikal kalitni avtomatik yaratmoqchi bo‘lsangiz, bo‘sh joyni to‘ldiring.', max_length=225, null=True, unique=True, verbose_name='key')),
                ('label', models.CharField(help_text='Reyting savolingizni shu yerga kiriting.', max_length=500, verbose_name='label')),
                ('choices', models.PositiveIntegerField(default=5, help_text='Reyting yulduzlari soni (masalan, 5 yulduzli reyting tizimi uchun).', verbose_name='number of stars')),
                ('help_text', models.CharField(blank=True, help_text='Bu yerda yordam matnini kiritishingiz mumkin.', max_length=200, null=True, verbose_name='help text')),
                ('required', models.BooleanField(default=True, help_text='Agar True bo‘lsa, foydalanuvchi ushbu savolga javob berishi kerak.', verbose_name='required')),
                ('ordering', models.PositiveIntegerField(default=0, help_text='So‘rovnomalar doirasida savollar tartibini belgilaydi.', verbose_name='ordering')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating_questions', to='djf_surveys.survey', verbose_name='survey')),
            ],
            options={
                'verbose_name': 'rating question',
                'verbose_name_plural': 'rating questions',
                'ordering': ['ordering'],
            },
        ),
    ]
