import csv
from io import StringIO

from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.contrib import messages

from djf_surveys.app_settings import SURVEYS_ADMIN_BASE_PATH
from djf_surveys.models import Survey, Question, UserAnswer, Answer, Direction
from djf_surveys.mixin import ContextTitleMixin
from djf_surveys.views import SurveyListView
from djf_surveys.forms import BaseSurveyForm
from djf_surveys.summary import SummaryResponse
from djf_surveys.admins.v2.forms import SurveyForm


@method_decorator(staff_member_required, name='dispatch')
class AdminCrateSurveyView(ContextTitleMixin, CreateView):
    template_name = 'djf_surveys/admins/form.html'
    form_class = SurveyForm
    title_page = _("Add New Survey")

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            survey = form.save()
            self.success_url = reverse("djf_surveys:admin_forms_survey", args=[survey.slug])
            messages.success(self.request, gettext("%(page_action_name)s succeeded.") % dict(page_action_name=capfirst(self.title_page.lower())))
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


@method_decorator(staff_member_required, name='dispatch')
class AdminEditSurveyView(ContextTitleMixin, UpdateView):
    model = Survey
    form_class = SurveyForm
    template_name = 'djf_surveys/admins/form.html'
    title_page = _("Edit Survey")

    def get_success_url(self):
        survey = self.get_object()
        return reverse("djf_surveys:admin_forms_survey", args=[survey.slug])


@method_decorator(staff_member_required, name='dispatch')
class AdminSurveyListView(SurveyListView):
    template_name = 'djf_surveys/admins/survey_list.html'


@method_decorator(staff_member_required, name='dispatch')
class AdminSurveyFormView(ContextTitleMixin, FormMixin, DetailView):
    model = Survey
    template_name = 'djf_surveys/admins/form_preview.html'
    form_class = BaseSurveyForm

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(survey=self.object, user=self.request.user, **self.get_form_kwargs())

    def get_title_page(self):
        return self.object.name

    def get_sub_title_page(self):
        return self.object.description


@method_decorator(staff_member_required, name='dispatch')
class AdminDeleteSurveyView(DetailView):
    model = Survey

    def get(self, request, *args, **kwargs):
        survey = self.get_object()
        survey.delete()
        messages.success(request, gettext("Survey %ss succesfully deleted.") % survey.name)
        return redirect("djf_surveys:admin_survey")


