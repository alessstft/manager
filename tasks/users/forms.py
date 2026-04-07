from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Profile

_CONTROL = {'class': 'form-control'}
_CONTROL_FILE = {'class': 'form-control'}


class FirstAdminRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='Имя', max_length=150, required=True)
    last_name = forms.CharField(label='Фамилия', max_length=150, required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]
        widgets = {
            'username': forms.TextInput(attrs=_CONTROL),
            'first_name': forms.TextInput(attrs=_CONTROL),
            'last_name': forms.TextInput(attrs=_CONTROL),
            'email': forms.EmailInput(attrs=_CONTROL),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update(_CONTROL)
        self.fields['password2'].widget.attrs.update(_CONTROL)


class AdminCreateEmployeeForm(UserCreationForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(label='Имя', max_length=150, required=True)
    last_name = forms.CharField(label='Фамилия', max_length=150, required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]
        widgets = {
            'username': forms.TextInput(attrs=_CONTROL),
            'first_name': forms.TextInput(attrs=_CONTROL),
            'last_name': forms.TextInput(attrs=_CONTROL),
            'email': forms.EmailInput(attrs=_CONTROL),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update(_CONTROL)
        self.fields['password2'].widget.attrs.update(_CONTROL)


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs=_CONTROL),
            'last_name': forms.TextInput(attrs=_CONTROL),
            'email': forms.EmailInput(attrs=_CONTROL),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
        widgets = {'image': forms.FileInput(attrs=_CONTROL_FILE)}
