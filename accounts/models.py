from datetime import date

from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from slugify import slugify
from PIL import Image
from birthday import BirthdayField, BirthdayManager


class Department(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Position(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    name = models.CharField(max_length=255)
    slug = models.SlugField(null=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Rank(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


GENDER_CHOICES = (
        ('E','Erkak'),
        ('A','Ayol'),
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='profiles')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, related_name='profiles')
    rank = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True, related_name='rank')


    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default='E')
    birthday = BirthdayField(null=True, default=date.today)
    objects = BirthdayManager()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Telefon raqami quyidagi formatda kiritilishi kerak: '+998901234567'")
    phone_number = models.CharField(validators=[phone_regex], max_length=15, blank=True)
    image = models.ImageField(upload_to='user_image/', default='user_image/default.png')

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)  # Open image

        # resize image
        if img.height > 200 or img.width > 200:
            output_size = (200, 200)
            img.thumbnail(output_size)  # Resize image
            img.save(self.image.path)  # Save it again and override
