from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile, Position, Department


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control',
                                                             }))
    password = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'form-control',
                                                                 'data-toggle': 'password',
                                                                 'id': 'password',
                                                                 'name': 'password',
                                                                 }))
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me']


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50,
                                 required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Optional: Use a suitable widget
        required=False
    )
    positions = forms.ModelMultipleChoiceField(
        queryset=Position.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Optional: Use a suitable widget
        required=False
    )

    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    phone_number = forms.RegexField(
        regex=r'^\+?1?\d{9,15}$',
        error_messages={
            'invalid': "Telefon raqami quyidagi formatda kiritilishi kerak: +998901234567"
        }
    )
    birthday = forms.DateField(
        label="Tug'ilgan kuni",
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )

    class Meta:
        model = Profile
        fields = ['departments', 'positions', 'rank', 'gender', 'birthday', 'phone_number', 'image', 'can_be_rated']

