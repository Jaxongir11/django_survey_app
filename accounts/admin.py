from django.contrib import admin
from .models import Department, Position, Profile, ProfileDepartmentPosition


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}  # slug avtomatik to'ldiriladi


class PositionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class ProfileDepartmentPositionInline(admin.TabularInline):
    model = ProfileDepartmentPosition
    extra = 1


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'list_departments_positions']
    inlines = [ProfileDepartmentPositionInline]

    def list_departments_positions(self, obj):
        # Profilega bog'langan barcha department va positionlar ro'yxatini qaytaradi
        return ", ".join([
            f"{relation.department.name} - {relation.position.name}"
            for relation in ProfileDepartmentPosition.objects.filter(profile=obj)
        ])
    list_departments_positions.short_description = "Departments & Positions"


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Profile, ProfileAdmin)