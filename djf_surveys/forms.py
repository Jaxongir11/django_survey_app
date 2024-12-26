from typing import List, Tuple
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from accounts.models import Profile
from djf_surveys.models import Answer, TYPE_FIELD, UserAnswer, Question, Direction, Question2, UserAnswer2, UserRating, \
    Answer2
from djf_surveys.widgets import CheckboxSelectMultipleSurvey, RadioSelectSurvey, DateSurvey, RatingSurvey
from djf_surveys.app_settings import DATE_INPUT_FORMAT, SURVEY_FIELD_VALIDATORS, SURVEY_EMAIL_FROM
from djf_surveys.validators import RatingValidator


def make_choices(question: Question) -> List[Tuple[str, str]]:
    choices = []
    for choice in question.choices.split(','):
        choice = choice.strip()
        choices.append((choice.replace(' ', '_').lower(), choice))
    return choices


class BaseSurveyForm(forms.Form):

    def __init__(self, survey, user, *args, **kwargs):
        self.survey = survey
        self.user = user if user.is_authenticated else None
        self.field_names = []
        self.questions = self.survey.questions.all().order_by('ordering')
        super().__init__(*args, **kwargs)

        for question in self.questions:
            # to generate field name
            field_name = f'field_survey_{question.id}'

            if question.type_field == TYPE_FIELD.multi_select:
                choices = make_choices(question)
                self.fields[field_name] = forms.MultipleChoiceField(
                    choices=choices, label=question.label,
                    widget=CheckboxSelectMultipleSurvey,
                )
            elif question.type_field == TYPE_FIELD.radio:
                choices = make_choices(question)
                self.fields[field_name] = forms.ChoiceField(
                    choices=choices, label=question.label,
                    widget=RadioSelectSurvey
                )
            elif question.type_field == TYPE_FIELD.select:
                choices = make_choices(question)
                empty_choice = [("", _("Choose"))]
                choices = empty_choice + choices
                self.fields[field_name] = forms.ChoiceField(
                    choices=choices, label=question.label
                )
            elif question.type_field == TYPE_FIELD.number:
                self.fields[field_name] = forms.IntegerField(label=question.label)
            elif question.type_field == TYPE_FIELD.url:
                self.fields[field_name] = forms.URLField(
                    label=question.label,
                    validators=[MaxLengthValidator(SURVEY_FIELD_VALIDATORS['max_length']['url'])]
                )
            elif question.type_field == TYPE_FIELD.email:
                self.fields[field_name] = forms.EmailField(
                    label=question.label,
                    validators=[MaxLengthValidator(SURVEY_FIELD_VALIDATORS['max_length']['email'])]
                )
            elif question.type_field == TYPE_FIELD.date:
                self.fields[field_name] = forms.DateField(
                    label=question.label, widget=DateSurvey(),
                    input_formats=DATE_INPUT_FORMAT
                )
            elif question.type_field == TYPE_FIELD.text_area:
                self.fields[field_name] = forms.CharField(
                    label=question.label, widget=forms.Textarea,
                    validators=[MinLengthValidator(SURVEY_FIELD_VALIDATORS['min_length']['text_area'])]
                )
            elif question.type_field == TYPE_FIELD.rating:
                if not question.choices:  # use 5 as default for backward compatibility
                    question.choices = 5
                self.fields[field_name] = forms.CharField(
                    label=question.label, widget=RatingSurvey,
                    validators=[MaxLengthValidator(len(str(int(question.choices)))),
                                RatingValidator(int(question.choices))]
                )
                self.fields[field_name].widget.num_ratings = int(question.choices)
            else:
                self.fields[field_name] = forms.CharField(
                    label=question.label,
                    validators=[
                        MinLengthValidator(SURVEY_FIELD_VALIDATORS['min_length']['text']),
                        MaxLengthValidator(SURVEY_FIELD_VALIDATORS['max_length']['text'])
                    ]
                )

            self.fields[field_name].required = question.required
            self.fields[field_name].help_text = question.help_text
            self.field_names.append(field_name)

    def clean(self):
        cleaned_data = super().clean()

        for field_name in self.field_names:
            try:
                field = cleaned_data[field_name]
            except KeyError:
                raise forms.ValidationError("You must enter valid data")

            if self.fields[field_name].required and not field:
                self.add_error(field_name, 'This field is required')

        return cleaned_data


class CreateSurveyForm(BaseSurveyForm):
    direction = forms.ModelChoiceField(
        queryset=Direction.objects.all(),
        required=True,
        label="O'qiyotgan kursingizni tanlang:",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, survey, user, *args, **kwargs):
        self.survey = survey
        self.user = user
        super().__init__(survey=survey, user=user, *args, **kwargs)

    @transaction.atomic
    def save(self):
        cleaned_data = super().clean()

        # UserAnswer va UserAnswer2 ni saqlash
        user_answer = UserAnswer.objects.create(
            survey=self.survey, user=self.user,
            direction=cleaned_data.get('direction')
        )
        user_answer2 = UserAnswer2.objects.create(
            survey=self.survey, user=self.user,
            direction=cleaned_data.get('direction')
        )

        # Umumiy savollarni saqlash
        for question in self.questions:
            field_name = f'field_survey_{question.id}'
            if question.type_field == TYPE_FIELD.multi_select:
                value = ",".join(cleaned_data[field_name])
            else:
                value = cleaned_data[field_name]
            Answer.objects.create(
                question=question, value=value, user_answer=user_answer
            )

        for key, val in self.data.items():
            print("KEY=", key, " VAL=", val)

        # Reyting savollarni saqlash
        for key, val in self.data.items():
            if key.startswith("rating_") and len(key.split("_")) == 3:
                _, profile_id_str, question_id_str = key.split("_")
                try:
                    rating_value = int(val)
                    profile_id = int(profile_id_str)
                    question_id = int(question_id_str)

                    question = get_object_or_404(Question2, id=question_id)
                    profile_obj = Profile.objects.get(id=profile_id)

                    # Chunki model 'UserRating.rated_user' -> ForeignKey(User)
                    user_rating = UserRating.objects.create(
                        user_answer=user_answer2,
                        rated_user=profile_obj.user  # <-- .user bilan User obyektini oldik
                    )
                    Answer2.objects.create(
                        question=question,
                        value=rating_value,
                        user_rating=user_rating
                    )
                except (ObjectDoesNotExist, ValueError) as e:
                    print("Xatolik:", e)
                    continue  # Noto‘g‘ri ma’lumotlarni o‘tkazib yuboring

        return user_answer


class EditSurveyForm(BaseSurveyForm):

    def __init__(self, user_answer, *args, **kwargs):
        self.survey = user_answer.survey
        self.user_answer = user_answer
        super().__init__(survey=self.survey, user=user_answer.user, *args, **kwargs)
        self._set_initial_data()

    def _set_initial_data(self):
        answers = self.user_answer.answer_set.all()

        for answer in answers:
            field_name = f'field_survey_{answer.question.id}'
            if answer.question.type_field == TYPE_FIELD.multi_select:
                self.fields[field_name].initial = answer.value.split(',')
            else:
                self.fields[field_name].initial = answer.value

