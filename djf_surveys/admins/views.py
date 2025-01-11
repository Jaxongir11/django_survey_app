import csv
from io import StringIO

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _
from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db.models import Avg

from accounts.models import Profile
from djf_surveys.app_settings import SURVEYS_ADMIN_BASE_PATH
from djf_surveys.models import Survey, Question, UserAnswer, Answer, Direction, Question2, UserRating, Answer2
from djf_surveys.mixin import ContextTitleMixin
from djf_surveys.views import SurveyListView
from djf_surveys.forms import BaseSurveyForm
from djf_surveys.summary import SummaryResponse
from djf_surveys.admins.v2.forms import SurveyForm


@method_decorator(staff_member_required, name='dispatch')
class AdminCrateSurveyView(ContextTitleMixin, CreateView):
    template_name = 'djf_surveys/admins/form.html'
    form_class = SurveyForm
    title_page = _("Yangi so‘rovnoma qo‘shish")

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
    title_page = _("So‘rovnomani tahrirlash")

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Existing context data...

        # Add eligible_users to context
        context['eligible_users'] = Profile.objects.filter(
            position__slug__in=[
                'boshligi', 'boshligi-orinbosari', 'professori', 'dotsenti',
                'katta-oqituvchisi', 'oqituvchisi', 'kabinet-boshligi'
            ]
        ).distinct()
        return context

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(survey=self.object, user=self.request.user, **self.get_form_kwargs())

    def get_title_page(self):
        return self.object.name

    def get_sub_title_page(self):
        return self.object.description

    def dispatch(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            return self.handle_ajax_request(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def handle_ajax_request(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        can_be_rated = request.POST.get('can_be_rated') == 'true'

        try:
            profile = Profile.objects.get(id=user_id)
            profile.can_be_rated = can_be_rated
            profile.save()
            return JsonResponse({'status': 'success', 'can_be_rated': profile.can_be_rated})
        except Profile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Foydalanuvchi topilmadi.'}, status=404)


@method_decorator(staff_member_required, name='dispatch')
class AdminDeleteSurveyView(DetailView):
    model = Survey

    def get(self, request, *args, **kwargs):
        survey = self.get_object()
        survey.delete()
        messages.success(request, gettext("So‘rovnoma %ss muvaffaqiyatli o‘chirildi.") % survey.name)
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
    title_page = _("Savol qo‘shish")
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
            messages.success(self.request, gettext("%(page_action_name)s bajarildi.") % dict(page_action_name=capfirst(self.title_page.lower())))
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
    title_page = _("Savol qo‘shish")
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
        messages.success(request, gettext("Savol %ss muvaffaqiyatli o‘chirildi.") % question.label)
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
        survey = self.get_object()

        current_year = now().year
        selected_year = self.request.GET.get('year', None)
        try:
            selected_year = int(selected_year) if selected_year else current_year
        except ValueError:
            selected_year = None

        selected_month = self.request.GET.get('month', None)
        if selected_month and selected_month.isdigit():
            selected_month = int(selected_month)
        else:
            selected_month = None

        selected_direction_id = self.request.GET.get('direction')

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

        rated_users = (
            UserRating.objects
                .filter(user_answer__survey=survey)  # ayni shu survey'ga tegishli reytinglar
                .values(
                "rated_user__first_name",
                "rated_user__last_name",
            )
                .annotate(avg_rating=Avg("answer2__value"))  # O'rtacha reyting
                .order_by("-avg_rating")  # Eng balanddan eng pastga
        )

        summary = SummaryResponse(survey=survey,
                                  selected_year=selected_year if selected_year else None,
                                  selected_month=selected_month if selected_month else None,
                                  selected_direction=selected_direction if selected_direction else None)

        # Generate year and month ranges for the form
        years = range(2024, current_year + 1)
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
            'rated_users': rated_users,
        })
        return context


class DirectionsListView(View):
    template_name = "djf_surveys/admins/directions.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        directions_qs = Direction.objects.all().order_by('name')

        context = {
            'directions_qs': directions_qs,
        }
        return render(request, self.template_name, context)


class DirectionUpdateView(UpdateView):
    model = Direction
    fields = ["name"]
    template_name = "djf_surveys/admins/direction_update.html"
    success_url = reverse_lazy("djf_surveys:directions")


class DirectionDeleteView(LoginRequiredMixin, DeleteView):
    model = Direction
    template_name = "djf_surveys/admins/direction_delete.html"
    success_url = reverse_lazy("djf_surveys:directions")


class DirectionAddView(LoginRequiredMixin, CreateView):
    model = Direction
    fields = ["name"]
    template_name = "djf_surveys/admins/add_direction.html"
    success_url = reverse_lazy("djf_surveys:directions")