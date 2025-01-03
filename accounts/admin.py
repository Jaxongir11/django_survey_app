from django.contrib import admin
from .models import Department, Position, Profile


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}  # slug avtomatik to'ldiriladi


class PositionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class ProfileAdmin(admin.ModelAdmin):
    # Endi 'department' va 'position' ForeignKey bo‘lgani uchun to'g'ridan-to'g'ri ko'rsatish mumkin
    list_display = ['user', 'department', 'position', 'gender', 'can_be_rated']
    # Agar xohlasangiz, qidirish va filtr sozlamalarini ham qo‘shishingiz mumkin, masalan:
    search_fields = ['user__username', 'department__name', 'position__name']
    list_filter = ['department', 'position', 'gender', 'can_be_rated']


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Profile, ProfileAdmin)