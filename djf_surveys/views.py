from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, reverse
from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _
from django.views.generic.list import ListView
from django.views.generic.edit import FormMixin
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from accounts.models import Profile
from djf_surveys.models import Survey, UserAnswer, UserAnswer2, Question, Question2, TYPE_FIELD, Answer2, UserRating
from djf_surveys.forms import CreateSurveyForm, EditSurveyForm
from djf_surveys.mixin import ContextTitleMixin
from djf_surveys import app_settings
from djf_surveys.utils import NewPaginator
from django.core.exceptions import ObjectDoesNotExist


class SurveyListView(ContextTitleMixin, UserPassesTestMixin, ListView):
    model = Survey
    title_page = "So‘rovnomalar ro‘yxati"
    paginate_by = app_settings.SURVEY_PAGINATION_NUMBER['survey_list']
    paginator_class = NewPaginator

    def test_func(self):
        return app_settings.SURVEY_ANONYMOUS_VIEW_LIST or self.request.user.is_authenticated

    def get_queryset(self):
        filter = {}
        if app_settings.SURVEY_ANONYMOUS_VIEW_LIST and not self.request.user.is_authenticated:
            filter["can_anonymous_user"] = True
        query = self.request.GET.get('q')
        if query:
            object_list = self.model.objects.filter(name__icontains=query, **filter)
        else:
            object_list = self.model.objects.filter(**filter)
        return object_list

    def get_context_data(self, **kwargs):
        page_number = self.request.GET.get('page', 1)
        context = super().get_context_data(**kwargs)
        page_range = context['page_obj'].paginator.get_elided_page_range(number=page_number)
        context['page_range'] = page_range
        return context


class SurveyFormView(FormMixin, DetailView):
    template_name = 'djf_surveys/form.html'
    success_url = reverse_lazy("djf_surveys:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['eligible_users'] = Profile.objects.filter(
            positions__slug__in=['boshligi', 'professori', 'dotsenti', 'katta-oqituvchisi', 'oqituvchisi', 'kabinet-boshligi'],
            can_be_rated=True
        ).distinct()

        context['questions2'] = Question2.objects.filter(survey=self.object)  # Add Question2 to context
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        if 'create' in request.path:
            questions = Question.objects.filter(survey=self.object)
            for param in request.GET.keys():  # loop over all GET parameters
                for question in questions:
                    if question.key == param:  # find corresponding question
                        field_key = f"field_survey_{question.id}"
                        if field_key in context["form"].field_names:
                            if question.type_field == TYPE_FIELD.rating:
                                if not question.choices:
                                    question.choices = 5
                                context["form"][field_key].field.initial = max(0, min(int(request.GET[param]),
                                                                                      int(question.choices) - 1))
                            elif question.type_field == TYPE_FIELD.multi_select:
                                context["form"][field_key].field.initial = request.GET[param].split(',')
                            else:
                                context["form"][field_key].field.initial = request.GET[param]
                        break

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Hozirgi so‘rovnoma obyekti
        form = self.get_form()

        if form.is_valid():
            try:
                # Save ma'lumotlar
                form.save()
                messages.success(request, "Javobingiz saqlandi!")
                return self.form_valid(form)
            except Exception as e:
                messages.error(request, f"Saqlashda xatolik yuz berdi: {str(e)}")
                return self.form_invalid(form)
        else:
            messages.error(request, "Formani to‘ldirishda xatolik")
            return self.form_invalid(form)

    def get_form(self, form_class=None):
        form_class = form_class or self.get_form_class()
        return form_class(survey=self.get_object(), user=self.request.user, **self.get_form_kwargs())


class CreateSurveyFormView(ContextTitleMixin, SurveyFormView):
    model = Survey
    form_class = CreateSurveyForm
    title_page = _("So'rovnoma to'ldirish")

    def dispatch(self, request, *args, **kwargs):
        survey = self.get_object()
        if not request.user.is_authenticated and not survey.can_anonymous_user:
            messages.warning(request, gettext("Kechirasiz, so'rovnomani to'ldirish uchun tizimga kirgan bo'lishingiz kerak."))
            return redirect("djf_surveys:index")

        # handle if user have answer survey
        if request.user.is_authenticated and not survey.duplicate_entry and \
                UserAnswer.objects.filter(survey=survey, user=request.user).exists():
            messages.warning(request, gettext("Siz ushbu so'rovnomani topshirdingiz."))
            return redirect("djf_surveys:index")
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form_class = form_class or self.get_form_class()
        return form_class(survey=self.get_object(), user=self.request.user, **self.get_form_kwargs())

    def get_title_page(self):
        return self.get_object().name

    def get_sub_title_page(self):
        return self.get_object().description

    def get_success_url(self):
        return reverse("djf_surveys:success", kwargs={"slug": self.get_object().slug})


