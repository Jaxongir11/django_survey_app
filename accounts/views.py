from datetime import datetime
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, UserLoginForm
from .models import Profile, Position


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
            messages.success(request, f'Account created for {username}')

            return redirect(to='/')

        return render(request, self.template_name, {'form': form})

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
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
            messages.success(request, f'Akkaunt yangilandi!')
            return redirect('accounts:profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        profile_instance = get_object_or_404(Profile, user=request.user)
        p_form = ProfileUpdateForm(instance=profile_instance)

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


def load_positions(request):
    department_id = request.GET.get('department')
    positions = Position.objects.filter(department_id=department_id).order_by('name')
    return render(request, 'accounts/positions_dropdown_list.html', {'positions': positions})
