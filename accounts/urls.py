from django.urls import path
from .forms import UserLoginForm
from .views import profile, CustomLoginView, RegisterView, CustomLogoutView, \
    load_positions


app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(template_name='accounts/login.html',
                                           authentication_form=UserLoginForm), name='login'),
    path('logout/', CustomLogoutView.as_view(next_page='/'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', profile, name='profile'),
    path('profile/update/', profile, name='profile_update'),
    path('ajax/load-positions/', load_positions, name='ajax_load_positions'),
]
