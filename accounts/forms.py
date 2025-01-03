from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile, Position, Department, Rank, GENDER_CHOICES


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Login',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm' 
                         ' focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }
        )
    )
    password = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Parol',
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm' 
                         ' focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }
        )
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            }
        )
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me']


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none'
                         ' focus:ring-blue-500 focus:border-blue-500'
            }
        )
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none'
                         ' focus:ring-blue-500 focus:border-blue-500'
            }
        )
    )
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none'
                         ' focus:ring-blue-500 focus:border-blue-500'
            }
        )
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none'
                         ' focus:ring-blue-500 focus:border-blue-500'
            }
        )
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm'
                         ' focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }
        )
    )
    position = forms.ModelChoiceField(
        queryset=Position.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm'
                         ' focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }
        )
    )

    rank = forms.ModelChoiceField(
        queryset=Rank.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm'
                         ' focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }
        )
    )
    # GENDER uchun ChoiceField (modelda GENDER_CHOICES bor)
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm'
                         ' focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }
        )
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer'
                         ' bg-gray-50 focus:outline-none'
            }
        )
    )

    class Meta:
        model = Profile
        fields = ['department', 'position', 'rank', 'gender', 'image', 'can_be_rated']