@method_decorator(staff_member_required, name='dispatch')
class AdminCreateQuestionView(ContextTitleMixin, CreateView):
    """
    Note: This class already has version 2
    """
    model = Question
    template_name = 'djf_surveys/admins/question_form.html'
    success_url = reverse_lazy("djf_surveys:")
    fields = ['label', 'key', 'type_field', 'choices', 'help_text', 'required']
    title_page = _("Add Question")
    survey = None

    def dispatch(self, request, *args, **kwargs):
        self.survey = get_object_or_404(Survey, id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = self.survey
            question.save()
            messages.success(self.request, gettext("%(page_action_name)s succeeded.") % dict(page_action_name=capfirst(self.title_page.lower())))
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("djf_surveys:admin_forms_survey", args=[self.survey.slug])


@method_decorator(staff_member_required, name='dispatch')
class AdminUpdateQuestionView(ContextTitleMixin, UpdateView):
    """
    Note: This class already has version 2
    """
    model = Question
    template_name = 'djf_surveys/admins/question_form.html'
    success_url = SURVEYS_ADMIN_BASE_PATH
    fields = ['label', 'key', 'type_field', 'choices', 'help_text', 'required']
    title_page = _("Add Question")
    survey = None

    def dispatch(self, request, *args, **kwargs):
        question = self.get_object()
        self.survey = question.survey
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("djf_surveys:admin_forms_survey", args=[self.survey.slug])


@method_decorator(staff_member_required, name='dispatch')
class AdminDeleteQuestionView(DetailView):
    model = Question
    survey = None

    def dispatch(self, request, *args, **kwargs):
        question = self.get_object()
        self.survey = question.survey
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        question = self.get_object()
        question.delete()
        messages.success(request, gettext("Question %ss succesfully deleted.") % question.label)
        return redirect("djf_surveys:admin_forms_survey", slug=self.survey.slug)


@method_decorator(staff_member_required, name='dispatch')
class AdminChangeOrderQuestionView(View):
    def post(self, request, *args, **kwargs):
        ordering = request.POST['order_question'].split(",")
        for index, question_id in enumerate(ordering):
            if question_id:
                question = Question.objects.get(id=question_id)
                question.ordering = index
                question.save()

        data = {
            'message': gettext("Update ordering of questions succeeded.")
        }
        return JsonResponse(data, status=200)


@method_decorator(staff_member_required, name='dispatch')
class DownloadResponseSurveyView(DetailView):
    model = Survey

    def get(self, request, *args, **kwargs):
        survey = self.get_object()
        user_answers = UserAnswer.objects.filter(survey=survey)
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)

        rows = []
        header = []
        for index, user_answer in enumerate(user_answers):
            if index == 0:
                header.append('foydalanuvchi')
                header.append('yuborilgan vaqti')
                header.append('kurs nomi')

            rows.append(user_answer.user.username if user_answer.user else 'ro‘yxatdan o‘tmagan')
            rows.append(user_answer.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
            rows.append(user_answer.direction.name if user_answer.direction else 'yo‘nalish tanlanmagan')

            for answer in user_answer.answer_set.all():
                if index == 0:
                    header.append(answer.question.label)
                rows.append(answer.get_value_for_csv)

            if index == 0:
                writer.writerow(header)
            writer.writerow(rows)
            rows = []

        response = HttpResponse(csv_buffer.getvalue(), content_type="text/csv")
        response['Content-Disposition'] = f'attachment; filename={survey.slug}.csv'
        return response


@method_decorator(staff_member_required, name='dispatch')
class SummaryResponseSurveyView(ContextTitleMixin, DetailView):
    model = Survey
    template_name = "djf_surveys/admins/summary.html"
    title_page = _("Natija")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_year = now().year
        selected_year = self.request.GET.get('year', None)
        try:
            selected_year = int(selected_year) if selected_year else None
        except ValueError:
            selected_year = None

        selected_month = self.request.GET.get('month', None)
        if selected_month and selected_month.isdigit():
            selected_month = int(selected_month)
        else:
            selected_month = None

        selected_direction_id = self.request.GET.get('direction')
        print(f"Request GET parameters: {self.request.GET}")
        # Convert to integers
        if selected_direction_id == '':
            print("Direction ID is None. It may not be provided in the request.")
        else:
            print(f"Direction ID: {selected_direction_id}")

        selected_direction = None
        if selected_direction_id:
            try:
                selected_direction = Direction.objects.get(id=selected_direction_id)
            except Direction.DoesNotExist:
                selected_direction = None
        else:
            selected_direction = None

        directions = Direction.objects.all()

        answer_queryset = Answer.objects.all()

        if selected_year:
            answer_queryset = answer_queryset.filter(created_at__year=selected_year)

        if selected_month:
            answer_queryset = answer_queryset.filter(created_at__month=selected_month)

        if selected_direction:
            answer_queryset = answer_queryset.filter(user_answer__direction=selected_direction)

        survey = self.get_object()
        summary = SummaryResponse(survey=survey,
                                  selected_year=selected_year if selected_year else None,
                                  selected_month=selected_month if selected_month else None,
                                  selected_direction=selected_direction if selected_direction else None)

        # Generate year and month ranges for the form
        years = range(2023, current_year + 1)
        months = [
            {'value': 1, 'name': 'Yanvar'},
            {'value': 2, 'name': 'Fevral'},
            {'value': 3, 'name': 'Mart'},
            {'value': 4, 'name': 'Aprel'},
            {'value': 5, 'name': 'May'},
            {'value': 6, 'name': 'Iyun'},
            {'value': 7, 'name': 'Iyul'},
            {'value': 8, 'name': 'Avgust'},
            {'value': 9, 'name': 'Sentabr'},
            {'value': 10, 'name': 'Oktabr'},
            {'value': 11, 'name': 'Noyabr'},
            {'value': 12, 'name': 'Dekabr'}
        ]

        context.update({
            'summary': summary,
            'years': years,
            'selected_year': selected_year,
            'months': months,
            'selected_month': selected_month,
            'directions': directions,
            'selected_direction': selected_direction,
        })
        return context