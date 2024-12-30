from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from PIL import Image


class Department(models.Model):
    name = models.CharField(max_length=255,)
    slug = models.SlugField(null=False, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Position(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(null=False, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class DepartmentPosition(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('department', 'position')

    def __str__(self):
        return f"{self.department.name} - {self.position.name}"


class Rank(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


GENDER_CHOICES = (
    ('E', 'Erkak'),
    ('A', 'Ayol'),
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    departments = models.ManyToManyField(Department, through="ProfileDepartmentPosition", related_name="profiles")
    positions = models.ManyToManyField(Position, through="ProfileDepartmentPosition", related_name="profiles")
    rank = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True, related_name='rank')
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default='E')
    image = models.ImageField(upload_to='user_image/', default='user_image/default.png')
    can_be_rated = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)  # Open image

        # Resize image
        if img.height > 200 or img.width > 200:
            output_size = (200, 200)
            img.thumbnail(output_size)  # Resize image
            img.save(self.image.path)  # Save it again and override


class ProfileDepartmentPosition(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("profile", "department", "position")

    def __str__(self):
        return f"{self.profile.user.username} - {self.department.name} - {self.position.name}"