from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import DeleteView
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, UserLoginForm
from django.contrib.auth.models import User
from .models import Profile, Department, Position, Rank


class CustomLoginView(LoginView):
    form_class = UserLoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class CustomLogoutView(LogoutView):
    """This view renders our logout page."""
    template_name = 'accounts/logout.html'

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            # Perform any additional logic needed for GET request
            return super().get(request, *args, **kwargs)
        elif request.method == 'POST':
            # Perform any additional logic needed for POST request
            return super().post(request, *args, **kwargs)


class RegisterView(View):
    form_class = UserRegisterForm
    initial = {'key': 'value'}
    template_name = 'accounts/register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'{username} nomli akkaunt yaratildi')

            return redirect(to='/')

        return render(request, self.template_name, {'form': form})

    def dispatch(self, request, *args, **kwargs):
        # Agar user login bo'lmagan bo'lsa yoki staff bo'lmasa, ruxsat yo'q
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect(to='/')
        return super(RegisterView, self).dispatch(request, *args, **kwargs)


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Profil muvaffaqiyatli yangilandi!')
            return redirect('accounts:profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    if request.user.is_superuser:
        # Render a different template for superusers
        return render(request, 'accounts/superuser_profile.html', context)
    else:
        # Render the regular profile template for other users
        return render(request, 'accounts/profile.html', context)


class UsersListView(View):
    template_name = 'accounts/users_list.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        users_qs = User.objects.select_related('profile').all()

        # Filtrlash parametrlari
        department_id = request.GET.get('department')
        position_id = request.GET.get('position')
        rank_id = request.GET.get('rank')
        gender = request.GET.get('gender')

        # Agar department_id bo‘lsa, shunga mos userlarni filtrlaymiz
        if department_id:
            users_qs = users_qs.filter(profile__department_id=department_id)

        if position_id:
            users_qs = users_qs.filter(profile__position_id=position_id)

        if rank_id:
            users_qs = users_qs.filter(profile__rank_id=rank_id)

        if gender:
            users_qs = users_qs.filter(profile__gender=gender)

        # Department nomi bo‘yicha alfavit tartibida saralash
        users_qs = users_qs.order_by('profile__department__name', 'last_name', 'first_name')

        # Filtr dropdownlarini to‘ldirish uchun
        departments = Department.objects.all()
        positions = Position.objects.all()
        ranks = Rank.objects.all()

        context = {
            'users_list': users_qs,
            'departments': departments,
            'positions': positions,
            'ranks': ranks,
            'selected_department': department_id,
            'selected_position': position_id,
            'selected_rank': rank_id,
            'selected_gender': gender
        }
        return render(request, self.template_name, context)


@login_required
def edit_profile(request, pk):
    """Admin (yoki ruxsati bor user) tomonidan boshqa foydalanuvchini tahrirlash"""
    user_obj = get_object_or_404(User, pk=pk)  # user_id bo‘yicha User ni topamiz
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user_obj)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_obj.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Foydalanuvchi profili yangilandi!')
            return redirect('accounts:users_list')
    else:
        u_form = UserUpdateForm(instance=user_obj)
        p_form = ProfileUpdateForm(instance=user_obj.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'edit_user': user_obj
    }
    return render(request, 'accounts/profile.html', context)


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "accounts/delete.html"
    success_url = reverse_lazy("accounts:users_list")


