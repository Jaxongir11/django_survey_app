from django.contrib import admin
from .models import Survey, Question, Question2, Answer, Answer2, UserAnswer, UserAnswer2, Direction, UserRating


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('name',)  # This will show the 'name' field in the list view.
    search_fields = ('name',)


class AdminQuestion(admin.ModelAdmin):
    list_display = ('survey', 'label', 'type_field', 'help_text', 'required')
    search_fields = ('survey__name', )


class AdminQuestion2(admin.ModelAdmin):
    list_display = ('survey', 'label', 'type_field', 'help_text', 'required')
    search_fields = ('survey__name', )


class AdminAnswer(admin.ModelAdmin):
    list_display = ('question', 'get_label', 'value', 'user_answer')
    search_fields = ('question__label', 'value',)
    list_filter = ('user_answer', 'created_at')

    def get_label(self, obj):
        return obj.question.label
    get_label.admin_order_field = 'question'
    get_label.short_description = 'Label'


class AdminAnswer2(admin.ModelAdmin):
    list_display = ('question', 'value', 'user_rating', 'created_at')
    search_fields = ('question__label', 'value')
    list_filter = ('user_rating', 'created_at')


class AdminUserAnswer(admin.ModelAdmin):
    list_display = ('survey', 'user', 'created_at', 'updated_at')


class AdminUserAnswer2(admin.ModelAdmin):
    list_display = ('survey', 'user', 'created_at', 'updated_at')
    search_fields = ('survey__name', 'user__username')


class AdminUserRating(admin.ModelAdmin):
    list_display = ('user_answer', 'rated_user', 'created_at')
    search_fields = ('user_answer__user__username', 'rated_user__username')


class AdminSurvey(admin.ModelAdmin):
    list_display = ('name', 'slug')
    exclude = ['slug']


admin.site.register(Survey, AdminSurvey)
admin.site.register(Question, AdminQuestion)
admin.site.register(Question2, AdminQuestion2)
admin.site.register(Answer, AdminAnswer)
admin.site.register(Answer2, AdminAnswer2)
admin.site.register(UserAnswer, AdminUserAnswer)
admin.site.register(UserAnswer2, AdminUserAnswer2)
admin.site.register(UserRating, AdminUserRating)
