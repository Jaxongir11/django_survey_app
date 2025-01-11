from django.contrib import admin
from .models import Department, Position, Profile, Rank


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}  # slug avtomatik to'ldiriladi


class PositionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class RankAdmin(admin.ModelAdmin):
    list_display = ("name",)


class ProfileAdmin(admin.ModelAdmin):
    # Endi 'department' va 'position' ForeignKey bo‘lgani uchun to'g'ridan-to'g'ri ko'rsatish mumkin
    list_display = ['user', 'get_user_full_name', 'department', 'position', 'rank', 'gender', 'can_be_rated']
    # Agar xohlasangiz, qidirish va filtr sozlamalarini ham qo‘shishingiz mumkin, masalan:
    search_fields = ['user__username', 'department__name', 'position__name']
    list_filter = ['department', 'position', 'gender', 'can_be_rated']

    def get_user_full_name(self, obj):
        return f"{obj.user.last_name} {obj.user.first_name}"

    get_user_full_name.short_description = 'Familiyasi va ismi'


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Rank, RankAdmin)
admin.site.register(Profile, ProfileAdmin)