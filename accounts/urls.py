from django.urls import path
from .views import (profile, CustomLoginView, RegisterView,
                    CustomLogoutView, UsersListView, edit_profile, UserDeleteView)
from .forms import UserLoginForm

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(template_name='accounts/login.html',
                                           authentication_form=UserLoginForm),
         name='login'),
    path('logout/', CustomLogoutView.as_view(next_page='/'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    # Hozirgi "shaxsiy" profil
    path('profile/', profile, name='profile'),

    # Barcha userlarning ro'yxati
    path('users_list/', UsersListView.as_view(), name='users_list'),

    # Tahrirlash — <user_id> bilan
    path('profile/<int:pk>/', edit_profile, name='edit_profile'),

    # O'chirish
    path('delete_user/<int:pk>/', UserDeleteView.as_view(), name='delete_user'),
]