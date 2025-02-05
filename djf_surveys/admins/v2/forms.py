from django import forms
from django.utils.translation import gettext_lazy as _
from djf_surveys.models import Question, Survey
from djf_surveys.widgets import InlineChoiceField


class QuestionForm(forms.ModelForm):
    
    class Meta:
        model = Question
        fields = ['label', 'key', 'help_text', 'required']


class QuestionWithChoicesForm(forms.ModelForm):
    
    class Meta:
        model = Question
        fields = ['label', 'key', 'choices', 'help_text', 'required']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['choices'].widget = InlineChoiceField()
        self.fields['choices'].help_text = _("Yana variant qo'shish uchun + tugmasini bosing")


class QuestionFormRatings(forms.ModelForm):
    
    class Meta:
        model = Question
        fields = ['label', 'key', 'choices', 'help_text', 'required']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['choices'].widget = forms.NumberInput(attrs={'max': 10, 'min': 1})
        self.fields['choices'].help_text = _("1 va 10 orasida bo‘lishi kerak")
        self.fields['choices'].label = _("Reytinglar soni")
        self.fields['choices'].initial = 5


class SurveyForm(forms.ModelForm):
    
    class Meta:
        model = Survey
        fields = [
            'name', 'description', 'editable', 'deletable', 
            'duplicate_entry', 'private_response', 'can_anonymous_user',
            'notification_to', 'success_page_content'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notification_to'].widget = InlineChoiceField()
