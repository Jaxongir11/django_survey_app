from django.contrib import admin
from .models import Department, Position, Profile, Rank


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class PositiontAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class RankAdmin(admin.ModelAdmin):
    list_display = ("name",)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'get_first_name', 'get_last_name']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "position":
            kwargs["queryset"] = Position.objects.filter(department_id=1)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_username(self, obj):
        return obj.user.username

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    get_username.short_description = 'Username'
    get_first_name.short_description = 'First Name'
    get_last_name.short_description = 'Last Name'

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Position, PositiontAdmin)
admin.site.register(Rank, RankAdmin)