@method_decorator(login_required, name='dispatch')
class EditSurveyFormView(ContextTitleMixin, SurveyFormView):
    form_class = EditSurveyForm
    title_page = "So‘rovnomani tahrirlash"
    model = UserAnswer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object().survey
        return context

    def dispatch(self, request, *args, **kwargs):
        # handle if user not same
        user_answer = self.get_object()
        if user_answer.user != request.user or not user_answer.survey.editable:
            messages.warning(request, gettext("Siz bu soʻrovnomani tahrirlay olmaysiz. Sizda ruxsat yo‘q."))
            return redirect("djf_surveys:index")
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        user_answer = self.get_object()
        return form_class(user_answer=user_answer, **self.get_form_kwargs())

    def get_title_page(self):
        return self.get_object().survey.name

    def get_sub_title_page(self):
        return self.get_object().survey.description


@method_decorator(login_required, name='dispatch')
class DeleteSurveyAnswerView(DetailView):
    model = UserAnswer

    def dispatch(self, request, *args, **kwargs):
        # handle if user not same
        user_answer = self.get_object()
        if user_answer.user != request.user or not user_answer.survey.deletable:
            messages.warning(request, gettext("Bu soʻrovnomani oʻchira olmaysiz. Sizda ruxsat yo‘q."))
            return redirect("djf_surveys:index")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user_answer = self.get_object()
        user_answer.delete()
        messages.success(self.request, gettext("Javob muvaffaqiyatli oʻchirildi."))
        return redirect("djf_surveys:detail", slug=user_answer.survey.slug)


class DetailSurveyView(ContextTitleMixin, DetailView):
    model = Survey
    template_name = "djf_surveys/answer_list.html"
    title_page = _("So'rovnoma tafsilotlari")
    paginate_by = app_settings.SURVEY_PAGINATION_NUMBER['answer_list']

    def dispatch(self, request, *args, **kwargs):
        survey = self.get_object()
        if not self.request.user.is_superuser and survey.private_response:
            messages.warning(request, gettext("Siz bu sahifaga kira olmaysiz. Sizda ruxsat yo‘q."))
            return redirect("djf_surveys:index")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user_answers = UserAnswer.objects.filter(survey=self.get_object()) \
            .select_related('user').prefetch_related('answer_set__question')
        paginator = NewPaginator(user_answers, self.paginate_by)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(number=page_number)
        context = super().get_context_data(**kwargs)
        context['page_obj'] = page_obj
        context['page_range'] = page_range
        return context


@method_decorator(login_required, name='dispatch')
class DetailResultSurveyView(ContextTitleMixin, DetailView):
    title_page = _("So‘rovnoma natijalari")
    template_name = "djf_surveys/detail_result.html"
    model = UserAnswer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        context['on_detail'] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        # handle if user not same
        user_answer = self.get_object()
        if user_answer.user != request.user:
            messages.warning(request, gettext("Siz bu sahifaga kira olmaysiz. Sizda ruxsat yo‘q."))
            return redirect("djf_surveys:index")
        return super().dispatch(request, *args, **kwargs)

    def get_title_page(self):
        return self.get_object().survey.name

    def get_sub_title_page(self):
        return self.get_object().survey.description


def share_link(request, slug):
    # this func to handle link redirect to create form or edit form
    survey = get_object_or_404(Survey, slug=slug)
    if request.user.is_authenticated:
        user_answer = UserAnswer.objects.filter(survey=survey, user=request.user).last()
        if user_answer:
            return redirect(reverse_lazy("djf_surveys:edit", kwargs={'pk': user_answer.id}))
    return redirect(reverse_lazy("djf_surveys:create", kwargs={'slug': survey.slug}))


class SuccessPageSurveyView(ContextTitleMixin, DetailView):
    model = Survey
    template_name = "djf_surveys/success-page.html"
    title_page = _("Muvaffaqiyatli yuborildi!")
